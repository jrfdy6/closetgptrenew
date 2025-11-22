"""
Payment routes for Easy Outfit App.
Handles Stripe payment processing and subscription management.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging
import os

from ..auth.auth_service import get_current_user_id
from ..config.firebase import db, firestore
from ..services.subscription_utils import (
    DEFAULT_SUBSCRIPTION_TIER as DEFAULT_ROLE,
    TIER_LIMITS as ROLE_LIMITS,
    WEEKLY_ALLOWANCE_SECONDS,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payments"])
security = HTTPBearer()

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
}

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://easyoutfitapp.com")


# Request/Response Models
class SubscriptionUpgradeRequest(BaseModel):
    role: str  # "tier2" or "tier3"


class SubscriptionResponse(BaseModel):
    role: str
    status: str
    flatlays_remaining: int


@router.get("/subscription/current")
async def get_current_subscription(
    user_id: str = Depends(get_current_user_id)
) -> SubscriptionResponse:
    """Get current user subscription details"""
    try:
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict() or {}
        
        # Support both old and new schema
        subscription = user_data.get('subscription', {})
        role = subscription.get('role') or subscription.get('tier', DEFAULT_ROLE)
        status = subscription.get('status', 'active')
        
        # Get quotas (new schema) or calculate from old schema
        quotas = user_data.get('quotas', {})
        if quotas:
            flatlays_remaining = quotas.get('flatlaysRemaining', 0)
        else:
            # Fallback to old schema calculation
            limit = ROLE_LIMITS.get(role, 1)
            used = subscription.get('openai_flatlays_used', 0) or 0
            flatlays_remaining = max(0, limit - used)
        
        return SubscriptionResponse(
            role=role,
            status=status,
            flatlays_remaining=flatlays_remaining
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
    if role not in STRIPE_PRICE_IDS or role == "tier1" or not STRIPE_PRICE_IDS[role]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid role or role does not require payment"
        )
    
    try:
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict() or {}
        email = user_data.get('email')
        billing = user_data.get('billing', {})
        existing_customer_id = billing.get('stripeCustomerId')
        
        # Create or retrieve Stripe customer
        if existing_customer_id:
            try:
                customer = stripe.Customer.retrieve(existing_customer_id)
            except stripe.error.StripeError:
                customer = None
        else:
            customer = None
        
        if not customer:
            customer = stripe.Customer.create(
                email=email,
                metadata={'user_id': user_id}
            )
            db.collection('users').document(user_id).update({
                'billing.stripeCustomerId': customer.id
            })
        
        price_id = STRIPE_PRICE_IDS[role]
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{FRONTEND_URL}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/subscription",
            metadata={
                'user_id': user_id,
                'role': role,
            },
            allow_promotion_codes=True,
        )
        
        logger.info(f"Created checkout session {checkout_session.id} for user {user_id}")
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    
    except HTTPException:
        raise
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
        billing = user_data.get('billing', {})
        customer_id = billing.get('stripeCustomerId')
        
        if not customer_id:
            raise HTTPException(
                status_code=400, 
                detail="No Stripe customer found. Please subscribe first."
            )
        
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{FRONTEND_URL}/subscription",
        )
        
        logger.info(f"Created portal session for user {user_id}")
        
        return {
            "url": portal_session.url
        }
    
    except HTTPException:
        raise
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
    
    event_type = event['type']
    logger.info(f"Processing Stripe webhook event: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            await handle_checkout_completed(session)
        elif event_type == 'customer.subscription.created':
            subscription = event['data']['object']
            await handle_subscription_created(subscription)
        elif event_type == 'customer.subscription.updated':
            subscription = event['data']['object']
            await handle_subscription_updated(subscription)
        elif event_type == 'customer.subscription.deleted':
            subscription = event['data']['object']
            await handle_subscription_deleted(subscription)
        elif event_type == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            await handle_invoice_payment_succeeded(invoice)
        elif event_type == 'invoice.payment_failed':
            invoice = event['data']['object']
            await handle_invoice_payment_failed(invoice)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def handle_checkout_completed(session: Dict[str, Any]):
    """Handle successful checkout completion"""
    metadata = session.get('metadata', {})
    user_id = metadata.get('user_id')
    role = metadata.get('role', 'tier2')
    
    if not user_id:
        logger.error(f"Missing user_id in checkout session: {session.get('id')}")
        return
    
    user_ref = db.collection('users').document(user_id)
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    
    now = datetime.now(timezone.utc)
    now_timestamp = int(now.timestamp())
    
    # Get flat lay limit for role
    flatlay_limit = ROLE_LIMITS.get(role, 1)
    period_end = now_timestamp + (30 * 24 * 60 * 60)  # 30 days
    
    updates = {
        'billing.stripeCustomerId': customer_id,
        'subscription.status': 'active',
        'subscription.role': role,
        'subscription.currentPeriodEnd': period_end,
        'subscription.priceId': STRIPE_PRICE_IDS.get(role, 'free'),
        'quotas.flatlaysRemaining': flatlay_limit,
        'quotas.lastRefillAt': now_timestamp,
    }
    
    if subscription_id:
        updates['subscription.stripeSubscriptionId'] = subscription_id
    
    user_ref.update(updates)
    logger.info(f"Updated user {user_id} subscription to {role}")


async def handle_subscription_updated(subscription: Dict[str, Any]):
    """Handle subscription updates"""
    customer_id = subscription.get('customer')
    subscription_id = subscription.get('id')
    
    users_ref = db.collection('users')
    query = users_ref.where('billing.stripeCustomerId', '==', customer_id).limit(1)
    docs = list(query.stream())
    
    if not docs:
        logger.warning(f"No user found for customer {customer_id}")
        return
    
    # Determine role from price ID (simplified - you'd map price IDs to roles)
    role = 'tier2'  # Default, should be determined from subscription items
    period_end = subscription.get('current_period_end', 0)
    status = subscription.get('status', 'active')
    
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    doc = docs[0]
    doc.reference.update({
        'subscription.role': role,
        'subscription.status': status,
        'subscription.currentPeriodEnd': period_end,
        'subscription.last_updated': firestore.SERVER_TIMESTAMP,
    })
    logger.info(f"Updated subscription {subscription_id} for user {doc.id}")


async def handle_subscription_created(subscription: Dict[str, Any]):
    """Handle new subscription creation"""
    customer_id = subscription.get('customer')
    subscription_id = subscription.get('id')
    
    users_ref = db.collection('users')
    query = users_ref.where('billing.stripeCustomerId', '==', customer_id).limit(1)
    docs = list(query.stream())
    
    if not docs:
        logger.warning(f"No user found for customer {customer_id}")
        return
    
    # Determine role from subscription items
    items = subscription.get('items', {}).get('data', [])
    role = 'tier2'  # Default
    if items:
        price_id = items[0].get('price', {}).get('id', '')
        if price_id == STRIPE_PRICE_IDS.get('tier3'):
            role = 'tier3'
        elif price_id == STRIPE_PRICE_IDS.get('tier2'):
            role = 'tier2'
    
    period_end = subscription.get('current_period_end', 0)
    status = subscription.get('status', 'active')
    flatlay_limit = ROLE_LIMITS.get(role, 1)
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    doc = docs[0]
    doc.reference.update({
        'subscription.role': role,
        'subscription.status': status,
        'subscription.stripeSubscriptionId': subscription_id,
        'subscription.currentPeriodEnd': period_end,
        'quotas.flatlaysRemaining': flatlay_limit,
        'quotas.lastRefillAt': now_timestamp,
    })
    logger.info(f"Created subscription {subscription_id} for user {doc.id}, role: {role}")


async def handle_subscription_deleted(subscription: Dict[str, Any]):
    """Handle subscription cancellation - downgrade to tier1"""
    customer_id = subscription.get('customer')
    
    users_ref = db.collection('users')
    query = users_ref.where('billing.stripeCustomerId', '==', customer_id).limit(1)
    docs = list(query.stream())
    
    if not docs:
        logger.warning(f"No user found for customer {customer_id}")
        return
    
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    next_period_end = now_timestamp + WEEKLY_ALLOWANCE_SECONDS
    flatlay_limit = ROLE_LIMITS.get(DEFAULT_ROLE, 1)
    
    doc = docs[0]
    doc.reference.update({
        'subscription.role': DEFAULT_ROLE,
        'subscription.status': 'canceled',
        'subscription.currentPeriodEnd': next_period_end,
        'subscription.priceId': 'free',
        'quotas.flatlaysRemaining': flatlay_limit,
        'quotas.lastRefillAt': now_timestamp,
    })
    logger.info(f"Canceled subscription for user {doc.id}, downgraded to {DEFAULT_ROLE}")


async def handle_invoice_payment_succeeded(invoice: Dict[str, Any]):
    """Handle successful invoice payment - refill quotas"""
    customer_id = invoice.get('customer')
    subscription_id = invoice.get('subscription')
    
    if not subscription_id:
        logger.info(f"Invoice {invoice.get('id')} has no subscription, skipping")
        return
    
    users_ref = db.collection('users')
    query = users_ref.where('billing.stripeCustomerId', '==', customer_id).limit(1)
    docs = list(query.stream())
    
    if not docs:
        logger.warning(f"No user found for customer {customer_id}")
        return
    
    doc = docs[0]
    user_data = doc.to_dict() or {}
    subscription = user_data.get('subscription', {})
    current_role = subscription.get('role', DEFAULT_ROLE)
    
    # Refill quotas based on current role
    flatlay_limit = ROLE_LIMITS.get(current_role, 1)
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    doc.reference.update({
        'subscription.status': 'active',
        'quotas.flatlaysRemaining': flatlay_limit,
        'quotas.lastRefillAt': now_timestamp,
    })
    logger.info(f"Refilled quotas for user {doc.id} after successful payment")


async def handle_invoice_payment_failed(invoice: Dict[str, Any]):
    """Handle failed invoice payment"""
    customer_id = invoice.get('customer')
    
    users_ref = db.collection('users')
    query = users_ref.where('billing.stripeCustomerId', '==', customer_id).limit(1)
    docs = list(query.stream())
    
    if not docs:
        logger.warning(f"No user found for customer {customer_id}")
        return
    
    doc = docs[0]
    doc.reference.update({
        'subscription.status': 'past_due',
    })
    logger.warning(f"Payment failed for user {doc.id}, subscription marked as past_due")


@router.post("/flatlay/consume")
async def consume_flatlay_quota(
    user_id: str = Depends(get_current_user_id)
):
    """Consume one flat lay credit when user requests a flat lay"""
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict() or {}
        subscription = user_data.get('subscription', {})
        role = subscription.get('role') or subscription.get('tier', DEFAULT_ROLE)
        quotas = user_data.get('quotas', {})
        
        # Get current remaining
        remaining = quotas.get('flatlaysRemaining', 0)
        try:
            remaining = int(remaining)
        except (TypeError, ValueError):
            remaining = 0
        
        # Check if quota needs weekly refill
        last_refill_at = quotas.get('lastRefillAt')
        now_timestamp = int(datetime.now(timezone.utc).timestamp())
        
        if last_refill_at:
            try:
                last_refill_timestamp = int(last_refill_at)
                seconds_since_refill = now_timestamp - last_refill_timestamp
                if seconds_since_refill >= WEEKLY_ALLOWANCE_SECONDS:
                    # Week has passed, refill quota
                    limit = ROLE_LIMITS.get(role, 1)
                    remaining = limit
            except (TypeError, ValueError):
                limit = ROLE_LIMITS.get(role, 1)
                remaining = limit
        else:
            # No refill timestamp, assume fresh start
            limit = ROLE_LIMITS.get(role, 1)
            remaining = limit
        
        # Check if user has credits
        if remaining <= 0:
            raise HTTPException(
                status_code=403,
                detail=f"No flat lay credits remaining. You have {remaining} of {ROLE_LIMITS.get(role, 1)} credits."
            )
        
        # Decrement quota
        new_remaining = max(0, remaining - 1)
        
        user_ref.update({
            'quotas.flatlaysRemaining': new_remaining,
            'quotas.lastRefillAt': now_timestamp,
        })
        
        logger.info(f"Consumed flat lay credit for user {user_id}: {remaining} -> {new_remaining}")
        
        return {
            "success": True,
            "remaining": new_remaining,
            "limit": ROLE_LIMITS.get(role, 1)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consuming flat lay quota: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

