"""
Global Wardrobe Score (GWS) Service
Calculates composite score from utilization, CPW, AI Fit Score, and revived items
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from ..config.firebase import db
from .utilization_service import utilization_service
from .cpw_service import cpw_service
from .ai_fit_score_service import ai_fit_score_service

logger = logging.getLogger(__name__)


class GWSService:
    """Service for calculating Global Wardrobe Score"""
    
    def __init__(self):
        self.db = db
    
    async def calculate_gws(self, user_id: str) -> float:
        """
        Calculate Global Wardrobe Score (0-100)
        
        Formula:
        GWS = 0.4 * utilization_pct + 0.3 * cpw_improvement_pct + 
              0.2 * ai_fit_score_normalized + 0.1 * revived_items_score
        
        Args:
            user_id: User ID
            
        Returns:
            GWS score (0-100)
        """
        try:
            # Component 1: Utilization (40 points max)
            utilization_data = await utilization_service.calculate_utilization_percentage(
                user_id, days=30
            )
            utilization_pct = utilization_data.get('utilization_percentage', 0)
            utilization_component = (utilization_pct / 100) * 40
            
            # Component 2: CPW Improvement (30 points max)
            cpw_trend = await cpw_service.calculate_cpw_trend(user_id, days=30)
            cpw_change = cpw_trend.get('change_percentage', 0)
            
            # Normalize CPW change to 0-1 (max improvement is -20%, max decline is +20%)
            cpw_normalized = max(0, min(1, (-cpw_change + 20) / 40))
            cpw_component = cpw_normalized * 30
            
            # Component 3: AI Fit Score normalized (20 points max)
            ai_fit_score = await ai_fit_score_service.calculate_ai_fit_score(user_id)
            ai_fit_component = (ai_fit_score / 100) * 20
            
            # Component 4: Revived Items Score (10 points max)
            revived_score = await self._calculate_revived_items_score(user_id)
            revived_component = revived_score * 10
            
            # Calculate total GWS
            gws = utilization_component + cpw_component + ai_fit_component + revived_component
            gws = round(gws, 1)
            
            # Update user profile with GWS
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'gws': gws,
                'gws_last_calculated': datetime.now().isoformat()
            })
            
            logger.info(f"GWS for user {user_id}: {gws} "
                       f"(util: {utilization_component:.1f}, "
                       f"cpw: {cpw_component:.1f}, "
                       f"ai: {ai_fit_component:.1f}, "
                       f"revived: {revived_component:.1f})")
            
            return gws
            
        except Exception as e:
            logger.error(f"Error calculating GWS: {e}", exc_info=True)
            return 0.0
    
    async def get_gws_breakdown(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed GWS breakdown for UI display
        
        Returns:
            Dict with total GWS and component scores
        """
        try:
            # Get all components
            utilization_data = await utilization_service.calculate_utilization_percentage(user_id, days=30)
            cpw_trend = await cpw_service.calculate_cpw_trend(user_id, days=30)
            ai_fit_score = await ai_fit_score_service.calculate_ai_fit_score(user_id)
            revived_score = await self._calculate_revived_items_score(user_id)
            
            # Calculate components
            utilization_pct = utilization_data.get('utilization_percentage', 0)
            utilization_component = (utilization_pct / 100) * 40
            
            cpw_change = cpw_trend.get('change_percentage', 0)
            cpw_normalized = max(0, min(1, (-cpw_change + 20) / 40))
            cpw_component = cpw_normalized * 30
            
            ai_fit_component = (ai_fit_score / 100) * 20
            revived_component = revived_score * 10
            
            total_gws = utilization_component + cpw_component + ai_fit_component + revived_component
            
            return {
                "total_gws": round(total_gws, 1),
                "components": {
                    "utilization": {
                        "score": round(utilization_component, 1),
                        "max": 40,
                        "percentage": utilization_pct,
                        "label": "Wardrobe Usage"
                    },
                    "cpw_improvement": {
                        "score": round(cpw_component, 1),
                        "max": 30,
                        "percentage": round(cpw_normalized * 100, 1),
                        "change": cpw_change,
                        "label": "Value Optimization"
                    },
                    "ai_fit": {
                        "score": round(ai_fit_component, 1),
                        "max": 20,
                        "raw_score": ai_fit_score,
                        "label": "AI Understanding"
                    },
                    "revived_items": {
                        "score": round(revived_component, 1),
                        "max": 10,
                        "percentage": round(revived_score * 100, 1),
                        "label": "Item Revival"
                    }
                },
                "insights": self._generate_gws_insights(total_gws, {
                    "utilization": utilization_pct,
                    "cpw_change": cpw_change,
                    "ai_fit": ai_fit_score,
                    "revived": revived_score
                })
            }
            
        except Exception as e:
            logger.error(f"Error getting GWS breakdown: {e}", exc_info=True)
            return {
                "total_gws": 0,
                "components": {},
                "insights": []
            }
    
    async def _calculate_revived_items_score(self, user_id: str) -> float:
        """
        Calculate score based on how many dormant items have been revived (0-1)
        
        An item is "revived" if it was dormant (180+ days) and worn in last 30 days
        """
        try:
            # Get items worn in last 30 days
            recent_cutoff = (datetime.now() - timedelta(days=30)).timestamp() * 1000
            
            # Get items that were dormant before but worn recently
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            all_items = list(wardrobe_ref.stream())
            
            revived_count = 0
            total_previously_dormant = 0
            
            for doc in all_items:
                item_data = doc.to_dict()
                last_worn = item_data.get('lastWorn', 0)
                wear_count = item_data.get('wearCount', 0)
                
                # Item was dormant if it had low wear count or old last worn
                was_dormant = wear_count <= 2 or (last_worn > 0 and last_worn < recent_cutoff - (180 * 24 * 60 * 60 * 1000))
                
                if was_dormant:
                    total_previously_dormant += 1
                    
                    # Check if worn recently
                    if last_worn >= recent_cutoff:
                        revived_count += 1
            
            if total_previously_dormant == 0:
                return 0.5  # Neutral score if no dormant items
            
            # Score is percentage of dormant items that were revived
            score = revived_count / total_previously_dormant
            
            return min(max(score, 0), 1)
            
        except Exception as e:
            logger.error(f"Error calculating revived items score: {e}", exc_info=True)
            return 0.5
    
    def _generate_gws_insights(self, gws: float, components: Dict[str, Any]) -> List[str]:
        """Generate actionable insights based on GWS components"""
        insights = []
        
        # Overall GWS insights
        if gws >= 75:
            insights.append("Excellent! You're maximizing your wardrobe's potential.")
        elif gws >= 50:
            insights.append("Great progress! Your wardrobe is working well for you.")
        elif gws >= 25:
            insights.append("Good start! Keep logging outfits to improve your score.")
        else:
            insights.append("Opportunity ahead! Complete challenges to boost your score.")
        
        # Component-specific insights
        if components.get('utilization', 0) < 40:
            insights.append("Try wearing different items to increase your utilization score.")
        
        if components.get('cpw_change', 0) > 5:
            insights.append("Log more outfits to reduce your cost-per-wear.")
        
        if components.get('ai_fit', 0) < 50:
            insights.append("Rate more outfits to help the AI learn your style.")
        
        if components.get('revived', 0) < 0.3:
            insights.append("Revive forgotten items to unlock their value!")
        
        return insights[:3]  # Return top 3 insights


# Create singleton instance
gws_service = GWSService()


# Export
__all__ = ['GWSService', 'gws_service']

