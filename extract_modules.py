#!/usr/bin/env python3
"""
Script to extract scoring and composition modules from robust_outfit_generation_service.py
"""

import re

# Read the file
with open('backend/src/services/robust_outfit_generation_service.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')

def extract_method(content, method_name, start_line, end_line):
    """Extract a method and its content"""
    lines = content.split('\n')
    method_lines = lines[start_line-1:end_line]
    return '\n'.join(method_lines)

def find_method_bounds(lines, method_name):
    """Find start and end line of a method"""
    start = None
    indent_level = None
    
    for i, line in enumerate(lines):
        if f'def {method_name}(' in line:
            start = i
            # Get indent level (number of leading spaces)
            indent_level = len(line) - len(line.lstrip())
            break
    
    if start is None:
        return None, None
    
    # Find end of method (next method at same or lower indent level)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.strip().startswith('#'):
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and (line.strip().startswith('def ') or line.strip().startswith('async def ')):
                end = i
                break
    
    return start + 1, end  # +1 for 1-indexed

# Methods to extract
scoring_methods = {
    '_soft_score': (3573, 4340),
    '_analyze_style_profile_scores': (5327, 5789),
    '_analyze_weather_scores': (5790, 6090),
    '_analyze_user_feedback_scores': (6091, 6334),
    '_analyze_body_type_scores': (5161, 5326),
    '_calculate_style_evolution_score': (7907, 8122),
}

composition_methods = {
    '_cohesive_composition_with_scores': (6335, 7906),
    '_intelligent_item_selection': (4341, 4480),
}

print("✅ Extraction script ready")
print(f"Scoring methods: {len(scoring_methods)}")
print(f"Composition methods: {len(composition_methods)}")
print(f"Total lines to extract: {sum(end-start for start, end in list(scoring_methods.values()) + list(composition_methods.values()))}")

