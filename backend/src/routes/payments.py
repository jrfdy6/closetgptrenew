"""
Payment routes for Easy Outfit App.
Handles Stripe payment processing and subscription management.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging
import os

from ..auth.auth_service import get_current_user_id
from ..config.firebase import db
from ..services.subscription_utils import (
    DEFAULT_SUBSCRIPTION_TIER as DEFAULT_ROLE,
    current_quota, QuotaNeedsReview,
)
from ..services.subscription_feature_access import get_user_subscription_info
from ..services.subscription_read_repair import read_subscription_user
from ..services.account_bootstrap import ensure_user_account
from ..services.billing_portal import (
    BillingPortalConfigurationError, create_subscription_update_confirmation,
)
from ..services.billing_reconciliation import (
    BillingReconciliationError, bind_checkout_customer, reconcile_stripe_event,
    user_for_customer, verify_customer_identity, resolve_checkout_customer_id,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payments"])

# Initialize Stripe (optional - only if configured)
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_AVAILABLE = bool(stripe.api_key)
except ImportError:
    stripe = None
    STRIPE_AVAILABLE = False

# Stripe price IDs (create these in Stripe dashboard)
STRIPE_PRICE_IDS = {
    "tier1": None,  # Free tier - no payment
    "tier2": os.getenv("STRIPE_PRICE_TIER2", ""),
    "tier3": os.getenv("STRIPE_PRICE_TIER3", ""),
    "tier2_yearly": os.getenv("STRIPE_PRICE_TIER2_YEARLY", ""),
    "tier3_yearly": os.getenv("STRIPE_PRICE_TIER3_YEARLY", ""),
}

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://easyoutfitapp.com")


# Request/Response Models
class SubscriptionUpgradeRequest(BaseModel):
    role: str  # "tier2" or "tier3"
    interval: str = "month"  # "month" or "year"


class SubscriptionResponse(BaseModel):
    role: str
    status: str
    flatlays_remaining: int
    trial_end: Optional[int] = None
    is_trialing: bool = False
    days_remaining_in_trial: Optional[int] = None
    trial_used: bool = False
    quota_review_required: bool = False


@router.get("/subscription/current")
async def get_current_subscription(
    user_id: str = Depends(get_current_user_id)
) -> SubscriptionResponse:
    """Read subscription state without repairing uncertain accounts or granting credit."""
    try:
        user_data = read_subscription_user(db, user_id)
        if user_data is None:
            user_data = ensure_user_account(db, user_id)
        
        # Support both old and new schema
        raw_subscription = user_data.get('subscription')
        subscription = raw_subscription if isinstance(raw_subscription, dict) else {}
        role = subscription.get('role') or subscription.get('tier', DEFAULT_ROLE)
        status = subscription.get('status', 'active')
        
        # Preview the same lazy weekly allowance the reservation transaction
        # will use, without persisting a grant on a read or reconstructing an
        # unknown historical balance from a tier label.
        quota_review_required = False
        try:
            flatlays_remaining = current_quota(user_data, int(datetime.now(timezone.utc).timestamp()))['flatlaysRemaining']
        except QuotaNeedsReview:
            flatlays_remaining = 0
            quota_review_required = True

        # Get trial information
        trial_end = subscription.get('trialEnd')
        if isinstance(trial_end, bool) or not isinstance(trial_end, (int, type(None))):
            trial_end = None
        trial_used = subscription.get('trial_used', False)
        is_trialing = status == 'trialing'
        days_remaining_in_trial = None
        
        if trial_end and is_trialing:
            now_timestamp = int(datetime.now(timezone.utc).timestamp())
            seconds_remaining = trial_end - now_timestamp
            if seconds_remaining > 0:
                days_remaining_in_trial = max(1, int(seconds_remaining / (24 * 60 * 60)))
            else:
                # Trial has ended
                is_trialing = False
        
        return SubscriptionResponse(
            role=role,
            status=status,
            flatlays_remaining=flatlays_remaining,
            trial_end=trial_end,
            is_trialing=is_trialing,
            days_remaining_in_trial=days_remaining_in_trial,
            trial_used=trial_used,
            quota_review_required=quota_review_required,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout/create-session")
async def create_checkout_session(
    request: SubscriptionUpgradeRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create Stripe checkout session for subscription upgrade"""
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Payment processing not configured"
        )
    
    role = request.role
    interval = request.interval or "month"
    
    if role not in ("tier2", "tier3") or interval not in ("month", "year"):
        raise HTTPException(status_code=400, detail="Invalid role or interval")

    # Determine the correct price ID based on role and interval
    if interval == "year":
        price_key = f"{role}_yearly"
    else:
        price_key = role
    
    if price_key not in STRIPE_PRICE_IDS or role == "tier1" or not STRIPE_PRICE_IDS[price_key]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid role, interval, or price not configured"
        )
    
    try:
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict() or {}
        email = user_data.get('email')
        existing_customer_id = resolve_checkout_customer_id(stripe, user_data)
        
        # Existing identity failures need review. Never silently replace a
        # customer and strand its active subscription or trial history.
        if existing_customer_id:
            customer = stripe.Customer.retrieve(existing_customer_id)
            if customer.get('deleted'):
                raise HTTPException(status_code=409, detail="Your billing account needs review. Please contact support.")
            declared_user = (customer.get('metadata') or {}).get('user_id')
            if declared_user and declared_user != user_id:
                raise HTTPException(status_code=409, detail="Your billing account needs review. Please contact support.")
        else:
            customer = stripe.Customer.create(
                email=email, metadata={'user_id': user_id},
                idempotency_key=f"easyoutfit-customer-{user_id}",
            )
        bind_checkout_customer(db, user_id, customer)

        price_id = STRIPE_PRICE_IDS[price_key]
        
        # Check if user has already used a free trial
        # Check both current subscription and subscription history
        subscription = user_data.get('subscription', {})
        has_used_trial = subscription.get('trial_used', False)
        
        # Failed history reads must fail checkout, not silently offer another
        # trial. Check every page so older trials cannot disappear behind limit10.
        history = stripe.Subscription.list(customer=customer.id, status='all', limit=100)
        current_subscriptions = []
        for prior in history.auto_paging_iter():
            if prior.get('status') not in ('canceled', 'incomplete_expired'):
                current_subscriptions.append(prior)
            has_used_trial = has_used_trial or bool(prior.get('trial_end'))
        if current_subscriptions:
            if len(current_subscriptions) != 1 or user_for_customer(db, customer.id) != user_id:
                raise HTTPException(status_code=409, detail="Your billing account needs review. Please contact support.")
            # Confirm the requested price on the existing subscription. A
            # generic portal can have upgrades disabled; never create another
            # subscription or quietly send the customer to a dead-end instead.
            portal = create_subscription_update_confirmation(
                stripe, customer.id, current_subscriptions[0].get('id'), price_id,
                STRIPE_PRICE_IDS, f"{FRONTEND_URL}/subscription",
            )
            return {'checkout_url': portal.url, 'session_id': portal.id}

        # Create checkout session with 30-day free trial (if not already used)
        checkout_params = {
            'customer': customer.id,
            'payment_method_types': ['card'],
            'line_items': [{
                'price': price_id,
                'quantity': 1,
            }],
            'mode': 'subscription',
            'success_url': f"{FRONTEND_URL}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}",
            'cancel_url': f"{FRONTEND_URL}/subscription",
            'metadata': {
                'user_id': user_id,
                'role': role,
                'interval': interval,
            },
            'allow_promotion_codes': True,
        }
        
        # Set up subscription data (trial for monthly, no trial for yearly)
        subscription_data = {}
        
        # Add 30-day free trial ONLY for monthly subscriptions if user hasn't used one
        # Rationale: Yearly subscriptions already have a discount and indicate committed users
        if not has_used_trial and interval == "month":
            subscription_data['trial_period_days'] = 30
            logger.info(f"Adding 30-day free trial to checkout for user {user_id} (monthly plan)")
        
        # Always add subscription_data to ensure proper billing cycle
        checkout_params['subscription_data'] = subscription_data
        
        checkout_session = stripe.checkout.Session.create(**checkout_params)
        
        logger.info(f"Created checkout session {checkout_session.id} for user {user_id}")
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    
    except HTTPException:
        raise
    except BillingPortalConfigurationError:
        logger.exception("Stripe portal plan changes are not configured")
        raise HTTPException(status_code=503, detail="Plan changes are temporarily unavailable. Please contact support or retry later.")
    except BillingReconciliationError:
        logger.exception("Billing account identity requires review")
        raise HTTPException(status_code=409, detail="Your billing account needs review. Please contact support.")
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout/create-portal-session")
async def create_portal_session(
    user_id: str = Depends(get_current_user_id)
):
    """Create Stripe customer portal session for subscription management"""
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Payment processing not configured"
        )
    
    try:
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict() or {}
        customer_id = resolve_checkout_customer_id(stripe, user_data)
        if not customer_id:
            raise HTTPException(
                status_code=400,
                detail="No Stripe customer found. Please subscribe first to access the Customer Portal."
            )
        customer = stripe.Customer.retrieve(customer_id)
        verify_customer_identity(db, user_id, customer)
        bind_checkout_customer(db, user_id, customer)
        declared_user = (customer.get('metadata') or {}).get('user_id')
        if customer.get('deleted') or (declared_user and declared_user != user_id):
            raise HTTPException(status_code=409, detail="Your billing account needs review. Please contact support.")
        # Require a unique trusted account association before exposing billing.
        if user_for_customer(db, customer_id) != user_id:
            raise HTTPException(status_code=409, detail="Your billing account needs review. Please contact support.")

        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"{FRONTEND_URL}/subscription",
            )
            
            logger.info(f"Created portal session for user {user_id}")
            
            return {
                "url": portal_session.url
            }
        except stripe.error.InvalidRequestError as e:
            if "No such customer" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail="Your billing account needs review. Please contact support.",
                )
            raise
    
    except HTTPException:
        raise
    except BillingReconciliationError:
        logger.exception("Billing account identity requires review")
        raise HTTPException(status_code=409, detail="Your billing account needs review. Please contact support.")
    except Exception as e:
        logger.error(f"Error creating portal session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks for subscription events"""
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Payment processing not configured"
        )
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=503, detail="Webhook secret not configured")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        logger.error("Invalid payload in webhook")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature in webhook")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    try:
        # Stripe I/O is blocking. Keep it out of the event loop and outside every
        # retryable Firestore transaction.
        return await run_in_threadpool(reconcile_stripe_event, db, stripe, event, STRIPE_PRICE_IDS)
    except BillingReconciliationError:
        logger.exception("Stripe event requires retry or account review", extra={"event_id": event.get('id')})
        raise HTTPException(status_code=503, detail="Subscription update is pending. Stripe may retry this event.")
    except Exception:
        logger.exception("Stripe event processing failed", extra={"event_id": event.get('id')})
        raise HTTPException(status_code=503, detail="Subscription update could not be completed. Please retry.")


