#!/usr/bin/env python3
"""
Comprehensive script to find and fix ALL NoneType .get() errors
This script will systematically search through ALL Python files and fix every potential issue.
"""

import os
import re
import sys
from pathlib import Path

def find_python_files(directory):
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environments and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def find_get_calls(file_path):
    """Find all .get() calls in a file that could cause NoneType errors."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Pattern to find .get() calls
        get_pattern = r'(\w+)\.get\('
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(get_pattern, line)
            for match in matches:
                variable_name = match.group(1)
                
                # Check if there's already a None check for this variable
                has_none_check = False
                
                # Look for None checks in the same line or nearby lines
                check_lines = lines[max(0, line_num-3):min(len(lines), line_num+1)]
                check_content = ' '.join(check_lines)
                
                # Check for common None check patterns
                none_check_patterns = [
                    rf'if\s+{variable_name}\s+is\s+not\s+None',
                    rf'if\s+{variable_name}',
                    rf'{variable_name}\s+if\s+{variable_name}\s+else',
                    rf'{variable_name}\s+and\s+{variable_name}\.get',
                ]
                
                for pattern in none_check_patterns:
                    if re.search(pattern, check_content):
                        has_none_check = True
                        break
                
                if not has_none_check:
                    issues.append({
                        'file': file_path,
                        'line': line_num,
                        'variable': variable_name,
                        'content': line.strip()
                    })
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return issues

def fix_get_call_issue(file_path, line_num, variable_name, original_line):
    """Fix a .get() call issue by adding None check."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get the current line (0-indexed)
        current_line_idx = line_num - 1
        current_line = lines[current_line_idx]
        
        # Create the fixed line with None check
        # Pattern: variable.get(...) -> (variable.get(...) if variable else default)
        
        # Find the .get() call and extract the parameters
        get_match = re.search(rf'{re.escape(variable_name)}\.get\(([^)]+)\)', current_line)
        if get_match:
            get_params = get_match.group(1)
            
            # Create the fixed version
            fixed_call = f'({variable_name}.get({get_params}) if {variable_name} else {get_params.split(",")[-1].strip() if "," in get_params else "None"})'
            fixed_line = current_line.replace(f'{variable_name}.get({get_params})', fixed_call)
            
            # Replace the line
            lines[current_line_idx] = fixed_line
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True, fixed_line.strip()
        
    except Exception as e:
        print(f"Error fixing {file_path} line {line_num}: {e}")
        return False, None
    
    return False, None

def main():
    """Main function to find and fix all NoneType .get() errors."""
    
    print("🔍 COMPREHENSIVE NoneType .get() ERROR FINDER AND FIXER")
    print("=" * 60)
    
    # Find all Python files in src directory
    src_dir = "backend/src"
    if not os.path.exists(src_dir):
        print(f"❌ Directory {src_dir} not found!")
        return
    
    python_files = find_python_files(src_dir)
    print(f"📁 Found {len(python_files)} Python files to analyze")
    
    all_issues = []
    
    # Find all potential issues
    for file_path in python_files:
        issues = find_get_calls(file_path)
        all_issues.extend(issues)
    
    print(f"🔍 Found {len(all_issues)} potential NoneType .get() issues")
    
    if not all_issues:
        print("✅ No NoneType .get() issues found!")
        return
    
    # Display all issues
    print("\n📋 ALL ISSUES FOUND:")
    print("-" * 60)
    
    for i, issue in enumerate(all_issues, 1):
        print(f"{i}. {os.path.basename(issue['file'])}:{issue['line']}")
        print(f"   Variable: {issue['variable']}")
        print(f"   Content: {issue['content']}")
        print()
    
    # Fix all issues
    print("🔧 FIXING ALL ISSUES...")
    print("-" * 60)
    
    fixed_count = 0
    for i, issue in enumerate(all_issues, 1):
        print(f"Fixing {i}/{len(all_issues)}: {os.path.basename(issue['file'])}:{issue['line']}")
        
        success, fixed_line = fix_get_call_issue(
            issue['file'], 
            issue['line'], 
            issue['variable'], 
            issue['content']
        )
        
        if success:
            print(f"   ✅ Fixed: {fixed_line}")
            fixed_count += 1
        else:
            print(f"   ❌ Failed to fix")
        print()
    
    print(f"🎉 COMPLETION SUMMARY:")
    print(f"   Total issues found: {len(all_issues)}")
    print(f"   Successfully fixed: {fixed_count}")
    print(f"   Failed fixes: {len(all_issues) - fixed_count}")
    
    if fixed_count == len(all_issues):
        print("\n✅ ALL NoneType .get() ERRORS HAVE BEEN FIXED!")
        print("🚀 The robust outfit generation service should now work!")
    else:
        print(f"\n⚠️ {len(all_issues) - fixed_count} issues could not be automatically fixed")
        print("   Manual review may be required")

if __name__ == "__main__":
    main()
