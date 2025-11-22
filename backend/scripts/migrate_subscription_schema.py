#!/usr/bin/env python3
"""
Migration Script: Convert User Subscription Schema

Migrates users from old schema:
  subscription: { tier, openai_flatlays_used, flatlay_week_start }

To new schema:
  billing: { stripeCustomerId, defaultPaymentMethodId? }
  subscription: { status, role, currentPeriodEnd, priceId }
  quotas: { flatlaysRemaining, lastRefillAt }

Usage:
    python scripts/migrate_subscription_schema.py [--dry-run] [--user-id USER_ID] [--limit N]
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import argparse
import logging

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tier limits mapping (same as subscription_utils.py)
TIER_LIMITS = {
    "tier1": 1,
    "tier2": 7,
    "tier3": 30,
}

WEEKLY_ALLOWANCE_SECONDS = 7 * 24 * 60 * 60


def parse_iso8601(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 string into an aware UTC datetime."""
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def migrate_user_subscription(user_id: str, user_data: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Migrate a single user's subscription schema.
    
    Returns:
        Dict with migration result: { migrated: bool, error: Optional[str], changes: Dict }
    """
    try:
        # Check if already migrated (has new schema)
        if 'billing' in user_data and 'quotas' in user_data:
            subscription = user_data.get('subscription', {})
            if 'role' in subscription and 'currentPeriodEnd' in subscription:
                return {
                    'migrated': False,
                    'error': None,
                    'reason': 'already_migrated',
                    'changes': {}
                }
        
        # Get old subscription data
        old_subscription = user_data.get('subscription', {})
        old_tier = old_subscription.get('tier', 'tier1')
        old_used = old_subscription.get('openai_flatlays_used', 0)
        old_week_start_str = old_subscription.get('flatlay_week_start')
        
        # Calculate quotas from old data
        now = datetime.now(timezone.utc)
        now_timestamp = int(now.timestamp())
        
        # Parse old week start
        old_week_start = parse_iso8601(old_week_start_str) or now
        
        # Calculate remaining flatlays
        limit = TIER_LIMITS.get(old_tier, 1)
        
        # Check if week has passed since last reset
        time_since_reset = (now - old_week_start).total_seconds()
        if time_since_reset >= WEEKLY_ALLOWANCE_SECONDS:
            # Week passed, reset to full limit
            flatlays_remaining = limit
            last_refill_at = now_timestamp
        else:
            # Week hasn't passed, calculate remaining
            flatlays_remaining = max(0, limit - (old_used or 0))
            last_refill_at = int(old_week_start.timestamp())
        
        # Map old tier to new role (they're the same)
        role = old_tier  # tier1, tier2, or tier3
        
        # Determine status
        old_status = old_subscription.get('status', 'active')
        status = old_status if old_status in ['active', 'canceled', 'past_due'] else 'active'
        
        # Get stripe customer ID if exists
        stripe_customer_id = old_subscription.get('stripe_customer_id') or old_subscription.get('stripeCustomerId')
        stripe_subscription_id = old_subscription.get('stripe_subscription_id') or old_subscription.get('stripeSubscriptionId')
        
        # Calculate current period end
        if stripe_subscription_id:
            # If they have a subscription, use a future date (30 days)
            current_period_end = now_timestamp + (30 * 24 * 60 * 60)
        else:
            # Free tier - use weekly period
            current_period_end = now_timestamp + WEEKLY_ALLOWANCE_SECONDS
        
        # Map tier to price ID
        price_id_map = {
            'tier1': 'free',
            'tier2': os.getenv('STRIPE_PRICE_TIER2', 'tier2'),
            'tier3': os.getenv('STRIPE_PRICE_TIER3', 'tier3'),
        }
        price_id = price_id_map.get(role, 'free')
        
        # Prepare new schema
        billing_data = {}
        if stripe_customer_id:
            billing_data['stripeCustomerId'] = stripe_customer_id
        
        subscription_data = {
            'status': status,
            'role': role,
            'currentPeriodEnd': current_period_end,
            'priceId': price_id,
        }
        
        # Keep stripe subscription ID if exists
        if stripe_subscription_id:
            subscription_data['stripeSubscriptionId'] = stripe_subscription_id
        
        quotas_data = {
            'flatlaysRemaining': flatlays_remaining,
            'lastRefillAt': last_refill_at,
        }
        
        # Check if name needs to be migrated to displayName
        display_name = user_data.get('displayName') or user_data.get('name')
        
        # Prepare update payload
        update_payload = {
            'billing': billing_data,
            'subscription': subscription_data,
            'quotas': quotas_data,
        }
        
        # Add displayName if needed
        if display_name and 'displayName' not in user_data:
            update_payload['displayName'] = display_name
        
        # Log changes
        changes = {
            'old_tier': old_tier,
            'new_role': role,
            'old_used': old_used,
            'new_remaining': flatlays_remaining,
            'old_status': old_status,
            'new_status': status,
            'stripe_customer_id': stripe_customer_id,
        }
        
        if not dry_run:
            # Import Firebase
            try:
                from src.config.firebase import db
            except ImportError:
                from config.firebase import db
            
            if db is None:
                return {
                    'migrated': False,
                    'error': 'Firebase not initialized',
                    'changes': changes
                }
            
            # Update user document
            user_ref = db.collection('users').document(user_id)
            
            # Use update to preserve existing fields
            user_ref.update(update_payload)
            
            logger.info(f"✅ Migrated user {user_id}: {old_tier} -> {role}, {old_used} used -> {flatlays_remaining} remaining")
        else:
            logger.info(f"🔍 [DRY RUN] Would migrate user {user_id}: {old_tier} -> {role}, {old_used} used -> {flatlays_remaining} remaining")
        
        return {
            'migrated': True,
            'error': None,
            'changes': changes
        }
    
    except Exception as e:
        logger.error(f"❌ Error migrating user {user_id}: {e}", exc_info=True)
        return {
            'migrated': False,
            'error': str(e),
            'changes': {}
        }


def migrate_all_users(dry_run: bool = False, limit: Optional[int] = None) -> Dict[str, Any]:
    """Migrate all users in the database."""
    try:
        # Import Firebase
        try:
            from src.config.firebase import db
        except ImportError:
            from config.firebase import db
        
        if db is None:
            return {
                'success': False,
                'error': 'Firebase not initialized',
                'stats': {}
            }
        
        logger.info("🚀 Starting subscription schema migration...")
        logger.info(f"📋 Dry run: {dry_run}")
        
        stats = {
            'total_users': 0,
            'migrated': 0,
            'already_migrated': 0,
            'errors': 0,
            'skipped': 0,
        }
        
        # Get all users
        users_query = db.collection('users')
        if limit:
            users_query = users_query.limit(limit)
        
        users = users_query.stream()
        
        for user_doc in users:
            user_id = user_doc.id
            user_data = user_doc.to_dict() or {}
            
            stats['total_users'] += 1
            
            # Skip if no subscription data
            if 'subscription' not in user_data:
                stats['skipped'] += 1
                logger.debug(f"⏭️ Skipped user {user_id}: No subscription data")
                continue
            
            # Migrate user
            result = migrate_user_subscription(user_id, user_data, dry_run=dry_run)
            
            if result['migrated']:
                stats['migrated'] += 1
            elif result.get('reason') == 'already_migrated':
                stats['already_migrated'] += 1
            elif result.get('error'):
                stats['errors'] += 1
        
        logger.info("✅ Migration complete!")
        logger.info(f"📊 Stats: {stats}")
        
        return {
            'success': True,
            'stats': stats,
            'dry_run': dry_run
        }
    
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'stats': stats if 'stats' in locals() else {}
        }


def migrate_single_user(user_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Migrate a single user by ID."""
    try:
        # Import Firebase
        try:
            from src.config.firebase import db
        except ImportError:
            from config.firebase import db
        
        if db is None:
            return {
                'success': False,
                'error': 'Firebase not initialized'
            }
        
        # Get user document
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            return {
                'success': False,
                'error': f'User {user_id} not found'
            }
        
        user_data = user_doc.to_dict() or {}
        result = migrate_user_subscription(user_id, user_data, dry_run=dry_run)
        
        return {
            'success': result['migrated'] or result.get('reason') == 'already_migrated',
            'result': result
        }
    
    except Exception as e:
        logger.error(f"❌ Error migrating user {user_id}: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate user subscription schema')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no changes)')
    parser.add_argument('--user-id', type=str, help='Migrate specific user ID')
    parser.add_argument('--limit', type=int, help='Limit number of users to process')
    
    args = parser.parse_args()
    
    if args.user_id:
        result = migrate_single_user(args.user_id, dry_run=args.dry_run)
        print(f"\n{'DRY RUN: ' if args.dry_run else ''}Migration result:")
        print(result)
    else:
        result = migrate_all_users(dry_run=args.dry_run, limit=args.limit)
        print(f"\n{'DRY RUN: ' if args.dry_run else ''}Migration complete:")
        print(f"Total users: {result['stats']['total_users']}")
        print(f"Migrated: {result['stats']['migrated']}")
        print(f"Already migrated: {result['stats']['already_migrated']}")
        print(f"Errors: {result['stats']['errors']}")
        print(f"Skipped: {result['stats']['skipped']}")

