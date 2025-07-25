#!/usr/bin/env python3
"""
Fashion Trends Scheduler Startup Script

This script runs the fashion trends scheduler that fetches real-time fashion trends
from Google Trends and stores them in Firestore once daily.

Usage:
    python run_fashion_trends_scheduler.py

The scheduler will:
- Run an initial fetch immediately
- Schedule daily fetches at 9:00 AM and 3:00 PM (backup)
- Log all activities to fashion_trends_job.log
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Set up environment variables if not already set
if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    # You'll need to set this to your Firebase service account key file
    print("⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS not set")
    print("Please set the path to your Firebase service account key file")
    print("Example: export GOOGLE_APPLICATION_CREDENTIALS='path/to/serviceAccountKey.json'")

# Import and run the scheduler
try:
    from jobs.fashion_trends_job import run_scheduler
    print("🚀 Starting Fashion Trends Scheduler...")
    print("📅 Will fetch trends daily at 9:00 AM and 3:00 PM")
    print("📝 Logs will be saved to fashion_trends_job.log")
    print("🛑 Press Ctrl+C to stop the scheduler")
    print("-" * 50)
    
    run_scheduler()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting scheduler: {e}")
    sys.exit(1) 