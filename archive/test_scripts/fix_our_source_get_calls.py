#!/usr/bin/env python3
"""
Fix .get() calls in our source files that could cause NoneType errors
Focus only on files in src/ directory
"""

import os
import re

def fix_source_get_calls():
    """Fix .get() calls in our source files only."""
    
    # Only fix files in our src directory
    source_files = [
        "backend/src/routes/outfits.py",
        "backend/src/routes/wardrobe.py", 
        "backend/src/routes/weather.py",
        "backend/src/routes/analytics.py",
        "backend/src/routes/outfit_history.py",
        "backend/src/routes/outfit_service.py",
        "backend/src/routes/wardrobe_analysis_service.py",
        "backend/src/routes/item_analytics.py",
        "backend/src/routes/feedback.py",
        "backend/src/routes/enhanced_feedback.py",
        "backend/src/routes/outfit_generation_service.py",
        "backend/src/routes/wardrobe_simple.py",
        "backend/src/routes/outfit_stats_simple.py",
        "backend/src/routes/outfit_service_backup.py",
        "backend/src/routes/outfit_service_old.py",
        "backend/src/routes/debug_stats.py",
        "backend/src/routes/health.py"
    ]
    
    total_fixed = 0
    
    for file_path in source_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_fixed_count = 0
            
            # Patterns to fix Firebase document reference .get() calls
            patterns_to_fix = [
                # Pattern: doc_ref.get()
                (r'(\s+)(doc_ref\.get\(\))', r'\1\2 if doc_ref else None'),
                
                # Pattern: outfit_ref.get()
                (r'(\s+)(outfit_ref\.get\(\))', r'\1\2 if outfit_ref else None'),
                
                # Pattern: item_ref.get()
                (r'(\s+)(item_ref\.get\(\))', r'\1\2 if item_ref else None'),
                
                # Pattern: wardrobe_ref.get()
                (r'(\s+)(wardrobe_ref\.get\(\))', r'\1\2 if wardrobe_ref else None'),
                
                # Pattern: user_ref.get()
                (r'(\s+)(user_ref\.get\(\))', r'\1\2 if user_ref else None'),
                
                # Pattern: stats_ref.get()
                (r'(\s+)(stats_ref\.get\(\))', r'\1\2 if stats_ref else None'),
                
                # Pattern: suggestion_ref.get()
                (r'(\s+)(suggestion_ref\.get\(\))', r'\1\2 if suggestion_ref else None'),
                
                # Pattern: user_stats_ref.get()
                (r'(\s+)(user_stats_ref\.get\(\))', r'\1\2 if user_stats_ref else None'),
            ]
            
            for pattern, replacement in patterns_to_fix:
                # Count matches before replacement
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    file_fixed_count += len(matches)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed {file_fixed_count} .get() calls in {file_path}")
                total_fixed += file_fixed_count
            else:
                print(f"ℹ️ No .get() calls found to fix in {file_path}")
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    return total_fixed

def main():
    print("🔧 FIXING .get() CALLS IN OUR SOURCE FILES")
    print("=" * 60)
    
    fixed_count = fix_source_get_calls()
    
    print(f"\n🎉 Fixed {fixed_count} .get() calls in our source files!")
    if fixed_count > 0:
        print("🚀 The robust service should now work without NoneType .get() errors!")
    else:
        print("ℹ️ No .get() calls were found to fix in our source files")

if __name__ == "__main__":
    main()
