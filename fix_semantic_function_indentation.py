#!/usr/bin/env python3
"""
Script to fix indentation issues in the _is_semantically_appropriate function in outfits.py.
"""

import re

def fix_semantic_function_indentation():
    """Fix indentation issues in the _is_semantically_appropriate function."""
    file_path = "backend/src/routes/outfits.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the _is_semantically_appropriate function and fix indentation issues
    # Pattern to match elif/if statements with comments but no indented content
    pattern = r'(\s+)(elif|if)\s+.*:\s*\n(\s+)#\s+.*\n(\s+)([a-zA-Z_][a-zA-Z0-9_]*.*)'
    
    def fix_match(match):
        indent = match.group(1)
        control = match.group(2)
        comment_indent = match.group(3)
        code_indent = match.group(4)
        code = match.group(5)
        
        # Fix the indentation
        fixed_comment = indent + '    ' + match.group(0).split('#')[1].strip()
        fixed_code = indent + '    ' + code
        
        return f"{match.group(1)}{match.group(2)}{match.group(0).split(':')[1].split('#')[0]}:\n{fixed_comment}\n{fixed_code}"
    
    # Apply the fix
    fixed_content = re.sub(pattern, fix_match, content, flags=re.MULTILINE)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed indentation issues in _is_semantically_appropriate function")

def main():
    """Main function."""
    print("🔍 Fixing indentation issues in _is_semantically_appropriate function...")
    
    try:
        fix_semantic_function_indentation()
        print("✅ Successfully fixed indentation issues")
    except Exception as e:
        print(f"❌ Error fixing indentation: {e}")

if __name__ == "__main__":
    main()

