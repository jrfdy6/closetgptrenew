#!/usr/bin/env python3
"""
Enforce bidirectional compatibility for all semantic matching dimensions.
If A includes B, ensure B includes A.
"""

import ast
import re
from typing import Dict, List
from collections import defaultdict

def extract_dict_from_file(filepath: str, dict_name: str) -> tuple:
    """Extract a dictionary definition and its position from a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the dictionary definition
    pattern = rf'({dict_name}\s*(?::\s*Dict\[.*?\])?\s*=\s*{{)(.*?)(^\}})'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    
    if not match:
        return None, None, None
    
    start_pos = match.start()
    end_pos = match.end()
    dict_str = '{' + match.group(2) + '}'
    
    try:
        result = ast.literal_eval(dict_str)
        return result, start_pos, end_pos
    except:
        return None, None, None

def enforce_bidirectional(compat_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Enforce bidirectional compatibility."""
    print(f"   Original entries: {len(compat_dict)}")
    
    # Create a new dict with bidirectional relationships
    new_dict = {}
    
    # First pass: copy all existing relationships
    for key, values in compat_dict.items():
        new_dict[key] = set(values)  # Use set to avoid duplicates
    
    # Second pass: add reverse relationships
    changes_made = 0
    for key, values in compat_dict.items():
        for value in values:
            if value == key:
                continue  # Skip self-references
            
            # Ensure the value exists in new_dict
            if value not in new_dict:
                new_dict[value] = {value}  # Self-reference
            
            # Add bidirectional relationship
            if key not in new_dict[value]:
                new_dict[value].add(key)
                changes_made += 1
    
    # Convert sets back to sorted lists
    result = {k: sorted(v) for k, v in sorted(new_dict.items())}
    
    print(f"   New entries: {len(result)}")
    print(f"   Bidirectional relationships added: {changes_made}")
    
    return result

def format_dict_for_python(dict_data: Dict[str, List[str]], indent: int = 4) -> str:
    """Format dictionary as pretty Python code."""
    lines = []
    indent_str = ' ' * indent
    
    for key, values in sorted(dict_data.items()):
        # Format the values list - break into multiple lines if long
        if len(values) <= 5:
            # Short list - single line
            values_str = ', '.join(f'"{v}"' for v in values)
            lines.append(f'{indent_str}"{key}": [{values_str}],')
        else:
            # Long list - multiple lines
            lines.append(f'{indent_str}"{key}": [')
            for i in range(0, len(values), 5):
                batch = values[i:i+5]
                batch_str = ', '.join(f'"{v}"' for v in batch)
                comma = ',' if i + 5 < len(values) else ''
                lines.append(f'{indent_str}    {batch_str}{comma}')
            lines.append(f'{indent_str}],')
    
    return '\n'.join(lines)

def update_dict_in_file(filepath: str, dict_name: str, new_dict: Dict[str, List[str]]) -> bool:
    """Update a dictionary in a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the dictionary definition
    pattern = rf'({dict_name}\s*(?::\s*Dict\[.*?\])?\s*=\s*{{)(.*?)(^\}})'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    
    if not match:
        return False
    
    # Build new dictionary content
    new_dict_content = '\n' + format_dict_for_python(new_dict, 4) + '\n'
    
    # Replace the old content with new
    new_content = (
        content[:match.start(2)] +
        new_dict_content +
        content[match.end(2):]
    )
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    """Main enforcement function."""
    print("🔧 Automated Bidirectional Compatibility Enforcement")
    print("="*80)
    print("This script ensures all semantic relationships are bidirectional.\n")
    
    results = {}
    
    # 1. Fix Style Compatibility Matrix
    print("1️⃣  Processing STYLE_COMPATIBILITY...")
    filepath = 'backend/src/utils/style_compatibility_matrix.py'
    styles, _, _ = extract_dict_from_file(filepath, 'STYLE_COMPATIBILITY')
    
    if styles:
        fixed_styles = enforce_bidirectional(styles)
        if update_dict_in_file(filepath, 'STYLE_COMPATIBILITY', fixed_styles):
            print(f"   ✅ Updated {filepath}\n")
            results['styles'] = 'SUCCESS'
        else:
            print(f"   ❌ Failed to update {filepath}\n")
            results['styles'] = 'FAILED'
    else:
        print(f"   ❌ Could not parse {filepath}\n")
        results['styles'] = 'PARSE_FAILED'
    
    # 2. Fix Occasion Fallbacks
    print("2️⃣  Processing OCCASION FALLBACKS...")
    filepath = 'backend/src/utils/semantic_compatibility.py'
    occasions, _, _ = extract_dict_from_file(filepath, 'OCCASION_FALLBACKS')
    
    if occasions:
        fixed_occasions = enforce_bidirectional(occasions)
        if update_dict_in_file(filepath, 'OCCASION_FALLBACKS', fixed_occasions):
            print(f"   ✅ Updated {filepath}\n")
            results['occasions'] = 'SUCCESS'
        else:
            print(f"   ❌ Failed to update {filepath}\n")
            results['occasions'] = 'FAILED'
    else:
        print(f"   ⚠️  Could not parse occasions\n")
        results['occasions'] = 'SKIPPED'
    
    # 3. Fix Mood Compatibility
    print("3️⃣  Processing MOOD_COMPAT...")
    moods, _, _ = extract_dict_from_file(filepath, 'MOOD_COMPAT')
    
    if moods:
        fixed_moods = enforce_bidirectional(moods)
        if update_dict_in_file(filepath, 'MOOD_COMPAT', fixed_moods):
            print(f"   ✅ Updated {filepath}\n")
            results['moods'] = 'SUCCESS'
        else:
            print(f"   ❌ Failed to update {filepath}\n")
            results['moods'] = 'FAILED'
    else:
        print(f"   ⚠️  Could not parse moods (inline dict)\n")
        results['moods'] = 'SKIPPED'
    
    # Summary
    print("="*80)
    print("📊 ENFORCEMENT SUMMARY")
    print("="*80)
    
    for dimension, status in results.items():
        icon = "✅" if status == "SUCCESS" else "⚠️" if status == "SKIPPED" else "❌"
        print(f"{icon} {dimension.capitalize()}: {status}")
    
    success_count = sum(1 for s in results.values() if s == 'SUCCESS')
    
    if success_count > 0:
        print(f"\n✅ Successfully enforced bidirectional compatibility for {success_count} dimension(s)!")
        print("\n💡 Next Steps:")
        print("   1. Review the changes in git diff")
        print("   2. Run audit script to verify: python3 audit_bidirectional_matching.py")
        print("   3. Test with real wardrobe: python3 test_semantic_impact.py")
        print("   4. Commit and deploy the fixes")
    else:
        print("\n❌ No dimensions were successfully updated.")
        print("   Check the error messages above for details.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

