#!/usr/bin/env python3
"""
Targeted script to find the specific .get() call causing NoneType errors in the robust service
"""

import os
import re
import sys
from pathlib import Path

def find_robust_service_get_calls():
    """Find all .get() calls specifically in robust service files."""
    
    # Files most likely to be involved in robust service execution
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
        "backend/src/services/wardrobe_preprocessor.py"
    ]
    
    all_issues = []
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
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

def main():
    print("🎯 TARGETED ROBUST SERVICE NoneType .get() FINDER")
    print("=" * 60)
    
    issues = find_robust_service_get_calls()
    
    print(f"\n📊 RESULTS:")
    print(f"   Total potential issues: {len(issues)}")
    
    if issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND:")
        print("-" * 60)
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {os.path.basename(issue['file'])}:{issue['line']}")
            print(f"   Variable: {issue['variable']}")
            print(f"   Content: {issue['content']}")
            print()
    else:
        print("\n✅ No obvious NoneType .get() issues found in robust service files!")
    
    print("\n🔧 NEXT STEPS:")
    if issues:
        print("1. These are the most likely candidates for the NoneType error")
        print("2. Add None checks before each .get() call")
        print("3. Test the robust service again")
    else:
        print("1. The issue might be in a different file")
        print("2. Check the 55 unfixed issues from the comprehensive scan")
        print("3. Look for chained .get() calls or complex expressions")

if __name__ == "__main__":
    main()
