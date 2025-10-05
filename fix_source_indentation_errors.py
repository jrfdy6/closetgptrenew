#!/usr/bin/env python3
"""
Targeted script to find and fix IndentationErrors ONLY in our source files,
not in virtual environment or third-party libraries.
"""

import os
import re
import glob

def find_empty_control_structures(file_path):
    """Find empty control structures that cause IndentationErrors."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    errors = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            continue
            
        # Check for control structures that might be empty
        control_patterns = [
            r'^(\s*)(if\s+.*):\s*$',
            r'^(\s*)(for\s+.*):\s*$',
            r'^(\s*)(while\s+.*):\s*$',
            r'^(\s*)(else):\s*$',
            r'^(\s*)(elif\s+.*):\s*$',
            r'^(\s*)(try):\s*$',
            r'^(\s*)(except\s+.*):\s*$',
            r'^(\s*)(finally):\s*$',
            r'^(\s*)(with\s+.*):\s*$',
            r'^(\s*)(def\s+.*):\s*$',
            r'^(\s*)(class\s+.*):\s*$',
        ]
        
        for pattern in control_patterns:
            match = re.match(pattern, stripped)
            if match:
                indent = match.group(1)
                control_keyword = match.group(2)
                
                # Check if the next non-empty line is properly indented
                next_line_idx = i + 1
                found_indented_content = False
                
                while next_line_idx < len(lines):
                    next_line = lines[next_line_idx]
                    next_stripped = next_line.strip()
                    
                    # Skip empty lines
                    if not next_stripped:
                        next_line_idx += 1
                        continue
                    
                    # Check if it's a comment (skip)
                    if next_stripped.startswith('#'):
                        next_line_idx += 1
                        continue
                    
                    # Check if it's properly indented (more indentation than the control structure)
                    if next_line.startswith(indent + '    ') or next_line.startswith(indent + '\t'):
                        found_indented_content = True
                        break
                    
                    # If we find a line with same or less indentation, we've hit the end of the block
                    if next_line.startswith(indent) and not next_line.startswith(indent + ' '):
                        break
                        
                    next_line_idx += 1
                
                if not found_indented_content:
                    errors.append({
                        'file': file_path,
                        'line': line_num,
                        'content': stripped,
                        'indent': indent,
                        'control': control_keyword
                    })
    
    return errors

def fix_indentation_error(error):
    """Fix a single indentation error by adding a pass statement."""
    file_path = error['file']
    line_num = error['line']
    indent = error['indent']
    control = error['control']
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Insert a pass statement after the control structure
    pass_line = indent + '    pass  # Fixed empty control structure\n'
    
    # Find the right place to insert the pass statement
    insert_idx = line_num  # Insert after the current line
    
    lines.insert(insert_idx, pass_line)
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Fixed {control} on line {line_num} in {file_path}")

def main():
    """Main function to find and fix all IndentationErrors in source files only."""
    print("🔍 Searching for empty control structures in source files only...")
    
    # Find all Python files in the backend source directory (exclude virtual environments)
    python_files = glob.glob("backend/src/**/*.py", recursive=True)
    
    total_errors = 0
    fixed_files = set()
    
    for file_path in python_files:
        try:
            errors = find_empty_control_structures(file_path)
            if errors:
                print(f"\n📁 {file_path}: Found {len(errors)} empty control structures")
                for error in errors:
                    print(f"  - Line {error['line']}: {error['content']}")
                    fix_indentation_error(error)
                    total_errors += 1
                    fixed_files.add(file_path)
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n✅ Summary:")
    print(f"  - Total errors fixed: {total_errors}")
    print(f"  - Files modified: {len(fixed_files)}")
    
    if fixed_files:
        print(f"\n📝 Source files that were fixed:")
        for file_path in sorted(fixed_files):
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()

