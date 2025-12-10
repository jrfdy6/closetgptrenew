"""
Gacha & Style Tokens API Routes
Endpoints for spending Style Tokens on variable rewards (Variable Ratio Reinforcement)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
import logging
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile

router = APIRouter(prefix="/gacha", tags=["gacha"])
logger = logging.getLogger(__name__)


@router.post("/pull")
async def style_gacha_pull(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Perform a Style Gacha Pull using Style Tokens.
    Implements Variable Ratio Reinforcement - users spend tokens for unpredictable rewards.
    """
    try:
        user_id = current_user.id
        logger.info(f"🎰 Gacha pull requested by user {user_id}")
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            logger.error("AddictionService not available - gacha features disabled")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gacha system is currently unavailable. Please try again later."
            )
        
        pull_result = await addiction_service.perform_style_gacha_pull(user_id=user_id)
        
        if pull_result.get("error") == "Insufficient tokens":
            balance = pull_result.get("balance", 0)
            required = pull_result.get("required", 500)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Insufficient tokens",
                    "message": f"You need {required} Style Tokens to pull. You currently have {balance}.",
                    "balance": balance,
                    "required": required,
                    "shortfall": required - balance
                }
            )
        
        if pull_result.get("error"):
            error_msg = pull_result.get("error")
            logger.error(f"Gacha pull failed for user {user_id}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gacha pull failed due to a server error. Please try again later."
            )
        
        rarity = pull_result.get("rarity", "COMMON")
        reward_data = pull_result.get("reward_data", {})
        
        rarity_messages = {
            "LEGENDARY": "🌟 Legendary Pull! You've unlocked an exclusive style insight!",
            "RARE": "✨ Rare Reward! Something special for your wardrobe!",
            "COMMON": "💫 Style Tokens spent! Here's your reward!"
        }
        
        success_message = rarity_messages.get(rarity, "🎰 Pull successful!")
        logger.info(f"✅ User {user_id} pulled {rarity} reward: {reward_data.get('type', 'Unknown')}")
        
        return {
            "success": True,
            "message": success_message,
            "rarity": rarity,
            "reward": {
                "type": pull_result.get("reward_type", "unknown"),
                "data": reward_data,
                "description": reward_data.get("description", "")
            },
            "tokens": {
                "spent": 500,
                "remaining": pull_result.get("remaining_tokens", 0),
                "balance": pull_result.get("remaining_tokens", 0)
            },
            "visual_effect": pull_result.get("visual_effect", "BLUE_TICK"),
            "dopamine_trigger": pull_result.get("dopamine_trigger", True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Critical error during gacha pull for user {current_user.id if current_user else 'unknown'}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A critical error occurred while processing your pull. Please try again later."
        )


@router.get("/balance")
async def get_token_balance(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's current Style Token balance"""
    try:
        user_id = current_user.id
        
        try:
            from ..services.addiction_service import addiction_service
            from ..config.firebase import db
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Token system is currently unavailable."
            )
        
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        tokens_data = user_data.get('style_tokens', {})
        balance = tokens_data.get('balance', 0)
        total_earned = tokens_data.get('total_earned', 0)
        total_spent = tokens_data.get('total_spent', 0)
        
        pull_cost = 500
        can_pull = balance >= pull_cost
        
        return {
            "success": True,
            "balance": balance,
            "total_earned": total_earned,
            "total_spent": total_spent,
            "pull_cost": pull_cost,
            "can_afford_pull": can_pull,
            "pulls_available": balance // pull_cost if balance >= pull_cost else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token balance for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve token balance"
        )


@router.get("/pull-history")
async def get_pull_history(
    current_user: UserProfile = Depends(get_current_user),
    limit: int = 10
) -> Dict[str, Any]:
    """Get user's recent gacha pull history"""
    try:
        user_id = current_user.id
        
        try:
            from ..config.firebase import db
            from google.cloud.firestore_v1 import Query
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )
        
        pulls_ref = db.collection('users').document(user_id).collection('gacha_pulls')
        query = pulls_ref.order_by('pulled_at', direction=Query.DESCENDING).limit(limit)
        
        pulls = []
        for doc in query.stream():
            pull_data = doc.to_dict()
            pulls.append({
                "id": doc.id,
                "rarity": pull_data.get('rarity', 'COMMON'),
                "reward_type": pull_data.get('reward_type', 'unknown'),
                "reward_data": pull_data.get('reward_data', {}),
                "visual_effect": pull_data.get('visual_effect', 'BLUE_TICK'),
                "pulled_at": pull_data.get('pulled_at'),
                "cost": pull_data.get('cost', 500)
            })
        
        rarity_counts = {"LEGENDARY": 0, "RARE": 0, "COMMON": 0}
        for pull in pulls:
            rarity = pull.get('rarity', 'COMMON')
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        return {
            "success": True,
            "pulls": pulls,
            "count": len(pulls),
            "statistics": {
                "total_pulls": len(pulls),
                "legendary_pulls": rarity_counts["LEGENDARY"],
                "rare_pulls": rarity_counts["RARE"],
                "common_pulls": rarity_counts["COMMON"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pull history for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pull history"
        )

