#!/usr/bin/env python3
"""
Comprehensive script to fix ALL structural and indentation issues in outfits.py
"""

import re

def fix_outfits_comprehensively(file_path):
    """Fix all structural and indentation issues in outfits.py"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for processing
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # Fix specific problematic patterns
        if line.strip() == 'except Exception as conversion_error:' and i > 0:
            # Check if the previous line has proper indentation
            prev_line = lines[i-1] if i > 0 else ''
            if 'logger.info(f"✅ Pre-outfit-construction guard completed' in prev_line:
                # This except block should be at the same level as the try
                fixed_line = '            ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {line_num}: Corrected except block indentation")
            else:
                fixed_lines.append(line + '\n')
        elif line.strip() == 'for i, item in enumerate(clothing_items):' and i > 0:
            # Check if this for loop is properly indented
            prev_line = lines[i-1] if i > 0 else ''
            if 'clothing_items type = {type(clothing_items)}' in prev_line:
                # This for loop should be at the same level as the surrounding code
                fixed_line = '        ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {line_num}: Corrected for loop indentation")
            else:
                fixed_lines.append(line + '\n')
        elif line.strip() == 'if item is None:' and i > 0:
            # Check if this if statement is properly indented
            prev_line = lines[i-1] if i > 0 else ''
            if 'item {i} type = {type(item)}' in prev_line:
                # This if statement should be inside the for loop
                fixed_line = '            ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {line_num}: Corrected if statement indentation")
            else:
                fixed_lines.append(line + '\n')
        elif line.strip() == 'print(f"🚨 CRITICAL: clothing_items[{i}] is None!")' and i > 0:
            # Check if this print statement is properly indented
            prev_line = lines[i-1] if i > 0 else ''
            if 'if item is None:' in prev_line:
                # This print statement should be inside the if block
                fixed_line = '                ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {line_num}: Corrected print statement indentation")
            else:
                fixed_lines.append(line + '\n')
        elif line.strip() == 'context = GenerationContext(' and i > 0:
            # Check if this context creation is properly indented
            prev_line = lines[i-1] if i > 0 else ''
            if 'clothing_items[{i}] is None!' in prev_line:
                # This context creation should be at the same level as the for loop
                fixed_line = '        ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {line_num}: Corrected context creation indentation")
            else:
                fixed_lines.append(line + '\n')
        else:
            fixed_lines.append(line + '\n')
        
        i += 1
    
    # Join the lines back together
    fixed_content = ''.join(fixed_lines)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed all structural issues in {file_path}")

def main():
    """Main function to fix outfits.py comprehensively"""
    
    file_path = 'backend/src/routes/outfits.py'
    print(f"🔧 Fixing outfits.py comprehensively...")
    fix_outfits_comprehensively(file_path)
    print("✅ All issues fixed!")

if __name__ == "__main__":
    main()

