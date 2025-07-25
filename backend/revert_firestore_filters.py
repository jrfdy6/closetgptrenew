#!/usr/bin/env python3
"""
Script to revert Firestore filter syntax from .filter() back to .where()
since .filter() is not available in the current SDK version.
"""

import os
import re
from pathlib import Path

def revert_file_filters(file_path):
    """Revert .filter() calls back to .where() calls in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match .filter() calls
        pattern = r'\.filter\(([^)]+)\)'
        
        def replace_filter(match):
            # Check if this looks like a Firestore query (has string literals and operators)
            filter_content = match.group(1)
            if any(op in filter_content for op in ['==', '!=', '>=', '<=', '>', '<', 'in', 'not-in', 'array_contains']):
                return f'.where({filter_content})'
            return match.group(0)  # Keep original if it doesn't look like Firestore
        
        updated_content = re.sub(pattern, replace_filter, content)
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Reverted {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error reverting {file_path}: {e}")
        return False

def main():
    """Revert all Python files in the backend directory."""
    backend_dir = Path("src")
    
    if not backend_dir.exists():
        print(f"❌ Backend directory {backend_dir} not found")
        return
    
    reverted_files = 0
    total_files = 0
    
    # Find all Python files in the backend
    for py_file in backend_dir.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        total_files += 1
        if revert_file_filters(py_file):
            reverted_files += 1
    
    print(f"\n📊 Summary:")
    print(f"   Total Python files checked: {total_files}")
    print(f"   Files reverted: {reverted_files}")
    print(f"   Files unchanged: {total_files - reverted_files}")

if __name__ == "__main__":
    main() 