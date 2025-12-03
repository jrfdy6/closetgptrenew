#!/usr/bin/env python3
"""
Audit bidirectional matching for styles, occasions, and moods.
Identifies cases where A → B but B ↛ A (missing bidirectional compatibility).
"""

import ast
import re
from collections import defaultdict
from typing import Dict, List

def extract_dict_from_file(filepath: str, dict_name: str) -> Dict[str, List[str]]:
    """Extract a dictionary definition from a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Try to find and extract the dictionary
    # Look for the pattern: DICT_NAME = { or DICT_NAME: Dict[...] = {
    pattern = rf'{dict_name}\s*(?::\s*Dict\[.*?\])?\s*=\s*{{(.*?)^\}}'
    
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    
    if not match:
        return {}
    
    # Extract the dictionary content and parse it
    dict_str = '{' + match.group(1) + '}'
    
    try:
        # Use ast.literal_eval for safe evaluation
        result = ast.literal_eval(dict_str)
        return result
    except:
        # If that fails, try exec (less safe but works)
        try:
            local_vars = {}
            exec(f'result = {dict_str}', {}, local_vars)
            return local_vars.get('result', {})
        except Exception as e:
            print(f"   Error parsing {dict_name}: {e}")
            return {}

def check_bidirectional_compatibility(name: str, compat_dict: Dict[str, List[str]]) -> Dict[str, any]:
    """Check for bidirectional compatibility issues."""
    print(f"\n{'='*80}")
    print(f"🔍 Auditing {name} Bidirectional Compatibility")
    print(f"{'='*80}\n")
    
    print(f"Total {name.lower()}: {len(compat_dict)}\n")
    
    if not compat_dict:
        print(f"⚠️  No data found for {name}\n")
        return {'total_keys': 0, 'issues': 0}
    
    issues = []
    
    # Build a map of what each value is referenced by
    referenced_by = defaultdict(set)
    
    for key, values in compat_dict.items():
        if not isinstance(values, list):
            continue
        for value in values:
            if value != key:  # Ignore self-references
                referenced_by[value].add(key)
    
    # Check each key
    for key, values in compat_dict.items():
        if not isinstance(values, list):
            continue
            
        values_set = set(values)
        
        # Check if this key is referenced by others but doesn't reference them back
        for referencer in referenced_by.get(key, set()):
            if referencer not in values_set:
                issues.append({
                    'type': 'missing_bidirectional',
                    'key': key,
                    'missing': referencer,
                    'message': f"'{referencer}' includes '{key}', but '{key}' doesn't include '{referencer}'"
                })
    
    # Report issues
    if not issues:
        print(f"✅ No bidirectional compatibility issues found!\n")
        return {'total_keys': len(compat_dict), 'issues': 0, 'details': []}
    
    print(f"⚠️  Found {len(issues)} bidirectional compatibility issues:\n")
    
    # Group by key
    issues_by_key = defaultdict(list)
    for issue in issues:
        issues_by_key[issue['key']].append(issue['missing'])
    
    # Show top issues
    sorted_issues = sorted(issues_by_key.items(), key=lambda x: len(x[1]), reverse=True)
    
    for key, missing_items in sorted_issues[:15]:  # Show top 15
        print(f"❌ '{key}' is missing {len(missing_items)} bidirectional match(es):")
        for item in sorted(missing_items)[:8]:  # Show first 8
            print(f"   → Should include: '{item}'")
        if len(missing_items) > 8:
            print(f"   ... and {len(missing_items) - 8} more")
        print()
    
    if len(sorted_issues) > 15:
        print(f"... and {len(sorted_issues) - 15} more keys with issues\n")
    
    return {
        'total_keys': len(compat_dict),
        'issues': len(issues),
        'issues_by_key': dict(issues_by_key),
        'details': issues
    }

def main():
    """Run all audits."""
    print("🚀 Bidirectional Compatibility Audit")
    print("="*80)
    print("Checking for cases where A includes B but B doesn't include A\n")
    
    results = {}
    
    # Parse style compatibility
    print("📖 Loading style compatibility matrix...")
    styles = extract_dict_from_file('backend/src/utils/style_compatibility_matrix.py', 'STYLE_COMPATIBILITY')
    if styles:
        results['styles'] = check_bidirectional_compatibility("STYLES", styles)
    else:
        print("   ❌ Failed to parse styles\n")
        results['styles'] = {'issues': 0}
    
    # Parse occasion fallbacks
    print("📖 Loading occasion fallbacks...")
    occasions = extract_dict_from_file('backend/src/utils/semantic_compatibility.py', 'FALLBACKS')
    if occasions:
        results['occasions'] = check_bidirectional_compatibility("OCCASIONS", occasions)
    else:
        print("   ❌ Failed to parse occasions\n")
        results['occasions'] = {'issues': 0}
    
    # For moods
    print("📖 Loading mood compatibility...")
    moods = extract_dict_from_file('backend/src/utils/semantic_compatibility.py', 'MOOD_COMPAT')
    if moods:
        results['moods'] = check_bidirectional_compatibility("MOODS", moods)
    else:
        print("   ⚠️  Could not parse moods (inline dict)\n")
        results['moods'] = {'issues': 0}
    
    # Summary
    print("\n" + "="*80)
    print("📊 AUDIT SUMMARY")
    print("="*80)
    
    total_issues = sum(r.get('issues', 0) for r in results.values())
    
    print(f"\nStyles:    {results['styles'].get('issues', 0)} issues ({results['styles'].get('total_keys', 0)} total styles)")
    print(f"Occasions: {results['occasions'].get('issues', 0)} issues ({results['occasions'].get('total_keys', 0)} total occasions)")
    print(f"Moods:     {results['moods'].get('issues', 0)} issues ({results['moods'].get('total_keys', 0)} total moods)")
    
    print(f"\n{'✅ All dimensions checked!' if total_issues == 0 else f'⚠️  Total: {total_issues} bidirectional issues found'}")
    
    if total_issues > 0:
        print("\n💡 Action Items:")
        print("   1. Review the missing bidirectional references above")
        print("   2. Update compatibility matrices to add them")
        print("   3. Re-run this audit to verify fixes")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    results = main()
