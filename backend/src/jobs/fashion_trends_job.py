import asyncio
import schedule
import time
from datetime import datetime
import logging
import sys
import os

# Add the src directory to the path so we can import our services
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.fashion_trends_service import FashionTrendsService

logger = logging.getLogger(__name__)

async def fetch_fashion_trends_job():
    """Scheduled job to fetch fashion trends once daily at 9 AM."""
    try:
        logger.info("🔄 Starting daily fashion trends fetch job")
        
        trends_service = FashionTrendsService()
        result = await trends_service.fetch_and_store_trends()
        
        if result["status"] == "success":
            logger.info(f"✅ Daily trends fetch completed successfully. Fetched {result['trends_fetched']} trends")
        elif result["status"] == "skipped":
            logger.info(f"⏭️ Trends fetch skipped: {result['reason']}")
        else:
            logger.error(f"❌ Trends fetch failed: {(result.get('error', 'Unknown error') if result else 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error in fashion trends job: {str(e)}")

def run_fashion_trends_job():
    """Wrapper function to run the async job."""
    asyncio.run(fetch_fashion_trends_job())

def setup_daily_schedule():
    """Set up the daily schedule for fashion trends."""
    # Schedule the job to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(run_fashion_trends_job)
    
    # Also schedule a backup run at 3:00 PM in case the morning run fails
    schedule.every().day.at("15:00").do(run_fashion_trends_job)
    
    logger.info("📅 Fashion trends schedule set up:")
    logger.info("   - Daily at 9:00 AM (primary)")
    logger.info("   - Daily at 3:00 PM (backup)")

def run_scheduler():
    """Run the scheduler continuously."""
    logger.info("🚀 Starting fashion trends scheduler...")
    
    # Set up the schedule
    setup_daily_schedule()
    
    # Run the job immediately on startup (for testing/initial setup)
    logger.info("🔄 Running initial trends fetch...")
    run_fashion_trends_job()
    
    # Keep the scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Scheduler error: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fashion_trends_job.log'),
            logging.StreamHandler()
        ]
    )
    
    # Run the scheduler
    run_scheduler() 