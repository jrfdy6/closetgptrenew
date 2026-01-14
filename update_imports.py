#!/usr/bin/env python3
"""
Update imports in robust_outfit_generation_service.py to use extracted modules
"""

import re

# Read the file
with open('backend/src/services/robust_outfit_generation_service.py', 'r') as f:
    content = f.read()

# Add new imports after existing imports (after the last 'from' statement)
new_imports = """
# Extracted modules
from .constants import (
    GenerationStrategy,
    BASE_CATEGORY_LIMITS,
    MAX_ITEMS,
    MIN_ITEMS,
    INAPPROPRIATE_COMBINATIONS,
    STYLE_COMPATIBILITY,
    GENERATION_STRATEGY_ORDER,
)
from .item_utils import (
    safe_get_item_type as util_safe_get_item_type,
    safe_get_item_name as util_safe_get_item_name,
    safe_get_item_attr as util_safe_get_item_attr,
    safe_get,
    get_item_category as util_get_item_category,
    is_shirt as util_is_shirt,
    is_turtleneck as util_is_turtleneck,
    is_collared as util_is_collared,
    get_item_formality_level as util_get_item_formality_level,
    get_context_formality_level as util_get_context_formality_level,
)
from .validation import (
    can_add_category as util_can_add_category,
    check_inappropriate_combination as util_check_inappropriate_combination,
    deduplicate_items as util_deduplicate_items,
    get_essential_requirements as util_get_essential_requirements,
)
"""

# Find the last import statement
last_import_match = None
for match in re.finditer(r'^from .+ import .+$', content, re.MULTILINE):
    last_import_match = match

if last_import_match:
    insert_pos = last_import_match.end()
    content = content[:insert_pos] + '\n' + new_imports + content[insert_pos:]
    print(f"✅ Added imports after line {content[:insert_pos].count(chr(10)) + 1}")
else:
    print("⚠️ Could not find import section")

# Write back
with open('backend/src/services/robust_outfit_generation_service.py', 'w') as f:
    f.write(content)

print("✅ Updated imports in robust_outfit_generation_service.py")
print("\nNext steps:")
print("1. Replace method calls with util_ versions")
print("2. Remove old constant definitions from __init__")
print("3. Test the service")

