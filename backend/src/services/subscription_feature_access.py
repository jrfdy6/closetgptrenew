"""
Subscription Feature Access Service
Checks if users can access premium features based on their subscription tier.
"""

from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timezone
import logging

from ..config.firebase import db

logger = logging.getLogger(__name__)

# Feature access matrix - which tiers can access which features
FEATURE_ACCESS_MATRIX = {
    'basic_outfit_generation': ['tier1', 'tier2', 'tier3'],
    'semantic_filtering': ['tier2', 'tier3'],  # Feature #4: Advanced filtering
    'style_persona_analysis': ['tier2', 'tier3'],  # Feature #6: Style persona
    'flatlay_generation': ['tier1', 'tier2', 'tier3'],  # All tiers, but with different limits
    'advanced_personalization': ['tier2', 'tier3'],
    'wardrobe_analytics': ['tier2', 'tier3'],
    'forgotten_gems': ['tier2', 'tier3'],  # Forgotten gems wardrobe insights
    'unlimited_history': ['tier3'],
}

# Active subscription statuses
ACTIVE_STATUSES = ['active', 'trialing']


def check_feature_access(
    user_id: str, 
    feature: str,
    require_active: bool = True
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Check if user can access a feature based on their subscription.
    
    Args:
        user_id: User ID
        feature: Feature name (must be in FEATURE_ACCESS_MATRIX)
        require_active: Whether to require active subscription status
    
    Returns:
        Tuple of (allowed: bool, error_message: Optional[str], subscription_info: Dict)
    """
    try:
        # Get user document
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            return False, "User not found", {}
        
        user_data = user_doc.to_dict() or {}
        
        # Check if feature is defined in access matrix
        if feature not in FEATURE_ACCESS_MATRIX:
            logger.warning(f"Unknown feature: {feature}")
            return False, f"Unknown feature: {feature}", {}
        
        # Get subscription info (support both old and new schema)
        subscription = user_data.get('subscription', {})
        
        # Determine role/tier
        role = subscription.get('role') or subscription.get('tier', 'tier1')
        status = subscription.get('status', 'active')
        
        # Check subscription status
        if require_active and status not in ACTIVE_STATUSES:
            return False, f"Subscription status is {status}. Active subscription required.", {
                'role': role,
                'status': status,
                'required_statuses': ACTIVE_STATUSES
            }
        
        # Check if role has access to feature
        allowed_roles = FEATURE_ACCESS_MATRIX[feature]
        if role not in allowed_roles:
            # Map roles to friendly names for error message
            role_names = {
                'tier1': 'Free',
                'tier2': 'Pro',
                'tier3': 'Premium'
            }
            required_roles_str = ' or '.join([role_names.get(r, r) for r in allowed_roles])
            current_role_name = role_names.get(role, role)
            
            return False, f"This feature requires {required_roles_str} subscription. You currently have {current_role_name}.", {
                'role': role,
                'status': status,
                'required_roles': allowed_roles,
                'feature': feature
            }
        
        # Access granted
        subscription_info = {
            'role': role,
            'status': status,
            'feature': feature,
            'access_granted': True
        }
        
        # Add quota info for flatlay
        if feature == 'flatlay_generation':
            quotas = user_data.get('quotas', {})
            subscription_info['flatlays_remaining'] = quotas.get('flatlaysRemaining', 0)
        
        return True, None, subscription_info
    
    except Exception as e:
        logger.error(f"Error checking feature access: {e}", exc_info=True)
        return False, f"Error checking subscription: {str(e)}", {}


def get_user_subscription_info(user_id: str) -> Dict[str, Any]:
    """
    Get user's subscription information.
    
    Returns:
        Dict with role, status, and feature access info
    """
    try:
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            return {'error': 'User not found'}
        
        user_data = user_doc.to_dict() or {}
        subscription = user_data.get('subscription', {})
        billing = user_data.get('billing', {})
        quotas = user_data.get('quotas', {})
        
        role = subscription.get('role') or subscription.get('tier', 'tier1')
        status = subscription.get('status', 'active')
        
        # Determine which features user can access
        accessible_features = []
        for feature, allowed_roles in FEATURE_ACCESS_MATRIX.items():
            if role in allowed_roles and status in ACTIVE_STATUSES:
                accessible_features.append(feature)
        
        return {
            'role': role,
            'status': status,
            'stripe_customer_id': billing.get('stripeCustomerId'),
            'flatlays_remaining': quotas.get('flatlaysRemaining', 0),
            'accessible_features': accessible_features,
            'current_period_end': subscription.get('currentPeriodEnd'),
            'price_id': subscription.get('priceId')
        }
    
    except Exception as e:
        logger.error(f"Error getting subscription info: {e}", exc_info=True)
        return {'error': str(e)}

