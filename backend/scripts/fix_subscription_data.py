#!/usr/bin/env python3
"""
Fix subscription data for users with missing currentPeriodEnd or mismatched role/priceId.
This script:
1. Fetches subscription from Stripe
2. Updates currentPeriodEnd from Stripe data
3. Fixes role/priceId mismatches
4. Cleans up legacy fields
"""

import os
import sys
from pathlib import Path

# Add backend to path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))

from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
import stripe

# Initialize Firebase
try:
    cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)
except:
    # Try default credentials
    try:
        firebase_admin.initialize_app()
    except Exception as e:
        print(f"❌ Firebase init error: {e}")
        sys.exit(1)

db = firestore.client()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    print("❌ STRIPE_SECRET_KEY not set")
    sys.exit(1)

STRIPE_PRICE_IDS = {
    "tier2": os.getenv("STRIPE_PRICE_TIER2", ""),
    "tier3": os.getenv("STRIPE_PRICE_TIER3", ""),
}

def fix_user_subscription(user_id: str, dry_run: bool = True):
    """Fix subscription data for a specific user"""
    print(f"\n🔍 Fixing subscription for user: {user_id}")
    
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print(f"❌ User {user_id} not found")
            return False
        
        user_data = user_doc.to_dict() or {}
        subscription = user_data.get('subscription', {})
        billing = user_data.get('billing', {})
        
        stripe_customer_id = billing.get('stripeCustomerId')
        stripe_subscription_id = subscription.get('stripeSubscriptionId')
        
        if not stripe_subscription_id:
            print(f"⚠️  No Stripe subscription ID found for user {user_id}")
            return False
        
        print(f"📋 Current subscription data:")
        print(f"   Role: {subscription.get('role')}")
        print(f"   PriceId: {subscription.get('priceId')}")
        print(f"   currentPeriodEnd: {subscription.get('currentPeriodEnd')}")
        print(f"   Status: {subscription.get('status')}")
        
        # Fetch subscription from Stripe
        try:
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
            print(f"✅ Fetched subscription from Stripe: {stripe_sub.id}")
        except Exception as e:
            print(f"❌ Failed to fetch subscription from Stripe: {e}")
            return False
        
        # Determine correct role from Stripe subscription
        items = stripe_sub.get('items', {}).get('data', [])
        correct_role = 'tier2'  # Default
        correct_price_id = None
        
        if items:
            price_id = items[0].get('price', {}).get('id', '')
            if price_id == STRIPE_PRICE_IDS.get('tier3'):
                correct_role = 'tier3'
                correct_price_id = price_id
            elif price_id == STRIPE_PRICE_IDS.get('tier2'):
                correct_role = 'tier2'
                correct_price_id = price_id
        
        # Get period end from Stripe
        period_end = stripe_sub.get('current_period_end', 0)
        status = stripe_sub.get('status', 'active')
        cancel_at_period_end = stripe_sub.get('cancel_at_period_end', False)
        
        print(f"\n📊 Stripe subscription data:")
        print(f"   Role: {correct_role}")
        print(f"   PriceId: {correct_price_id}")
        print(f"   Period End: {period_end} ({datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else 'N/A'})")
        print(f"   Status: {status}")
        print(f"   Cancel at period end: {cancel_at_period_end}")
        
        # Prepare updates
        updates = {}
        needs_update = False
        
        # Fix currentPeriodEnd
        if subscription.get('currentPeriodEnd', 0) != period_end:
            updates['subscription.currentPeriodEnd'] = period_end
            needs_update = True
            print(f"✅ Will update currentPeriodEnd: {subscription.get('currentPeriodEnd')} -> {period_end}")
        
        # Fix role if mismatched
        if subscription.get('role') != correct_role:
            updates['subscription.role'] = correct_role
            needs_update = True
            print(f"✅ Will update role: {subscription.get('role')} -> {correct_role}")
        
        # Fix priceId if mismatched
        if subscription.get('priceId') != correct_price_id and correct_price_id:
            updates['subscription.priceId'] = correct_price_id
            needs_update = True
            print(f"✅ Will update priceId: {subscription.get('priceId')} -> {correct_price_id}")
        
        # Update status
        if subscription.get('status') != status:
            updates['subscription.status'] = status
            needs_update = True
            print(f"✅ Will update status: {subscription.get('status')} -> {status}")
        
        # Update cancelAtPeriodEnd
        if subscription.get('cancelAtPeriodEnd') != cancel_at_period_end:
            updates['subscription.cancelAtPeriodEnd'] = cancel_at_period_end
            needs_update = True
            print(f"✅ Will update cancelAtPeriodEnd: {subscription.get('cancelAtPeriodEnd')} -> {cancel_at_period_end}")
        
        # Clean up legacy fields (optional - can be done separately)
        legacy_updates = {}
        if 'tier' in subscription:
            legacy_updates['subscription.tier'] = firestore.DELETE_FIELD
            needs_update = True
            print(f"✅ Will remove legacy 'tier' field")
        
        if 'openai_flatlays_used' in subscription:
            legacy_updates['subscription.openai_flatlays_used'] = firestore.DELETE_FIELD
            needs_update = True
            print(f"✅ Will remove legacy 'openai_flatlays_used' field")
        
        if 'flatlay_week_start' in subscription:
            legacy_updates['subscription.flatlay_week_start'] = firestore.DELETE_FIELD
            needs_update = True
            print(f"✅ Will remove legacy 'flatlay_week_start' field")
        
        if needs_update:
            if dry_run:
                print(f"\n🔍 DRY RUN: Would update user {user_id} with:")
                for key, value in {**updates, **legacy_updates}.items():
                    print(f"   {key}: {value}")
                return True
            else:
                # Apply all updates
                all_updates = {**updates, **legacy_updates}
                all_updates['subscription.last_updated'] = firestore.SERVER_TIMESTAMP
                user_ref.update(all_updates)
                print(f"\n✅ Updated user {user_id} subscription data")
                return True
        else:
            print(f"\n✅ No updates needed for user {user_id}")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing subscription for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix subscription data for users')
    parser.add_argument('--user-id', type=str, help='Specific user ID to fix')
    parser.add_argument('--all', action='store_true', help='Fix all users with subscriptions')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run (default: True)')
    parser.add_argument('--execute', action='store_true', help='Actually execute updates (overrides --dry-run)')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if args.user_id:
        # Fix specific user
        fix_user_subscription(args.user_id, dry_run=dry_run)
    elif args.all:
        # Find all users with Stripe subscriptions
        print("🔍 Finding all users with Stripe subscriptions...")
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        fixed_count = 0
        error_count = 0
        
        for user_doc in users:
            user_data = user_doc.to_dict() or {}
            subscription = user_data.get('subscription', {})
            
            if subscription.get('stripeSubscriptionId'):
                if fix_user_subscription(user_doc.id, dry_run=dry_run):
                    fixed_count += 1
                else:
                    error_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   Fixed: {fixed_count}")
        print(f"   Errors: {error_count}")
    else:
        parser.print_help()
        print("\n💡 Example usage:")
        print("   # Dry run for specific user:")
        print("   python fix_subscription_data.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3")
        print("\n   # Actually fix specific user:")
        print("   python fix_subscription_data.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3 --execute")
        print("\n   # Dry run for all users:")
        print("   python fix_subscription_data.py --all")
        print("\n   # Fix all users:")
        print("   python fix_subscription_data.py --all --execute")


if __name__ == '__main__':
    main()

