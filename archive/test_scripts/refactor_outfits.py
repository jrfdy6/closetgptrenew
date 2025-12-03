#!/usr/bin/env python3
"""
Script to help refactor the large outfits.py file into smaller, manageable modules.
"""

import re
import os
from pathlib import Path

def analyze_file_structure():
    """Analyze the current outfits.py file structure"""
    
    file_path = "backend/src/routes/outfits.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    print(f"📊 FILE ANALYSIS: {file_path}")
    print(f"   Total lines: {total_lines}")
    print()
    
    # Find all functions and classes
    functions = []
    classes = []
    endpoints = []
    
    for i, line in enumerate(lines, 1):
        # Functions
        if re.match(r'^def |^async def ', line.strip()):
            func_name = re.search(r'(?:async )?def (\w+)', line)
            if func_name:
                functions.append((i, func_name.group(1)))
        
        # Classes
        elif re.match(r'^class ', line.strip()):
            class_name = re.search(r'class (\w+)', line)
            if class_name:
                classes.append((i, class_name.group(1)))
        
        # Router endpoints
        elif re.match(r'@router\.', line.strip()):
            endpoints.append((i, line.strip()))
    
    print(f"🔧 FUNCTIONS ({len(functions)}):")
    for line_num, func_name in functions[:10]:  # Show first 10
        print(f"   Line {line_num}: {func_name}")
    if len(functions) > 10:
        print(f"   ... and {len(functions) - 10} more")
    
    print(f"\n🏗️ CLASSES ({len(classes)}):")
    for line_num, class_name in classes:
        print(f"   Line {line_num}: {class_name}")
    
    print(f"\n🌐 ENDPOINTS ({len(endpoints)}):")
    for line_num, endpoint in endpoints[:10]:  # Show first 10
        print(f"   Line {line_num}: {endpoint}")
    if len(endpoints) > 10:
        print(f"   ... and {len(endpoints) - 10} more")
    
    return {
        'total_lines': total_lines,
        'functions': functions,
        'classes': classes,
        'endpoints': endpoints
    }

def create_refactor_plan():
    """Create a plan for refactoring the file"""
    
    plan = {
        'outfits/models.py': {
            'description': 'Pydantic models and request/response schemas',
            'includes': [
                'OutfitRequest',
                'CreateOutfitRequest', 
                'OutfitResponse'
            ]
        },
        'outfits/validation.py': {
            'description': 'Validation logic and outfit completeness checks',
            'includes': [
                'validate_outfit_completeness',
                '_is_semantically_appropriate',
                'validate_outfit_composition',
                'validate_layering_rules',
                'validate_color_material_harmony'
            ]
        },
        'outfits/styling.py': {
            'description': 'Style-related functions and filtering',
            'includes': [
                'filter_items_by_style',
                'get_hard_style_exclusions',
                'calculate_style_appropriateness_score',
                'validate_style_gender_compatibility'
            ]
        },
        'outfits/weather.py': {
            'description': 'Weather-related functions',
            'includes': [
                'check_item_weather_appropriateness',
                'attach_weather_context_to_items'
            ]
        },
        'outfits/generation.py': {
            'description': 'Core outfit generation logic',
            'includes': [
                'generate_outfit_logic',
                'ensure_base_item_included'
            ]
        },
        'outfits/utils.py': {
            'description': 'Utility functions and helpers',
            'includes': [
                'safe_get_metadata',
                'normalize_ts',
                'clean_for_firestore',
                'log_generation_strategy'
            ]
        },
        'outfits/routes.py': {
            'description': 'Main router with production endpoints',
            'includes': [
                'All @router.get() and @router.post() endpoints',
                'Main outfit generation endpoint'
            ]
        },
        'outfits/debug.py': {
            'description': 'Debug endpoints and testing',
            'includes': [
                'All debug-related endpoints',
                'Test endpoints'
            ]
        }
    }
    
    print("📋 REFACTORING PLAN:")
    print("=" * 50)
    
    for file_path, info in plan.items():
        print(f"\n📁 {file_path}")
        print(f"   Description: {info['description']}")
        print(f"   Includes:")
        for item in info['includes']:
            print(f"     - {item}")
    
    return plan

def create_directory_structure():
    """Create the directory structure for the refactored files"""
    
    base_dir = Path("backend/src/routes/outfits")
    base_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    init_file = base_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Outfits module for outfit generation and management."""\n')
    
    print(f"✅ Created directory structure: {base_dir}")
    return base_dir

if __name__ == "__main__":
    print("🔍 ANALYZING LARGE OUTFITS.PY FILE")
    print("=" * 50)
    
    # Analyze current structure
    analysis = analyze_file_structure()
    
    print("\n" + "=" * 50)
    
    # Create refactoring plan
    plan = create_refactor_plan()
    
    print("\n" + "=" * 50)
    
    # Create directory structure
    create_directory_structure()
    
    print("\n✅ ANALYSIS COMPLETE")
    print("\nNext steps:")
    print("1. Fix syntax errors in current outfits.py")
    print("2. Extract functions to appropriate modules")
    print("3. Update imports and dependencies")
    print("4. Test each module individually")
    print("5. Update main router to use new modules")
