#!/usr/bin/env python3
"""
Comprehensive script to fix ALL remaining IndentationErrors in outfits.py
"""

import re
import os

def fix_indentation_errors(file_path):
    """Fix all remaining IndentationErrors in a Python file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # Check for control structures that might have empty blocks
        if re.match(r'^\s*(if|elif|else|for|while|try|except|finally|with|def|class)\s+.*:\s*$', line.strip()):
            # This is a control structure that should have indented content
            current_indent = len(line) - len(line.lstrip())
            expected_indent = current_indent + 4
            
            # Look ahead to see if the next non-empty line is properly indented
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                fixed_lines.append(lines[j])
                j += 1
            
            if j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If the next line is not properly indented, it's likely an IndentationError
                if next_line.strip() and next_indent <= current_indent:
                    # This is likely an IndentationError - the next line should be indented
                    # Check if it's a comment or code
                    if next_line.strip().startswith('#'):
                        # It's a comment - indent it properly
                        fixed_lines.append(' ' * expected_indent + next_line.lstrip())
                        j += 1
                    else:
                        # It's code - indent it properly
                        fixed_lines.append(' ' * expected_indent + next_line.lstrip())
                        j += 1
                    
                    # Continue processing the rest of the indented block
                    while j < len(lines):
                        current_line = lines[j]
                        if not current_line.strip():  # Empty line
                            fixed_lines.append(current_line)
                            j += 1
                            continue
                        
                        current_indent = len(current_line) - len(current_line.lstrip())
                        
                        # If this line is at the same level as the control structure, we're done with the block
                        if current_indent <= current_indent:
                            break
                        
                        # If this line is indented but not enough, fix it
                        if current_indent < expected_indent:
                            fixed_lines.append(' ' * expected_indent + current_line.lstrip())
                        else:
                            fixed_lines.append(current_line)
                        j += 1
                    
                    i = j - 1  # -1 because the loop will increment i
        
        i += 1
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed indentation errors in {file_path}")

def main():
    """Main function to fix all remaining IndentationErrors"""
    
    files_to_fix = [
        'backend/src/routes/outfits.py',
        'backend/src/services/wardrobe_analysis_service.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"🔧 Fixing indentation errors in {file_path}...")
            fix_indentation_errors(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("✅ All indentation errors fixed!")

if __name__ == "__main__":
    main()

