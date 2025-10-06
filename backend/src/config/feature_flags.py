"""
Feature Flags Configuration
==========================

Centralized feature flag management for safe rollouts.
All flags default to False for maximum safety.
"""

import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FeatureFlags:
    """Centralized feature flag management."""
    
    def __init__(self):
        self.flags = {
            # Semantic filtering feature flag - defaults to False for safety
            'FEATURE_SEMANTIC_MATCH': self._get_bool_flag('FEATURE_SEMANTIC_MATCH', False),
            
            # Debug output flag - defaults to False for production
            'FEATURE_DEBUG_OUTPUT': self._get_bool_flag('FEATURE_DEBUG_OUTPUT', False),
            
            # Staging-specific flags
            'FEATURE_STAGING_SEMANTIC': self._get_bool_flag('FEATURE_STAGING_SEMANTIC', False),
            
            # Rollback flags
            'FEATURE_FORCE_TRADITIONAL': self._get_bool_flag('FEATURE_FORCE_TRADITIONAL', False),
        }
        
        self._log_flag_status()
    
    def _get_bool_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get boolean feature flag from environment with safe defaults."""
        try:
            value = os.getenv(flag_name, str(default)).lower()
            return value in ('true', '1', 'yes', 'on')
        except Exception as e:
            logger.warning(f"⚠️ Error reading flag {flag_name}: {e}, using default {default}")
            return default
    
    def _log_flag_status(self):
        """Log current feature flag status for visibility."""
        logger.info("🚩 Feature Flags Status:")
        for flag, value in self.flags.items():
            status = "✅ ENABLED" if value else "❌ DISABLED"
            logger.info(f"  {flag}: {status}")
    
    def is_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.flags.get(flag_name, False)
    
    def get_all_flags(self) -> Dict[str, bool]:
        """Get all feature flags for debugging."""
        return self.flags.copy()
    
    def override_flag(self, flag_name: str, value: bool):
        """Override a flag for testing (use with caution)."""
        if flag_name in self.flags:
            old_value = self.flags[flag_name]
            self.flags[flag_name] = value
            logger.warning(f"🔄 OVERRIDE: {flag_name} changed from {old_value} to {value}")
        else:
            logger.error(f"❌ Unknown flag: {flag_name}")

# Global feature flags instance
feature_flags = FeatureFlags()

# Convenience functions
def is_semantic_match_enabled() -> bool:
    """Check if semantic matching is enabled."""
    return feature_flags.is_enabled('FEATURE_SEMANTIC_MATCH')

def is_debug_output_enabled() -> bool:
    """Check if debug output is enabled."""
    return feature_flags.is_enabled('FEATURE_DEBUG_OUTPUT')

def is_staging_semantic_enabled() -> bool:
    """Check if staging semantic features are enabled."""
    return feature_flags.is_enabled('FEATURE_STAGING_SEMANTIC')

def is_force_traditional_enabled() -> bool:
    """Check if traditional filtering is forced (rollback mode)."""
    return feature_flags.is_enabled('FEATURE_FORCE_TRADITIONAL')
