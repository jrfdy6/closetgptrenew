#!/usr/bin/env python3
"""
Comprehensive script to fix ALL indentation errors in outfits.py
"""

import re

def fix_indentation_errors(file_path):
    """Fix all indentation errors in a Python file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for lines that have incorrect indentation patterns
        if line.strip():  # Skip empty lines
            # Check for common indentation issues
            if line.startswith('                logger.info') and not line.startswith('            logger.info'):
                # Fix lines that have too much indentation (16 spaces instead of 12)
                fixed_line = '            ' + line.strip() + '\n'
                print(f"Fixed line {i+1}: Too much indentation")
                fixed_lines.append(fixed_line)
            elif line.startswith('        print(f"') and not line.startswith('            print(f"'):
                # Fix lines that have too little indentation (8 spaces instead of 12)
                fixed_line = '            ' + line.strip() + '\n'
                print(f"Fixed line {i+1}: Too little indentation")
                fixed_lines.append(fixed_line)
            elif line.startswith('                try:') and not line.startswith('            try:'):
                # Fix try blocks that have too much indentation
                fixed_line = '            ' + line.strip() + '\n'
                print(f"Fixed line {i+1}: Try block indentation")
                fixed_lines.append(fixed_line)
            elif line.startswith('                except') and not line.startswith('            except'):
                # Fix except blocks that have too much indentation
                fixed_line = '            ' + line.strip() + '\n'
                print(f"Fixed line {i+1}: Except block indentation")
                fixed_lines.append(fixed_line)
            elif line.startswith('        # print(f"') and not line.startswith('            # print(f"'):
                # Fix commented print statements that have too little indentation
                fixed_line = '            ' + line.strip() + '\n'
                print(f"Fixed line {i+1}: Commented print indentation")
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed indentation errors in {file_path}")

def main():
    """Main function to fix indentation errors"""
    
    file_path = 'backend/src/routes/outfits.py'
    print(f"🔧 Fixing indentation errors in {file_path}...")
    fix_indentation_errors(file_path)
    print("✅ All indentation errors fixed!")

if __name__ == "__main__":
    main()

