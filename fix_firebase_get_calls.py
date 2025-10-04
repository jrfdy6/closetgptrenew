#!/usr/bin/env python3
"""
Fix Firebase document reference .get() calls that can cause NoneType errors
"""

import re

def fix_firebase_get_calls():
    """Fix all Firebase document reference .get() calls in outfits.py"""
    
    file_path = "backend/src/routes/outfits.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns to fix Firebase document reference .get() calls
        patterns_to_fix = [
            # Pattern: wardrobe_ref.get()
            (r'(\s+)(wardrobe_ref\.get\(\))', r'\1\2 if wardrobe_ref else None'),
            
            # Pattern: profile_ref.get()
            (r'(\s+)(profile_ref\.get\(\))', r'\1\2 if profile_ref else None'),
            
            # Pattern: doc_ref.get()
            (r'(\s+)(doc_ref\.get\(\))', r'\1\2 if doc_ref else None'),
            
            # Pattern: outfit_ref.get()
            (r'(\s+)(outfit_ref\.get\(\))', r'\1\2 if outfit_ref else None'),
            
            # Pattern: analytics_ref.get()
            (r'(\s+)(analytics_ref\.get\(\))', r'\1\2 if analytics_ref else None'),
            
            # Pattern: item_ref.get()
            (r'(\s+)(item_ref\.get\(\))', r'\1\2 if item_ref else None'),
            
            # Pattern: stats_ref.get()
            (r'(\s+)(stats_ref\.get\(\))', r'\1\2 if stats_ref else None'),
        ]
        
        original_content = content
        
        for pattern, replacement in patterns_to_fix:
            content = re.sub(pattern, replacement, content)
        
        # Check if any changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed Firebase document reference .get() calls")
            return True
        else:
            print("ℹ️ No Firebase document reference .get() calls found to fix")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing Firebase .get() calls: {e}")
        return False

def main():
    print("🔧 FIXING FIREBASE DOCUMENT REFERENCE .get() CALLS")
    print("=" * 60)
    
    success = fix_firebase_get_calls()
    
    if success:
        print("\n🎉 Firebase document reference .get() calls have been fixed!")
        print("🚀 The robust service should now work without NoneType errors!")
    else:
        print("\n⚠️ No Firebase .get() calls were found to fix")

if __name__ == "__main__":
    main()
