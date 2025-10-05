#!/usr/bin/env python3
"""
Fix indentation errors in wardrobe_analysis.py
"""

import re

def fix_indentation_errors(file_path):
    """Fix indentation errors in the file."""
    print(f"🔧 Fixing indentation errors in {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix empty else blocks
    content = re.sub(r'(\s+)else:\s*\n(\s*)#\s*print.*\n(\s+)except', r'\1else:\n\2# print statement\n\2pass\n\3except', content)
    
    # Fix empty except blocks
    content = re.sub(r'(\s+)except.*:\s*\n(\s*)#\s*print.*\n(\s+)(?=\n|\s*[a-zA-Z])', r'\1except Exception as e:\n\2# print statement\n\2pass\n\3', content)
    
    # Fix any remaining empty else blocks
    content = re.sub(r'(\s+)else:\s*\n(\s*)(?=\n|\s*[a-zA-Z])', r'\1else:\n\2pass\n', content)
    
    # Fix any remaining empty except blocks
    content = re.sub(r'(\s+)except.*:\s*\n(\s*)(?=\n|\s*[a-zA-Z])', r'\1except Exception as e:\n\2pass\n', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed indentation errors in {file_path}")

if __name__ == "__main__":
    fix_indentation_errors("src/routes/wardrobe_analysis.py")
