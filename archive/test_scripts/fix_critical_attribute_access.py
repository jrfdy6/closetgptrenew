#!/usr/bin/env python3
"""
Fix the most critical attribute access patterns that could cause NoneType errors
Focus on the patterns most likely to be causing the current robust service error
"""

import re

def fix_critical_attribute_access():
    """Fix critical attribute access patterns in the most important files."""
    
    # Focus on the most critical files and patterns
    critical_fixes = [
        {
            'file': 'backend/src/services/robust_outfit_generation_service.py',
            'patterns': [
                # item.name access
                (r'(\s+)(item\.name)', r'\1(item.name if item else "Unknown")'),
                # context.occasion access  
                (r'(\s+)(context\.occasion)', r'\1(context.occasion if context else "unknown")'),
                (r'(\s+)(context\.style)', r'\1(context.style if context else "unknown")'),
                (r'(\s+)(context\.mood)', r'\1(context.mood if context else "unknown")'),
                (r'(\s+)(context\.user_id)', r'\1(context.user_id if context else "unknown")'),
                (r'(\s+)(context\.wardrobe)', r'\1(context.wardrobe if context else [])'),
                (r'(\s+)(context\.weather)', r'\1(context.weather if context else None)'),
            ]
        },
        {
            'file': 'backend/src/routes/outfits.py',
            'patterns': [
                # req attribute access
                (r'(\s+)(req\.occasion)', r'\1(req.occasion if req else "unknown")'),
                (r'(\s+)(req\.style)', r'\1(req.style if req else "unknown")'),
                (r'(\s+)(req\.mood)', r'\1(req.mood if req else "unknown")'),
                (r'(\s+)(req\.wardrobe)', r'\1(req.wardrobe if req else [])'),
                (r'(\s+)(req\.weather)', r'\1(req.weather if req else None)'),
                (r'(\s+)(req\.baseItemId)', r'\1(req.baseItemId if req else None)'),
            ]
        }
    ]
    
    total_fixed = 0
    
    for fix_config in critical_fixes:
        file_path = fix_config['file']
        patterns = fix_config['patterns']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_fixed_count = 0
            
            for pattern, replacement in patterns:
                # Count matches before replacement
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    file_fixed_count += len(matches)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed {file_fixed_count} critical attribute access patterns in {file_path}")
                total_fixed += file_fixed_count
            else:
                print(f"ℹ️ No critical attribute access patterns found in {file_path}")
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    return total_fixed

def main():
    print("🔧 FIXING CRITICAL ATTRIBUTE ACCESS PATTERNS")
    print("=" * 60)
    
    fixed_count = fix_critical_attribute_access()
    
    print(f"\n🎉 Fixed {fixed_count} critical attribute access patterns!")
    if fixed_count > 0:
        print("🚀 The robust service should now work without NoneType attribute errors!")
    else:
        print("ℹ️ No critical attribute access patterns were found to fix")

if __name__ == "__main__":
    main()
