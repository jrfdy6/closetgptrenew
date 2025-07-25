#!/usr/bin/env python3
"""
Migration script to add user_id to existing outfits that don't have it.
This script will:
1. Find all outfits without user_id
2. Try to determine user_id from other fields or context
3. Update the outfits with the appropriate user_id
4. Report on the migration results
"""

import asyncio
import sys
import os
import time
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_service import OutfitService
from src.config.firebase import db

class OutfitMigrationService:
    def __init__(self):
        self.outfit_service = OutfitService()
        self.migration_stats = {
            'total_outfits': 0,
            'outfits_with_user_id': 0,
            'outfits_without_user_id': 0,
            'outfits_migrated': 0,
            'outfits_failed': 0,
            'errors': []
        }
    
    async def analyze_existing_outfits(self):
        """Analyze all existing outfits to see which ones need migration."""
        print("🔍 Analyzing existing outfits...")
        
        try:
            # Get all outfits
            all_outfits = await self.outfit_service.get_outfits()
            self.migration_stats['total_outfits'] = len(all_outfits)
            
            outfits_with_user_id = []
            outfits_without_user_id = []
            
            for outfit in all_outfits:
                outfit_dict = outfit.dict()
                if outfit_dict.get('user_id'):
                    outfits_with_user_id.append(outfit)
                else:
                    outfits_without_user_id.append(outfit)
            
            self.migration_stats['outfits_with_user_id'] = len(outfits_with_user_id)
            self.migration_stats['outfits_without_user_id'] = len(outfits_without_user_id)
            
            print(f"📊 Analysis Results:")
            print(f"   - Total outfits: {self.migration_stats['total_outfits']}")
            print(f"   - Outfits with user_id: {self.migration_stats['outfits_with_user_id']}")
            print(f"   - Outfits without user_id: {self.migration_stats['outfits_without_user_id']}")
            
            return outfits_without_user_id
            
        except Exception as e:
            print(f"❌ Error analyzing outfits: {e}")
            self.migration_stats['errors'].append(f"Analysis error: {e}")
            return []
    
    def determine_user_id_from_context(self, outfit_dict):
        """Try to determine user_id from outfit context."""
        # Method 1: Check user_session_context
        if 'user_session_context' in outfit_dict:
            user_context = outfit_dict['user_session_context']
            if isinstance(user_context, dict) and 'user_id' in user_context:
                return user_context['user_id']
        
        # Method 2: Check wardrobe_snapshot
        if 'wardrobe_snapshot' in outfit_dict:
            wardrobe_snapshot = outfit_dict['wardrobe_snapshot']
            if isinstance(wardrobe_snapshot, dict) and 'user_id' in wardrobe_snapshot:
                return wardrobe_snapshot['user_id']
        
        # Method 3: Check items for userId
        if 'items' in outfit_dict and isinstance(outfit_dict['items'], list):
            for item in outfit_dict['items']:
                if isinstance(item, dict) and 'userId' in item:
                    return item['userId']
        
        # Method 4: Check generation_trace for user_id
        if 'generation_trace' in outfit_dict and isinstance(outfit_dict['generation_trace'], list):
            for trace in outfit_dict['generation_trace']:
                if isinstance(trace, dict):
                    # Check params
                    if 'params' in trace and isinstance(trace['params'], dict):
                        if 'user_id' in trace['params']:
                            return trace['params']['user_id']
                    
                    # Check result
                    if 'result' in trace and isinstance(trace['result'], dict):
                        if 'user_id' in trace['result']:
                            return trace['result']['user_id']
        
        return None
    
    async def migrate_outfit(self, outfit):
        """Migrate a single outfit by adding user_id."""
        try:
            outfit_dict = outfit.dict()
            outfit_id = outfit_dict['id']
            
            print(f"🔄 Migrating outfit {outfit_id}...")
            
            # Try to determine user_id from context
            user_id = self.determine_user_id_from_context(outfit_dict)
            
            if user_id:
                print(f"   - Found user_id: {user_id}")
                
                # Update the outfit with user_id
                outfit_dict['user_id'] = user_id
                
                # Save back to Firestore
                doc_ref = self.outfit_service.collection.document(outfit_id)
                firestore_data = self.outfit_service.to_dict_recursive(outfit_dict)
                doc_ref.set(firestore_data)
                
                print(f"   - ✅ Successfully migrated outfit {outfit_id}")
                self.migration_stats['outfits_migrated'] += 1
                return True
            else:
                print(f"   - ❌ Could not determine user_id for outfit {outfit_id}")
                self.migration_stats['outfits_failed'] += 1
                return False
                
        except Exception as e:
            print(f"   - ❌ Error migrating outfit {outfit_id}: {e}")
            self.migration_stats['errors'].append(f"Migration error for {outfit_id}: {e}")
            self.migration_stats['outfits_failed'] += 1
            return False
    
    async def migrate_all_outfits(self):
        """Migrate all outfits that don't have user_id."""
        print("🚀 Starting outfit migration...")
        
        # Analyze existing outfits
        outfits_to_migrate = await self.analyze_existing_outfits()
        
        if not outfits_to_migrate:
            print("✅ No outfits need migration!")
            return
        
        print(f"\n🔄 Migrating {len(outfits_to_migrate)} outfits...")
        
        # Migrate outfits in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(outfits_to_migrate), batch_size):
            batch = outfits_to_migrate[i:i + batch_size]
            print(f"\n📦 Processing batch {i//batch_size + 1}/{(len(outfits_to_migrate) + batch_size - 1)//batch_size}")
            
            for outfit in batch:
                await self.migrate_outfit(outfit)
                # Small delay to avoid overwhelming Firestore
                await asyncio.sleep(0.1)
        
        # Print final results
        self.print_migration_results()
    
    def print_migration_results(self):
        """Print the final migration results."""
        print(f"\n📊 Migration Results:")
        print(f"   - Total outfits: {self.migration_stats['total_outfits']}")
        print(f"   - Outfits with user_id (before): {self.migration_stats['outfits_with_user_id']}")
        print(f"   - Outfits without user_id: {self.migration_stats['outfits_without_user_id']}")
        print(f"   - Successfully migrated: {self.migration_stats['outfits_migrated']}")
        print(f"   - Failed to migrate: {self.migration_stats['outfits_failed']}")
        
        if self.migration_stats['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.migration_stats['errors'][:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.migration_stats['errors']) > 10:
                print(f"   - ... and {len(self.migration_stats['errors']) - 10} more errors")
        
        # Calculate success rate
        if self.migration_stats['outfits_without_user_id'] > 0:
            success_rate = (self.migration_stats['outfits_migrated'] / self.migration_stats['outfits_without_user_id']) * 100
            print(f"\n🎯 Success rate: {success_rate:.1f}%")
        
        if self.migration_stats['outfits_migrated'] > 0:
            print(f"✅ Migration completed successfully!")
        else:
            print(f"⚠️ No outfits were migrated. Check the errors above.")

async def main():
    """Main migration function."""
    migration_service = OutfitMigrationService()
    
    try:
        await migration_service.migrate_all_outfits()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 