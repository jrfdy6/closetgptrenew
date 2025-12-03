#!/usr/bin/env python3
"""
Comprehensive script to find and fix ALL remaining IndentationErrors in outfits.py.
This script will find empty control structures and fix them by uncommenting print statements.
"""

import re

def fix_indentation_errors_in_outfits():
    """Fix all IndentationErrors in outfits.py by uncommenting print statements."""
    file_path = "backend/src/routes/outfits.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to find commented-out print statements that are the only content in control structures
    # This matches lines that have only whitespace, a comment, and a print statement
    pattern = r'(\s+)(#\s*print\([^)]+\))\s*$'
    
    # Find all matches
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    
    print(f"Found {len(matches)} commented-out print statements that might be causing IndentationErrors")
    
    # Fix each match by uncommenting the print statement
    fixed_count = 0
    for match in reversed(matches):  # Process in reverse order to maintain line numbers
        indent = match.group(1)
        commented_print = match.group(2)
        
        # Uncomment the print statement
        uncommented_print = commented_print[1:]  # Remove the # character
        
        # Replace in content
        old_text = match.group(0)
        new_text = f"{indent}{uncommented_print}"
        
        content = content.replace(old_text, new_text)
        fixed_count += 1
        
        print(f"Fixed: {commented_print.strip()} -> {uncommented_print.strip()}")
    
    # Write the fixed content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Fixed {fixed_count} commented-out print statements")
    return fixed_count

def main():
    """Main function to fix all IndentationErrors in outfits.py."""
    print("🔍 Finding and fixing all remaining IndentationErrors in outfits.py...")
    
    try:
        fixed_count = fix_indentation_errors_in_outfits()
        
        if fixed_count > 0:
            print(f"\n✅ Successfully fixed {fixed_count} IndentationErrors")
            print("📝 The outfits.py file should now compile successfully")
        else:
            print("\n✅ No IndentationErrors found to fix")
            
    except Exception as e:
        print(f"❌ Error fixing IndentationErrors: {e}")

if __name__ == "__main__":
    main()

