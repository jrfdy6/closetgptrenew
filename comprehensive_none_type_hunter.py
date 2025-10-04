#!/usr/bin/env python3
"""
Comprehensive script to find ALL possible NoneType errors, not just .get() calls
"""

import os
import re
import sys
from pathlib import Path

def find_all_dot_calls():
    """Find ALL .method() calls that could cause NoneType errors."""
    
    # Target files most likely to be involved in robust service execution
    target_files = [
        "backend/src/services/robust_outfit_generation_service.py",
        "backend/src/services/robust_hydrator.py", 
        "backend/src/routes/outfits.py",
        "backend/src/services/outfit_filtering_service.py",
        "backend/src/services/validation_orchestrator.py",
        "backend/src/services/outfit_validation_service.py",
        "backend/src/services/enhanced_outfit_validator.py",
        "backend/src/services/compatibility_matrix.py",
        "backend/src/services/diversity_filter_service.py",
        "backend/src/services/wardrobe_preprocessor.py",
        "backend/src/services/cohesive_outfit_composition_service.py"
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
            
            # Pattern to find any .method() calls
            dot_pattern = r'(\w+)\.(\w+)\('
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(dot_pattern, line)
                for match in matches:
                    variable_name = match.group(1)
                    method_name = match.group(2)
                    
                    # Skip obvious safe cases
                    if variable_name in ['self', 'dict', 'list', 'str', 'int', 'float', 'bool']:
                        continue
                    
                    # Skip if it's a class or module (starts with capital)
                    if variable_name[0].isupper():
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
                        rf'{variable_name}\s+and\s+{variable_name}\.',
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
                            'method': method_name,
                            'content': line.strip()
                        }
                        all_issues.append(issue)
                        print(f"  ❌ Line {line_num}: {variable_name}.{method_name}() - {line.strip()[:80]}...")
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return all_issues

def find_attribute_access():
    """Find attribute access patterns that could cause NoneType errors."""
    
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
            
            print(f"\n🔍 Checking attribute access in: {file_path}")
            
            # Pattern to find attribute access
            attr_pattern = r'(\w+)\.(\w+)(?!\s*\()'
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(attr_pattern, line)
                for match in matches:
                    variable_name = match.group(1)
                    attribute_name = match.group(2)
                    
                    # Skip obvious safe cases
                    if variable_name in ['self', 'dict', 'list', 'str', 'int', 'float', 'bool']:
                        continue
                    
                    # Skip if it's a class or module (starts with capital)
                    if variable_name[0].isupper():
                        continue
                    
                    # Skip if it looks like a method call
                    if '(' in line[line.find(match.group(0)):]:
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
                        rf'{variable_name}\s+and\s+{variable_name}\.',
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
                            'attribute': attribute_name,
                            'content': line.strip(),
                            'type': 'attribute_access'
                        }
                        all_issues.append(issue)
                        print(f"  ❌ Line {line_num}: {variable_name}.{attribute_name} - {line.strip()[:80]}...")
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return all_issues

def main():
    print("🔍 COMPREHENSIVE NoneType ERROR HUNTER")
    print("=" * 60)
    
    print("\n1️⃣ Looking for all .method() calls...")
    dot_issues = find_all_dot_calls()
    
    print("\n2️⃣ Looking for attribute access...")
    attr_issues = find_attribute_access()
    
    all_issues = dot_issues + attr_issues
    
    print(f"\n📊 RESULTS:")
    print(f"   .method() calls: {len(dot_issues)}")
    print(f"   Attribute access: {len(attr_issues)}")
    print(f"   Total issues: {len(all_issues)}")
    
    if all_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND:")
        print("-" * 60)
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {os.path.basename(issue['file'])}:{issue['line']}")
            print(f"   Variable: {issue['variable']}")
            print(f"   Type: {issue.get('type', 'method_call')}")
            if 'method' in issue:
                print(f"   Method: {issue['method']}")
            if 'attribute' in issue:
                print(f"   Attribute: {issue['attribute']}")
            print(f"   Content: {issue['content']}")
            print()
    else:
        print("\n✅ No obvious NoneType issues found!")
    
    print("\n🔧 NEXT STEPS:")
    if all_issues:
        print("1. These are ALL potential NoneType error sources")
        print("2. Add None checks before each access")
        print("3. Test the robust service again")
    else:
        print("1. The issue might be in a different pattern")
        print("2. Check for complex expressions or nested calls")
        print("3. Look for list/dict access on None objects")

if __name__ == "__main__":
    main()
