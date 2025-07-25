#!/usr/bin/env python3
"""
Script to update Firestore filter syntax from .where() to .filter()
This addresses the deprecation warnings in the Firebase console.
"""

import os
import re
from pathlib import Path

def update_file_filters(file_path):
    """Update .where() calls to .filter() calls in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match .where() calls but not pandas/numpy where() calls
        # This regex looks for .where( followed by a string literal, operator, and value
        pattern = r'\.where\(([^)]+)\)'
        
        def replace_where(match):
            # Check if this looks like a Firestore query (has string literals and operators)
            where_content = match.group(1)
            if any(op in where_content for op in ['==', '!=', '>=', '<=', '>', '<', 'in', 'not-in', 'array_contains']):
                return f'.filter({where_content})'
            return match.group(0)  # Keep original if it doesn't look like Firestore
        
        updated_content = re.sub(pattern, replace_where, content)
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all Python files in the backend directory."""
    backend_dir = Path("src")
    
    if not backend_dir.exists():
        print(f"❌ Backend directory {backend_dir} not found")
        return
    
    updated_files = 0
    total_files = 0
    
    # Find all Python files in the backend
    for py_file in backend_dir.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        total_files += 1
        if update_file_filters(py_file):
            updated_files += 1
    
    print(f"\n📊 Summary:")
    print(f"   Total Python files checked: {total_files}")
    print(f"   Files updated: {updated_files}")
    print(f"   Files unchanged: {total_files - updated_files}")

if __name__ == "__main__":
    main() 