#!/usr/bin/env python3
"""
Find the FINAL .get() call causing the NoneType error
This script will look for any .get() call that could still cause issues
"""

import os
import re

def find_all_get_calls():
    """Find ALL .get() calls in the codebase that could cause NoneType errors."""
    
    # Search in all Python files in the backend
    backend_dir = "backend"
    all_get_calls = []
    
    for root, dirs, files in os.walk(backend_dir):
        # Skip cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    # Find all .get() calls
                    get_pattern = r'(\w+)\.get\('
                    
                    for line_num, line in enumerate(lines, 1):
                        matches = re.finditer(get_pattern, line)
                        for match in matches:
                            variable_name = match.group(1)
                            
                            # Skip obvious safe cases
                            if variable_name in ['self', 'dict', 'list', 'str', 'int', 'float', 'bool', 'type']:
                                continue
                            
                            # Skip if it's a class or module (starts with capital)
                            if variable_name[0].isupper():
                                continue
                            
                            # Check if there's already a None check for this variable
                            has_none_check = False
                            
                            # Look for None checks in the same line or nearby lines
                            check_lines = lines[max(0, line_num-5):min(len(lines), line_num+2)]
                            check_content = ' '.join(check_lines)
                            
                            # Check for common None check patterns
                            none_check_patterns = [
                                rf'if\s+{variable_name}\s+is\s+not\s+None',
                                rf'if\s+{variable_name}',
                                rf'{variable_name}\s+if\s+{variable_name}\s+else',
                                rf'{variable_name}\s+and\s+{variable_name}\.get',
                                rf'\(\s*{variable_name}\s*if\s+{variable_name}\s+else',
                            ]
                            
                            for pattern in none_check_patterns:
                                if re.search(pattern, check_content):
                                    has_none_check = True
                                    break
                            
                            if not has_none_check:
                                get_call = {
                                    'file': file_path,
                                    'line': line_num,
                                    'variable': variable_name,
                                    'content': line.strip()
                                }
                                all_get_calls.append(get_call)
                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return all_get_calls

def main():
    print("🔍 FINDING THE FINAL .get() CALL CAUSING NoneType ERROR")
    print("=" * 60)
    
    get_calls = find_all_get_calls()
    
    print(f"\n📊 FOUND {len(get_calls)} POTENTIAL ISSUES:")
    print("-" * 60)
    
    if get_calls:
        # Group by file for easier reading
        by_file = {}
        for call in get_calls:
            file_name = os.path.basename(call['file'])
            if file_name not in by_file:
                by_file[file_name] = []
            by_file[file_name].append(call)
        
        for file_name, calls in by_file.items():
            print(f"\n📁 {file_name} ({len(calls)} issues):")
            for i, call in enumerate(calls[:10], 1):  # Show first 10 per file
                print(f"  {i}. Line {call['line']}: {call['variable']}.get() - {call['content'][:60]}...")
            
            if len(calls) > 10:
                print(f"  ... and {len(calls) - 10} more")
    else:
        print("\n✅ No .get() calls found without None checks!")
    
    print(f"\n🔧 NEXT STEPS:")
    if get_calls:
        print("1. These are the remaining .get() calls that could cause NoneType errors")
        print("2. Add None checks before each .get() call")
        print("3. Focus on the files with the most issues first")
    else:
        print("1. The issue might not be a .get() call")
        print("2. Check for other attribute access patterns")
        print("3. Look for method calls on None objects")

if __name__ == "__main__":
    main()
