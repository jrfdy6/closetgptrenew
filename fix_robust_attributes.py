#!/usr/bin/env python3
"""
Script to fix all remaining unsafe attribute accesses in the robust service.
"""

import re

def fix_robust_service():
    """Fix all unsafe attribute accesses in the robust service."""
    
    file_path = "backend/src/services/robust_outfit_generation_service.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix patterns systematically
    fixes = [
        # Fix item.name references
        (r'item\.name', 'self.safe_get_item_name(item)'),
        
        # Fix item.color references  
        (r'item\.color', 'self.safe_get_item_attr(item, "color", "")'),
        
        # Fix item.temperatureCompatibility
        (r'item\.temperatureCompatibility', 'self.safe_get_item_attr(item, "temperatureCompatibility")'),
        
        # Fix item.id references
        (r'item\.id', 'self.safe_get_item_attr(item, "id", "")'),
        
        # Fix remaining (item.name if item else "Unknown") patterns
        (r'\(item\.name if item else "Unknown"\)', 'self.safe_get_item_name(item)'),
    ]
    
    # Apply fixes
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed all unsafe attribute accesses in robust service")

if __name__ == "__main__":
    fix_robust_service()
