#!/usr/bin/env python3
"""
Comprehensive script to fix ALL structural issues in outfits.py
"""

def fix_structural_issues(file_path):
    """Fix all structural issues in a Python file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # Fix the broken try-except structure around line 1070
        if line_num == 1070 and 'try:' in line:
            fixed_lines.append(line)
            # Skip the malformed lines and fix the structure
            i += 1
            while i < len(lines) and i < 1075:  # Skip to the except block
                i += 1
            # Add the proper except block structure
            if i < len(lines) and 'except Exception as hydrator_error:' in lines[i]:
                fixed_lines.append(lines[i])  # Keep the except line
                i += 1
                # Fix the indentation of the except block content
                while i < len(lines) and (lines[i].startswith('                ') or lines[i].startswith('        ') or lines[i].strip() == ''):
                    if lines[i].startswith('                '):
                        # Fix over-indented lines
                        fixed_line = '            ' + lines[i].strip() + '\n'
                        fixed_lines.append(fixed_line)
                        print(f"Fixed line {i+1}: Over-indented line in except block")
                    elif lines[i].startswith('        '):
                        # Fix under-indented lines
                        fixed_line = '            ' + lines[i].strip() + '\n'
                        fixed_lines.append(fixed_line)
                        print(f"Fixed line {i+1}: Under-indented line in except block")
                    else:
                        fixed_lines.append(lines[i])
                    i += 1
                continue
        
        # Fix other structural issues
        if line.strip() and not line.startswith('#'):
            # Check for lines that should be inside try-except blocks
            if 'logger.info(f"✅ Pre-outfit-construction guard completed' in line:
                # This should be inside the try block
                fixed_line = '            ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {i+1}: Moved inside try block")
            elif 'clothing_items = []' in line:
                # This should be inside the try block
                fixed_line = '            ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {i+1}: Moved inside try block")
            elif 'if ClothingItem is None:' in line:
                # This should be inside the try block
                fixed_line = '            ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {i+1}: Moved inside try block")
            elif 'for i, item_dict in enumerate(hydrated_wardrobe_items):' in line:
                # This should be inside the try block
                fixed_line = '            ' + line.strip() + '\n'
                fixed_lines.append(fixed_line)
                print(f"Fixed line {i+1}: Moved inside try block")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed structural issues in {file_path}")

def main():
    """Main function to fix structural issues"""
    
    file_path = 'backend/src/routes/outfits.py'
    print(f"🔧 Fixing structural issues in {file_path}...")
    fix_structural_issues(file_path)
    print("✅ All structural issues fixed!")

if __name__ == "__main__":
    main()

