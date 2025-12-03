#!/usr/bin/env python3
"""
Script to fix unexpected indent errors in outfits.py.
This script will find lines that start with extra spaces and fix them.
"""

import re

def fix_unexpected_indents():
    """Fix unexpected indent errors in outfits.py."""
    file_path = "backend/src/routes/outfits.py"
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed_count = 0
    
    for i, line in enumerate(lines):
        # Check if line starts with extra spaces (more than expected)
        if re.match(r'^        \s+', line):  # Line starts with 8+ spaces (should be 4 or 8)
            # Find the correct indentation by looking at surrounding lines
            line_num = i + 1
            
            # Look at previous non-empty line to determine correct indentation
            prev_line_idx = i - 1
            while prev_line_idx >= 0 and not lines[prev_line_idx].strip():
                prev_line_idx -= 1
            
            if prev_line_idx >= 0:
                prev_line = lines[prev_line_idx]
                # Count leading spaces in previous line
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                
                # Fix the current line by using the same indentation as previous line
                stripped_content = line.strip()
                fixed_line = ' ' * prev_indent + stripped_content + '\n'
                
                print(f"Fixed line {line_num}: '{line.strip()}' -> '{fixed_line.strip()}'")
                lines[i] = fixed_line
                fixed_count += 1
    
    # Write the fixed content back to the file
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print(f"\n✅ Fixed {fixed_count} unexpected indent errors")
    return fixed_count

def main():
    """Main function to fix unexpected indent errors."""
    print("🔍 Finding and fixing unexpected indent errors in outfits.py...")
    
    try:
        fixed_count = fix_unexpected_indents()
        
        if fixed_count > 0:
            print(f"\n✅ Successfully fixed {fixed_count} unexpected indent errors")
        else:
            print("\n✅ No unexpected indent errors found")
            
    except Exception as e:
        print(f"❌ Error fixing unexpected indents: {e}")

if __name__ == "__main__":
    main()

