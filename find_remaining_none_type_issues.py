#!/usr/bin/env python3
"""
Find the remaining 55 unfixed .get() calls that could cause NoneType errors
"""

import os
import re
import sys
from pathlib import Path

def find_complex_get_calls():
    """Find complex .get() calls that the simple fix couldn't handle."""
    
    # Files that had unfixed issues
    target_files = [
        "backend/src/services/item_analytics_service.py",
        "backend/src/services/lightweight_embedding_service.py", 
        "backend/src/services/fashion_trends_service.py",
        "backend/src/services/analytics_service.py"
    ]
    
    all_issues = []
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            print(f"\n🔍 Analyzing: {file_path}")
            
            # Pattern to find .get() calls
            get_pattern = r'(\w+)\.get\('
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(get_pattern, line)
                for match in matches:
                    variable_name = match.group(1)
                    
                    # Skip obvious safe cases
                    if variable_name in ['dict', 'self', 'item', 'outfit', 'context', 'data', 'result']:
                        continue
                    
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
                        rf'\(\s*{variable_name}\s*if\s+{variable_name}\s+else',
                    ]
                    
                    for pattern in none_check_patterns:
                        if re.search(pattern, check_content):
                            has_none_check = True
                            break
                    
                    if not has_none_check:
                        issue = {
                            'file': file_path,
                            'line': line_num,
                            'variable': variable_name,
                            'content': line.strip()
                        }
                        all_issues.append(issue)
                        print(f"  ❌ Line {line_num}: {variable_name}.get() - {line.strip()[:80]}...")
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return all_issues

def find_chained_get_calls():
    """Find chained .get() calls that could cause issues."""
    
    # Look for patterns like: obj.get('key').get('nested_key')
    pattern = r'(\w+)\.get\([^)]+\)\.get\('
    
    target_files = [
        "backend/src/services/robust_outfit_generation_service.py",
        "backend/src/services/robust_hydrator.py",
        "backend/src/routes/outfits.py"
    ]
    
    all_issues = []
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            print(f"\n🔍 Checking chained .get() calls in: {file_path}")
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line)
                for match in matches:
                    variable_name = match.group(1)
                    
                    issue = {
                        'file': file_path,
                        'line': line_num,
                        'variable': variable_name,
                        'content': line.strip(),
                        'type': 'chained_get'
                    }
                    all_issues.append(issue)
                    print(f"  ❌ Line {line_num}: Chained .get() call - {line.strip()[:80]}...")
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return all_issues

def main():
    print("🔍 FINDING REMAINING NoneType .get() ISSUES")
    print("=" * 60)
    
    print("\n1️⃣ Looking for complex .get() calls...")
    complex_issues = find_complex_get_calls()
    
    print("\n2️⃣ Looking for chained .get() calls...")
    chained_issues = find_chained_get_calls()
    
    all_issues = complex_issues + chained_issues
    
    print(f"\n📊 RESULTS:")
    print(f"   Complex .get() issues: {len(complex_issues)}")
    print(f"   Chained .get() issues: {len(chained_issues)}")
    print(f"   Total issues: {len(all_issues)}")
    
    if all_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND:")
        print("-" * 60)
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {os.path.basename(issue['file'])}:{issue['line']}")
            print(f"   Variable: {issue['variable']}")
            print(f"   Type: {issue.get('type', 'simple')}")
            print(f"   Content: {issue['content']}")
            print()
    else:
        print("\n✅ No obvious remaining NoneType .get() issues found!")
    
    print("\n🔧 NEXT STEPS:")
    if all_issues:
        print("1. These are the most likely remaining candidates")
        print("2. Add None checks or use safe access patterns")
        print("3. Test the robust service again")
    else:
        print("1. The issue might be in a different pattern")
        print("2. Check for attribute access on None objects")
        print("3. Look for method calls on None objects")

if __name__ == "__main__":
    main()