@router.get("/usage/current")
async def get_current_usage(
    user_id: str = Depends(get_current_user_id)
):
    """Get current monthly usage for outfit generations and wardrobe items"""
    try:
        from ..services.usage_tracking_service import UsageTrackingService
        
        usage_service = UsageTrackingService()
        usage = await usage_service.get_monthly_usage(user_id)
        
        # Get limits for user's tier
        subscription_info = get_user_subscription_info(user_id)
        role = subscription_info.get("role", DEFAULT_ROLE)
        from ..services.usage_tracking_service import TIER_MONTHLY_LIMITS
        limits = TIER_MONTHLY_LIMITS.get(role, TIER_MONTHLY_LIMITS[DEFAULT_ROLE])
        
        return {
            "outfit_generations": {
                "current": usage.get("outfit_generations", 0),
                "limit": limits.get("outfit_generations"),
                "remaining": None if limits.get("outfit_generations") is None else max(0, limits.get("outfit_generations") - usage.get("outfit_generations", 0)),
            },
            "wardrobe_items": {
                "current": usage.get("wardrobe_items", 0),
                "limit": limits.get("wardrobe_items"),
                "remaining": None if limits.get("wardrobe_items") is None else max(0, limits.get("wardrobe_items") - usage.get("wardrobe_items", 0)),
            },
            "reset_date": usage.get("reset_date"),
            "reset_date_str": datetime.fromtimestamp(usage.get("reset_date", 0), tz=timezone.utc).strftime("%B %d, %Y") if usage.get("reset_date") and usage.get("reset_date") > 0 else None,
        }
    except Exception as e:
        logger.error(f"Error getting current usage: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flatlay/consume")
async def consume_flatlay_quota(user_id: str = Depends(get_current_user_id)):
    """Old clients must refresh instead of paying for an untracked job."""
    raise HTTPException(
        status_code=409,
        detail="Refresh the app and request the flat lay from your outfit. No credit was used.",
    )
