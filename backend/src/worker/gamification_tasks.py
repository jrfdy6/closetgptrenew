"""
Gamification Background Worker Tasks
Scheduled tasks for daily aggregations and weekly challenge generation
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.firebase import db
from src.services.cpw_service import cpw_service
from src.services.gws_service import gws_service
from src.services.ai_fit_score_service import ai_fit_score_service
from src.services.challenge_service import challenge_service
from src.custom_types.gamification import CHALLENGE_CATALOG, ChallengeType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def daily_aggregation_task():
    """
    Run daily aggregation tasks
    - Recalculate CPW for all users
    - Update GWS scores
    - Expire old challenges
    - Update AI Fit Scores
    """
    logger.info("="*60)
    logger.info("🌅 STARTING DAILY GAMIFICATION AGGREGATION")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("="*60)
    
    try:
        # Get all users
        users = db.collection('users').stream()
        user_ids = [user.id for user in users]
        
        logger.info(f"Found {len(user_ids)} users to process")
        
        cpw_updated = 0
        gws_updated = 0
        ai_scores_updated = 0
        challenges_expired = 0
        
        for user_id in user_ids:
            try:
                # 1. Recalculate CPW
                count = await cpw_service.recalculate_all_cpw_for_user(user_id)
                if count > 0:
                    cpw_updated += 1
                
                # 2. Update GWS
                gws = await gws_service.calculate_gws(user_id)
                if gws > 0:
                    gws_updated += 1
                
                # 3. Update AI Fit Score
                ai_score = await ai_fit_score_service.calculate_ai_fit_score(user_id)
                if ai_score > 0:
                    ai_scores_updated += 1
                    # Update user profile
                    user_ref = db.collection('users').document(user_id)
                    user_ref.update({'ai_fit_score': ai_score})
                
                # 4. Expire old challenges
                expired = await challenge_service.expire_old_challenges(user_id)
                challenges_expired += expired
                
                # Log progress every 10 users
                if cpw_updated % 10 == 0:
                    logger.info(f"Processed {cpw_updated} users...")
                
            except Exception as user_error:
                logger.error(f"Error processing user {user_id}: {user_error}")
                continue
        
        logger.info("="*60)
        logger.info("✅ DAILY AGGREGATION COMPLETE")
        logger.info(f"CPW updated for {cpw_updated} users")
        logger.info(f"GWS updated for {gws_updated} users")
        logger.info(f"AI Scores updated for {ai_scores_updated} users")
        logger.info(f"Expired {challenges_expired} challenges")
        logger.info("="*60)
        
        return {
            "success": True,
            "cpw_updated": cpw_updated,
            "gws_updated": gws_updated,
            "ai_scores_updated": ai_scores_updated,
            "challenges_expired": challenges_expired
        }
        
    except Exception as e:
        logger.error(f"❌ Daily aggregation failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def weekly_challenge_generation_task():
    """
    Run weekly challenge generation
    - Generate new featured challenges
    - Rotate challenge types
    - Clean up old featured challenges
    """
    logger.info("="*60)
    logger.info("🗓️  STARTING WEEKLY CHALLENGE GENERATION")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("="*60)
    
    try:
        # This week's featured challenges (rotate types)
        week_number = datetime.now().isocalendar()[1]
        
        # Rotate challenge types by week
        featured_rotation = [
            "color_harmony",  # Week 1, 5, 9...
            "forgotten_gems_weekly",  # Week 2, 6, 10...
            "30_wears_challenge",  # Week 3, 7, 11...
            "color_harmony"  # Week 4, 8, 12...
        ]
        
        rotation_index = week_number % len(featured_rotation)
        this_week_featured = featured_rotation[rotation_index]
        
        logger.info(f"This week's featured challenge: {this_week_featured}")
        
        # Update featured status in catalog
        for challenge_id, challenge_def in CHALLENGE_CATALOG.items():
            # Mark as featured if it's this week's challenge
            is_featured = (challenge_id == this_week_featured)
            
            # Save to Firestore challenges collection
            challenge_ref = db.collection('challenges').document(challenge_id)
            challenge_ref.set({
                **challenge_def.dict(),
                "featured": is_featured,
                "week_number": week_number,
                "updated_at": datetime.now().isoformat()
            }, merge=True)
        
        logger.info("="*60)
        logger.info("✅ WEEKLY CHALLENGE GENERATION COMPLETE")
        logger.info(f"Featured challenge set: {this_week_featured}")
        logger.info("="*60)
        
        return {
            "success": True,
            "featured_challenge": this_week_featured,
            "week_number": week_number
        }
        
    except Exception as e:
        logger.error(f"❌ Weekly challenge generation failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def streak_bonus_task():
    """
    Award streak bonuses for consistent engagement
    - Daily login streaks
    - Rating streaks
    - Outfit logging streaks
    """
    logger.info("🔥 Checking user streaks...")
    
    try:
        # Get all users
        users = db.collection('users').stream()
        streak_bonuses_awarded = 0
        
        for user_doc in users:
            user_id = user_doc.id
            user_data = user_doc.to_dict()
            
            # Check for 7-day rating streak
            feedback_ref = db.collection('outfit_feedback')\
                .where('user_id', '==', user_id)\
                .order_by('timestamp', direction='DESCENDING')\
                .limit(7)
            
            feedback_docs = list(feedback_ref.stream())
            
            # If user rated something every day for 7 days, award bonus
            if len(feedback_docs) >= 7:
                # Simplified check - just count
                from src.services.gamification_service import gamification_service
                await gamification_service.award_xp(
                    user_id=user_id,
                    amount=20,
                    reason="7-day rating streak bonus!",
                    metadata={"streak_type": "rating", "days": 7}
                )
                streak_bonuses_awarded += 1
        
        logger.info(f"✅ Awarded {streak_bonuses_awarded} streak bonuses")
        return {"success": True, "bonuses_awarded": streak_bonuses_awarded}
        
    except Exception as e:
        logger.error(f"Error awarding streak bonuses: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


# Main worker function that can be called by cron
async def run_daily_tasks():
    """Run all daily tasks in sequence"""
    logger.info("🚀 Starting daily gamification tasks...")
    
    results = {}
    
    # Task 1: Daily aggregations
    results['daily_aggregation'] = await daily_aggregation_task()
    
    # Task 2: Streak bonuses
    results['streak_bonuses'] = await streak_bonus_task()
    
    logger.info("✅ All daily tasks complete")
    return results


async def run_weekly_tasks():
    """Run all weekly tasks"""
    logger.info("🚀 Starting weekly gamification tasks...")
    
    results = {}
    
    # Task 1: Challenge generation
    results['challenge_generation'] = await weekly_challenge_generation_task()
    
    logger.info("✅ All weekly tasks complete")
    return results


# For Railway cron or manual execution
if __name__ == "__main__":
    import asyncio
    
    # Check command line args
    if len(sys.argv) > 1 and sys.argv[1] == "weekly":
        asyncio.run(run_weekly_tasks())
    else:
        asyncio.run(run_daily_tasks())


# Create singleton instance
challenge_service = ChallengeService()
