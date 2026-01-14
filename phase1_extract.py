#!/usr/bin/env python3
"""
Phase 1 Extraction: Move scoring and composition methods to separate modules
"""

import re

def extract_method_with_bounds(lines, start_line, end_line):
    """Extract method lines (1-indexed)"""
    return lines[start_line-1:end_line]

def remove_method_from_lines(lines, start_line, end_line):
    """Remove method lines and return modified list (1-indexed)"""
    return lines[:start_line-1] + lines[end_line:]

# Read the main file
with open('backend/src/services/robust_outfit_generation_service.py', 'r') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Define methods to extract (line numbers from analysis)
# Format: (method_name, start_line, end_line, target_file)
extractions = [
    # Scoring methods
    ('_soft_score', 3573, 4340, 'scoring/soft_scorer.py'),
    ('_analyze_body_type_scores', 5161, 5326, 'scoring/body_type_analyzer.py'),
    ('_analyze_style_profile_scores', 5327, 5789, 'scoring/style_analyzer.py'),
    ('_analyze_weather_scores', 5790, 6090, 'scoring/weather_analyzer.py'),
    ('_analyze_user_feedback_scores', 6091, 6334, 'scoring/feedback_analyzer.py'),
    ('_calculate_style_evolution_score', 7907, 8122, 'scoring/style_evolution.py'),
    
    # Composition methods
    ('_cohesive_composition_with_scores', 6335, 7906, 'composition/cohesive_composer.py'),
    ('_intelligent_item_selection', 4341, 4480, 'composition/intelligent_selector.py'),
]

# Sort by start_line in reverse order (extract from bottom to top to maintain line numbers)
extractions.sort(key=lambda x: x[1], reverse=True)

extracted_content = {}
stub_methods = []

for method_name, start, end, target_file in extractions:
    print(f"\nExtracting {method_name} ({end-start} lines) -> {target_file}")
    
    # Extract method
    method_lines = extract_method_with_bounds(lines, start, end)
    extracted_content[target_file] = method_lines
    
    # Create stub method
    indent = '    '
    stub = [
        f"{indent}# NOTE: This method has been moved to {target_file}\n",
        f"{indent}# Keeping stub for backward compatibility during refactoring\n",
    ]
    
    # Get method signature
    sig_line = method_lines[0]
    stub.append(sig_line)
    stub.append(f"{indent}    raise NotImplementedError(f'{method_name} has been moved to {target_file}')\n")
    stub.append(f"\n")
    
    stub_methods.append((start, stub))
    
    # Remove from main file
    lines = remove_method_from_lines(lines, start, end)
    print(f"  Removed from main file. New size: {len(lines)} lines")

# Insert stubs (in reverse order to maintain line numbers)
for start, stub in reversed(stub_methods):
    lines = lines[:start-1] + stub + lines[start-1:]

print(f"\nFinal main file size: {len(lines)} lines")
print(f"Reduction: {8278 - len(lines)} lines")

# Write modified main file
with open('backend/src/services/robust_outfit_generation_service.py', 'w') as f:
    f.writelines(lines)

print("\n✅ Main file updated with stubs")

# Create extracted files
for target_file, content in extracted_content.items():
    filepath = f'backend/src/services/{target_file}'
    
    # Create file header
    header = f'''#!/usr/bin/env python3
"""
{target_file.split('/')[-1].replace('.py', '').replace('_', ' ').title()}
{'=' * 50}

Extracted from robust_outfit_generation_service.py
Part of Phase 1 refactoring to reduce file size.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class {target_file.split('/')[-1].replace('.py', '').replace('_', ' ').title().replace(' ', '')}:
    """Extracted scoring/composition logic"""
    
    def __init__(self, parent_service):
        """Initialize with reference to parent service for accessing helper methods"""
        self.service = parent_service
    
'''
    
    # Write file
    with open(filepath, 'w') as f:
        f.write(header)
        f.writelines(content)
    
    print(f"✅ Created {filepath}")

print("\n" + "="*80)
print("Phase 1 Extraction Complete!")
print(f"Original: 8,278 lines")
print(f"New: {len(lines)} lines")
print(f"Extracted: {8278 - len(lines)} lines")
print("="*80)

