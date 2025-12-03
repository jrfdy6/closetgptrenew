#!/usr/bin/env python3
"""
Fix the remaining Firebase document reference .get() calls
"""

import re

def fix_firebase_calls_in_file(file_path, patterns):
    """Fix Firebase document reference .get() calls in a specific file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Check if any changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed Firebase .get() calls in {file_path}")
            return True
        else:
            print(f"ℹ️ No Firebase .get() calls found in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing Firebase .get() calls in {file_path}: {e}")
        return False

def main():
    print("🔧 FIXING REMAINING FIREBASE DOCUMENT REFERENCE .get() CALLS")
    print("=" * 60)
    
    # Patterns to fix Firebase document reference .get() calls
    firebase_patterns = [
        # Pattern: item_ref.get()
        (r'(\s+)(item_ref\.get\(\))', r'\1\2 if item_ref else None'),
        
        # Pattern: profile_ref.get()
        (r'(\s+)(profile_ref\.get\(\))', r'\1\2 if profile_ref else None'),
        
        # Pattern: fetch_log_ref.get()
        (r'(\s+)(fetch_log_ref\.get\(\))', r'\1\2 if fetch_log_ref else None'),
        
        # Pattern: daily_ref.get()
        (r'(\s+)(daily_ref\.get\(\))', r'\1\2 if daily_ref else None'),
    ]
    
    # Files to fix
    files_to_fix = [
        "backend/src/services/item_analytics_service.py",
        "backend/src/services/fashion_trends_service.py", 
        "backend/src/services/analytics_service.py"
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        if fix_firebase_calls_in_file(file_path, firebase_patterns):
            fixed_count += 1
    
    print(f"\n🎉 Fixed Firebase .get() calls in {fixed_count} files!")
    print("🚀 The robust service should now work without NoneType errors!")

if __name__ == "__main__":
    main()
