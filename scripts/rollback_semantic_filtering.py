#!/usr/bin/env python3
"""
Rollback Script for Semantic Filtering
=====================================

Emergency rollback mechanism to quickly disable semantic filtering
and force traditional filtering in case of issues.

Usage:
    python scripts/rollback_semantic_filtering.py --environment production
    python scripts/rollback_semantic_filtering.py --environment staging
"""

import argparse
import os
import sys
import logging
from typing import Dict, Any

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from config.feature_flags import feature_flags

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rollback_semantic_filtering(environment: str = "production") -> Dict[str, Any]:
    """
    Emergency rollback to disable semantic filtering and force traditional filtering.
    
    Args:
        environment: Target environment (production, staging, development)
    
    Returns:
        Dict with rollback status
    """
    
    logger.info(f"🚨 EMERGENCY ROLLBACK: Disabling semantic filtering for {environment}")
    
    try:
        # Force traditional filtering (rollback mode)
        feature_flags.override_flag('FEATURE_FORCE_TRADITIONAL', True)
        feature_flags.override_flag('FEATURE_SEMANTIC_MATCH', False)
        feature_flags.override_flag('FEATURE_DEBUG_OUTPUT', True)  # Keep debug for monitoring
        
        logger.info("✅ ROLLBACK COMPLETE: Traditional filtering forced")
        logger.info("🔍 All semantic filtering is now disabled")
        logger.info("📊 Debug output enabled for monitoring")
        
        return {
            "success": True,
            "environment": environment,
            "rollback_completed": True,
            "feature_flags": feature_flags.get_all_flags(),
            "message": "Semantic filtering disabled, traditional filtering forced"
        }
        
    except Exception as e:
        logger.error(f"❌ ROLLBACK FAILED: {e}")
        return {
            "success": False,
            "environment": environment,
            "rollback_completed": False,
            "error": str(e),
            "message": "Rollback failed - manual intervention required"
        }

def restore_semantic_filtering(environment: str = "production") -> Dict[str, Any]:
    """
    Restore semantic filtering after rollback (use with caution).
    
    Args:
        environment: Target environment (production, staging, development)
    
    Returns:
        Dict with restore status
    """
    
    logger.info(f"🔄 RESTORING: Re-enabling semantic filtering for {environment}")
    
    try:
        # Restore semantic filtering
        feature_flags.override_flag('FEATURE_FORCE_TRADITIONAL', False)
        feature_flags.override_flag('FEATURE_SEMANTIC_MATCH', True)
        
        logger.info("✅ RESTORE COMPLETE: Semantic filtering re-enabled")
        
        return {
            "success": True,
            "environment": environment,
            "restore_completed": True,
            "feature_flags": feature_flags.get_all_flags(),
            "message": "Semantic filtering restored"
        }
        
    except Exception as e:
        logger.error(f"❌ RESTORE FAILED: {e}")
        return {
            "success": False,
            "environment": environment,
            "restore_completed": False,
            "error": str(e),
            "message": "Restore failed - manual intervention required"
        }

def get_feature_flag_status() -> Dict[str, Any]:
    """Get current feature flag status."""
    return {
        "success": True,
        "feature_flags": feature_flags.get_all_flags(),
        "semantic_enabled": feature_flags.is_enabled('FEATURE_SEMANTIC_MATCH'),
        "force_traditional": feature_flags.is_enabled('FEATURE_FORCE_TRADITIONAL'),
        "message": "Feature flag status retrieved"
    }

def main():
    parser = argparse.ArgumentParser(description="Semantic Filtering Rollback Tool")
    parser.add_argument("--environment", default="production", 
                       choices=["production", "staging", "development"],
                       help="Target environment")
    parser.add_argument("--action", default="rollback",
                       choices=["rollback", "restore", "status"],
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "rollback":
        result = rollback_semantic_filtering(args.environment)
    elif args.action == "restore":
        result = restore_semantic_filtering(args.environment)
    elif args.action == "status":
        result = get_feature_flag_status()
    else:
        result = {"success": False, "message": "Invalid action"}
    
    print(f"\n🎯 RESULT: {result}")
    
    if not result.get("success", False):
        sys.exit(1)

if __name__ == "__main__":
    main()
