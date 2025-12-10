"""
Store API Routes (Scarcity & Revenue Loop)
Endpoints for processing in-app purchases of premium features.
NOTE: Tokens CANNOT be purchased - they are earned through gameplay only!
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List
import logging
import os
from datetime import datetime
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile

router = APIRouter(prefix="/store", tags=["store"])
logger = logging.getLogger(__name__)

# Store Configuration (Premium Battle Pass ONLY - NO TOKEN PURCHASES)
STORE_CATALOG = {
    "BP_PREMIUM_UNLOCK": {
        "type": "PREMIUM_BP",
        "season_id": "S1_ECO_ENGINEERING",
        "price": 14.99,
        "currency": "USD",
        "stripe_price_id": os.getenv("STRIPE_PRICE_BP_PREMIUM", ""),
        "description": "Premium Battle Pass - Unlock exclusive seasonal rewards! (Or unlock free with 30-day streak)",
        "alternative_unlock": "30_day_streak"
    }
}


@router.get("/catalog")
async def get_store_catalog(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns the list of available items for purchase"""
    return {
        "success": True,
        "items": STORE_CATALOG,
        "note": "Tokens cannot be purchased. Earn them through gameplay: logging outfits, completing challenges, and maintaining streaks!"
    }


@router.post("/purchase")
async def process_purchase(
    purchase_details: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process an in-app purchase.
    NOTE: Tokens CANNOT be purchased - this endpoint rejects any token purchase attempts!
    """
    user_id = current_user.id
    item_id = purchase_details.get("item_id")
    
    # HARD REJECT token purchases
    if item_id and ("TOKEN" in item_id.upper() or "TOKENS" in item_id.upper()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tokens cannot be purchased. They are earned exclusively through gameplay: logging outfits, completing challenges, maintaining streaks, and providing feedback. Keep playing to earn tokens!"
        )
    
    item_config = STORE_CATALOG.get(item_id)
    
    if not item_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in store catalog."
        )
    
    try:
        from ..services.addiction_service import addiction_service
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Store service is currently unavailable."
        )
    
    # In a real system, you would call a payment gateway here and validate the receipt.
    # For now, we'll simulate the success and move directly to reward fulfillment.
    result = await addiction_service.fulfill_purchase(
        user_id=user_id,
        item_id=item_id,
        item_config=item_config,
        purchase_data=purchase_details
    )
    
    if result.get("error"):
        logger.error(f"Purchase fulfillment failed for user {user_id}: {result['error']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    logger.info(f"💵 PURCHASE successful for user {user_id}: Item {item_id} fulfilled.")
    
    return {
        "success": True,
        "message": f"Purchase complete! {item_config.get('description', 'Item purchased')}",
        "item_purchased": item_id,
        "reward_details": result
    }


@router.post("/create-payment-intent")
async def create_payment_intent(
    item_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a Stripe Payment Intent for Premium Battle Pass purchase.
    NOTE: This endpoint will reject any attempts to create payment intents for tokens!
    """
    # HARD REJECT token purchases
    if item_id and ("TOKEN" in item_id.upper() or "TOKENS" in item_id.upper()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tokens cannot be purchased. They are earned exclusively through gameplay!"
        )
    
    item_config = STORE_CATALOG.get(item_id)
    
    if not item_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in store catalog."
        )
    
    # In a real implementation, you would create a Stripe Payment Intent here
    # For now, return a mock response
    return {
        "success": True,
        "payment_intent_id": f"mock_pi_{datetime.now().timestamp()}",
        "client_secret": "mock_client_secret",
        "amount": item_config.get("price", 0),
        "currency": item_config.get("currency", "USD")
    }


@router.get("/purchase-history")
async def get_purchase_history(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's purchase history"""
    try:
        user_id = current_user.id
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Store service is currently unavailable."
            )
        
        purchases = await addiction_service.get_purchase_history(user_id)
        
        return {
            "success": True,
            "purchases": purchases,
            "count": len(purchases)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting purchase history for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve purchase history"
        )

