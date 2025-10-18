#!/usr/bin/env python3
"""
Comprehensive Metadata Audit for Outfit Generation
===================================================

Ensures metadata is in the CORRECT FIELDS used by outfit generation,
not just in tags arrays.

Checks:
1. occasion, style, mood - Used for hard filtering and scoring
2. metadata.visualAttributes.* - Used for compatibility scoring
3. metadata.normalized.* - Used for consistent filtering
4. Mismatches between tags and actual fields
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
from collections import defaultdict
import json

# Initialize Firestore
db = firestore.Client()

# User ID to audit
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

# Known occasion/style/mood values (from config)
KNOWN_OCCASIONS = [
    'casual', 'business', 'formal', 'athletic', 'sport', 'gym', 
    'loungewear', 'beach', 'party', 'date', 'outdoor', 'travel'
]

KNOWN_STYLES = [
    'classic', 'modern', 'minimalist', 'bohemian', 'preppy', 
    'edgy', 'romantic', 'athletic', 'streetwear', 'professional'
]

KNOWN_MOODS = [
    'confident', 'relaxed', 'professional', 'playful', 
    'elegant', 'bold', 'comfortable', 'creative'
]

# Critical fields used by outfit generation
OUTFIT_GENERATION_FIELDS = {
    'CRITICAL_ROOT': {
        'occasion': 'Hard filtering (Line 1731) + Primary scoring (Line 1966)',
        'style': 'Hard filtering (Line 1732) + Style multiplier (Line 1940)',
    },
    'HIGH_PRIORITY_ROOT': {
        'mood': 'Bonus scoring (not hard filter)',
        'type': 'Category-specific logic',
        'color': 'Color harmony calculations',
        'season': 'Seasonal appropriateness',
    },
    'CRITICAL_VISUAL_ATTRIBUTES': {
        'wearLayer': 'Layer positioning (prevents jacket under shirt)',
        'sleeveLength': 'Sleeve validation (prevents conflicts)',
        'pattern': 'Pattern mixing rules',
        'material': 'Weather appropriateness + texture mixing',
        'fit': 'Fit/silhouette balance',
        'formalLevel': 'Formality matching',
    },
    'HIGH_PRIORITY_VISUAL_ATTRIBUTES': {
        'fabricWeight': 'Temperature matching',
        'textureStyle': 'Texture mixing',
        'silhouette': 'Proportion harmony',
        'length': 'Length compatibility',
    },
    'NORMALIZED_METADATA': {
        'normalized.occasion': 'Consistent filtering (lowercase)',
        'normalized.style': 'Consistent filtering (lowercase)',
        'normalized.mood': 'Consistent filtering (lowercase)',
    },
    'COMPATIBILITY_SCORES': {
        'bodyTypeCompatibility': 'Body type scoring (Analyzer #1)',
        'weatherCompatibility': 'Weather scoring (Analyzer #3)',
    }
}


def check_nested_field(item, field_path):
    """Check if a nested field exists and has a value."""
    parts = field_path.split('.')
    current = item
    
    for part in parts:
        if isinstance(current, dict):
            if part not in current or current[part] is None:
                return False, None
            current = current[part]
        else:
            return False, None
    
    # Check if value is empty
    if isinstance(current, (list, dict, str)) and not current:
        return False, None
    
    return True, current


def extract_keywords_from_tags(tags):
    """Extract potential occasion/style/mood values from tags."""
    if not tags:
        return {'occasions': [], 'styles': [], 'moods': []}
    
    extracted = {
        'occasions': [],
        'styles': [],
        'moods': []
    }
    
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in KNOWN_OCCASIONS:
            extracted['occasions'].append(tag)
        if tag_lower in KNOWN_STYLES:
            extracted['styles'].append(tag)
        if tag_lower in KNOWN_MOODS:
            extracted['moods'].append(tag)
    
    return extracted


def audit_wardrobe():
    """Perform comprehensive metadata audit."""
    
    print("\n" + "="*100)
    print("COMPREHENSIVE METADATA AUDIT FOR OUTFIT GENERATION")
    print("="*100)
    print(f"User ID: {USER_ID}\n")
    
    # Get all wardrobe items
    print("📦 Fetching wardrobe items from Firestore...")
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', USER_ID)
    docs = wardrobe_ref.stream()
    
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data['_doc_id'] = doc.id
        items.append(item_data)
    
    total_items = len(items)
    print(f"✅ Retrieved {total_items} items\n")
    
    if not items:
        print("❌ No items found!")
        return
    
    # Statistics tracking
    stats = {
        'total': total_items,
        'tags_only_metadata': 0,
        'structured_metadata': 0,
        'missing_critical_fields': 0,
        'complete_metadata': 0,
    }
    
    # Field-level statistics
    field_stats = defaultdict(lambda: {'present': 0, 'missing': 0, 'empty': 0})
    
    # Problem tracking
    problems = {
        'occasion_in_tags_not_field': [],
        'style_in_tags_not_field': [],
        'mood_in_tags_not_field': [],
        'missing_visual_attributes': [],
        'missing_normalized': [],
        'missing_critical_fields': [],
        'empty_occasion_style': [],
    }
    
    # Analyze each item
    for item in items:
        item_id = item.get('id', item.get('_doc_id', 'unknown'))[:20]
        item_name = item.get('name', 'Unknown')[:50]
        item_type = item.get('type', 'unknown')
        
        # Extract tags
        tags = item.get('tags', [])
        tags_content = extract_keywords_from_tags(tags)
        
        # Check root-level fields
        occasion_field = item.get('occasion', [])
        style_field = item.get('style', [])
        mood_field = item.get('mood', [])
        
        # PROBLEM 1: Metadata in tags but not in fields
        if tags_content['occasions'] and not occasion_field:
            problems['occasion_in_tags_not_field'].append({
                'id': item_id,
                'name': item_name,
                'tags': tags,
                'in_tags': tags_content['occasions'],
                'in_field': occasion_field
            })
        
        if tags_content['styles'] and not style_field:
            problems['style_in_tags_not_field'].append({
                'id': item_id,
                'name': item_name,
                'tags': tags,
                'in_tags': tags_content['styles'],
                'in_field': style_field
            })
        
        if tags_content['moods'] and not mood_field:
            problems['mood_in_tags_not_field'].append({
                'id': item_id,
                'name': item_name,
                'tags': tags,
                'in_tags': tags_content['moods'],
                'in_field': mood_field
            })
        
        # PROBLEM 2: Empty occasion AND style (will fail hard filtering)
        if not occasion_field and not style_field:
            problems['empty_occasion_style'].append({
                'id': item_id,
                'name': item_name,
                'type': item_type,
                'tags': tags,
            })
        
        # Check metadata object
        metadata = item.get('metadata', {})
        if not metadata:
            problems['missing_visual_attributes'].append({
                'id': item_id,
                'name': item_name,
                'reason': 'No metadata object'
            })
            continue
        
        # Check visualAttributes
        visual_attrs = metadata.get('visualAttributes', {})
        if not visual_attrs:
            problems['missing_visual_attributes'].append({
                'id': item_id,
                'name': item_name,
                'reason': 'No visualAttributes'
            })
        
        # Check normalized metadata
        normalized = metadata.get('normalized', {})
        if not normalized:
            problems['missing_normalized'].append({
                'id': item_id,
                'name': item_name,
            })
        
        # Track field presence
        for category, fields in OUTFIT_GENERATION_FIELDS.items():
            for field, description in fields.items():
                if category in ['CRITICAL_VISUAL_ATTRIBUTES', 'HIGH_PRIORITY_VISUAL_ATTRIBUTES']:
                    field_path = f'metadata.visualAttributes.{field}'
                elif category in ['NORMALIZED_METADATA']:
                    field_path = f'metadata.{field}'
                elif category == 'COMPATIBILITY_SCORES':
                    field_path = field
                else:
                    field_path = field
                
                has_value, value = check_nested_field(item, field_path)
                
                if has_value:
                    field_stats[field]['present'] += 1
                elif value is not None:
                    field_stats[field]['empty'] += 1
                else:
                    field_stats[field]['missing'] += 1
        
        # Check if item has ALL critical fields
        has_occasion = bool(occasion_field)
        has_style = bool(style_field)
        has_wear_layer = check_nested_field(item, 'metadata.visualAttributes.wearLayer')[0]
        has_sleeve_length = check_nested_field(item, 'metadata.visualAttributes.sleeveLength')[0]
        
        if not (has_occasion or has_style):
            stats['missing_critical_fields'] += 1
            problems['missing_critical_fields'].append({
                'id': item_id,
                'name': item_name,
                'missing': 'occasion AND style (will be filtered out)'
            })
        
        if has_occasion and has_style and has_wear_layer and has_sleeve_length:
            stats['complete_metadata'] += 1
    
    # Generate Report
    print("="*100)
    print("🚨 CRITICAL ISSUES - Items That Will Be Filtered Out")
    print("="*100)
    
    print(f"\n1. Items with EMPTY occasion AND style fields:")
    print(f"   Count: {len(problems['empty_occasion_style'])}/{total_items}")
    print(f"   Impact: ⛔ These items will NEVER appear in outfits (fail hard filtering)")
    if problems['empty_occasion_style']:
        print(f"\n   Examples:")
        for item in problems['empty_occasion_style'][:5]:
            print(f"   ❌ {item['name']}")
            print(f"      Type: {item['type']}, Tags: {item['tags']}")
    
    print(f"\n2. Items with occasion in TAGS but not in occasion FIELD:")
    print(f"   Count: {len(problems['occasion_in_tags_not_field'])}/{total_items}")
    print(f"   Impact: ⚠️  Outfit generation doesn't use tags, only the 'occasion' field")
    if problems['occasion_in_tags_not_field']:
        print(f"\n   Examples:")
        for item in problems['occasion_in_tags_not_field'][:5]:
            print(f"   ⚠️  {item['name']}")
            print(f"      In tags: {item['in_tags']}, In field: {item['in_field']}")
    
    print(f"\n3. Items with style in TAGS but not in style FIELD:")
    print(f"   Count: {len(problems['style_in_tags_not_field'])}/{total_items}")
    print(f"   Impact: ⚠️  Outfit generation doesn't use tags, only the 'style' field")
    if problems['style_in_tags_not_field']:
        print(f"\n   Examples:")
        for item in problems['style_in_tags_not_field'][:5]:
            print(f"   ⚠️  {item['name']}")
            print(f"      In tags: {item['in_tags']}, In field: {item['in_field']}")
    
    print("\n" + "="*100)
    print("⚠️  HIGH PRIORITY ISSUES - Missing Visual Attributes")
    print("="*100)
    
    print(f"\n4. Items with NO visualAttributes:")
    print(f"   Count: {len(problems['missing_visual_attributes'])}/{total_items}")
    print(f"   Impact: ⚠️  Missing pattern, material, fit, layer info (reduces compatibility scoring)")
    if problems['missing_visual_attributes']:
        print(f"\n   Examples:")
        for item in problems['missing_visual_attributes'][:5]:
            print(f"   ⚠️  {item['name']}: {item['reason']}")
    
    print(f"\n5. Items with NO normalized metadata:")
    print(f"   Count: {len(problems['missing_normalized'])}/{total_items}")
    print(f"   Impact: ⚠️  Inconsistent filtering (case sensitivity issues)")
    if problems['missing_normalized']:
        print(f"\n   Examples:")
        for item in problems['missing_normalized'][:5]:
            print(f"   ⚠️  {item['name']}")
    
    # Field-by-field breakdown
    print("\n" + "="*100)
    print("📊 FIELD-BY-FIELD BREAKDOWN")
    print("="*100)
    
    print(f"\n🔥 CRITICAL ROOT FIELDS (Required for Hard Filtering):")
    print(f"-" * 100)
    for field, description in OUTFIT_GENERATION_FIELDS['CRITICAL_ROOT'].items():
        present = field_stats[field]['present']
        missing = field_stats[field]['missing']
        empty = field_stats[field]['empty']
        total_bad = missing + empty
        pct = (present / total_items) * 100
        status = "✅" if pct >= 90 else "⚠️" if pct >= 50 else "❌"
        print(f"{status} {field:20} Present: {present:>3}/{total_items} ({pct:>5.1f}%) | Missing/Empty: {total_bad:>3}")
        print(f"   Usage: {description}")
    
    print(f"\n📊 HIGH PRIORITY ROOT FIELDS:")
    print(f"-" * 100)
    for field, description in OUTFIT_GENERATION_FIELDS['HIGH_PRIORITY_ROOT'].items():
        present = field_stats[field]['present']
        missing = field_stats[field]['missing']
        empty = field_stats[field]['empty']
        total_bad = missing + empty
        pct = (present / total_items) * 100
        status = "✅" if pct >= 90 else "⚠️" if pct >= 50 else "❌"
        print(f"{status} {field:20} Present: {present:>3}/{total_items} ({pct:>5.1f}%) | Missing/Empty: {total_bad:>3}")
        print(f"   Usage: {description}")
    
    print(f"\n🔥 CRITICAL VISUAL ATTRIBUTES (Required for Layer/Pattern/Fit Logic):")
    print(f"-" * 100)
    for field, description in OUTFIT_GENERATION_FIELDS['CRITICAL_VISUAL_ATTRIBUTES'].items():
        present = field_stats[field]['present']
        missing = field_stats[field]['missing']
        empty = field_stats[field]['empty']
        total_bad = missing + empty
        pct = (present / total_items) * 100
        status = "✅" if pct >= 90 else "⚠️" if pct >= 50 else "❌"
        print(f"{status} {field:20} Present: {present:>3}/{total_items} ({pct:>5.1f}%) | Missing/Empty: {total_bad:>3}")
        print(f"   Usage: {description}")
    
    print(f"\n📊 HIGH PRIORITY VISUAL ATTRIBUTES:")
    print(f"-" * 100)
    for field, description in OUTFIT_GENERATION_FIELDS['HIGH_PRIORITY_VISUAL_ATTRIBUTES'].items():
        present = field_stats[field]['present']
        missing = field_stats[field]['missing']
        empty = field_stats[field]['empty']
        total_bad = missing + empty
        pct = (present / total_items) * 100
        status = "✅" if pct >= 90 else "⚠️" if pct >= 50 else "❌"
        print(f"{status} {field:20} Present: {present:>3}/{total_items} ({pct:>5.1f}%) | Missing/Empty: {total_bad:>3}")
        print(f"   Usage: {description}")
    
    # Summary Score
    print("\n" + "="*100)
    print("📈 METADATA QUALITY SCORE")
    print("="*100)
    
    # Calculate score
    occasion_pct = (field_stats['occasion']['present'] / total_items) * 100
    style_pct = (field_stats['style']['present'] / total_items) * 100
    wear_layer_pct = (field_stats['wearLayer']['present'] / total_items) * 100
    sleeve_pct = (field_stats['sleeveLength']['present'] / total_items) * 100
    pattern_pct = (field_stats['pattern']['present'] / total_items) * 100
    material_pct = (field_stats['material']['present'] / total_items) * 100
    
    avg_critical = (occasion_pct + style_pct + wear_layer_pct + sleeve_pct) / 4
    avg_high_priority = (pattern_pct + material_pct) / 2
    
    overall_score = (avg_critical * 0.7) + (avg_high_priority * 0.3)
    
    print(f"\nCritical Fields Coverage:      {avg_critical:.1f}%")
    print(f"High Priority Fields Coverage: {avg_high_priority:.1f}%")
    print(f"\n🎯 OVERALL METADATA SCORE: {overall_score:.1f}%")
    
    if overall_score >= 90:
        grade = "A - Excellent"
        recommendation = "✅ Metadata is in great shape! Outfit generation should work optimally."
    elif overall_score >= 75:
        grade = "B - Good"
        recommendation = "✅ Good metadata coverage. Consider backfilling remaining items."
    elif overall_score >= 60:
        grade = "C - Fair"
        recommendation = "⚠️  Moderate coverage. Backfill recommended for better outfit quality."
    elif overall_score >= 40:
        grade = "D - Poor"
        recommendation = "⚠️  Low coverage. Backfill HIGHLY recommended."
    else:
        grade = "F - Critical"
        recommendation = "🚨 CRITICAL: Most items lack proper metadata. Backfill REQUIRED."
    
    print(f"Grade: {grade}")
    print(f"\n{recommendation}")
    
    # Export detailed report
    report = {
        'summary': {
            'total_items': total_items,
            'overall_score': round(overall_score, 1),
            'grade': grade,
            'critical_coverage': round(avg_critical, 1),
            'high_priority_coverage': round(avg_high_priority, 1),
        },
        'problems': {
            'empty_occasion_style': len(problems['empty_occasion_style']),
            'occasion_in_tags_not_field': len(problems['occasion_in_tags_not_field']),
            'style_in_tags_not_field': len(problems['style_in_tags_not_field']),
            'missing_visual_attributes': len(problems['missing_visual_attributes']),
            'missing_normalized': len(problems['missing_normalized']),
        },
        'field_coverage': {
            field: {
                'present': stats['present'],
                'missing': stats['missing'],
                'empty': stats['empty'],
                'coverage_pct': round((stats['present'] / total_items) * 100, 1)
            }
            for field, stats in field_stats.items()
        },
        'problem_items': {
            'empty_occasion_style': problems['empty_occasion_style'][:10],
            'occasion_in_tags_not_field': problems['occasion_in_tags_not_field'][:10],
            'style_in_tags_not_field': problems['style_in_tags_not_field'][:10],
        }
    }
    
    report_file = 'comprehensive_metadata_audit_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("="*100)
    
    # Action items
    print("\n🔧 RECOMMENDED ACTIONS:")
    print("-" * 100)
    
    if problems['empty_occasion_style']:
        print(f"1. URGENT: Fix {len(problems['empty_occasion_style'])} items with empty occasion AND style")
        print(f"   These items are INVISIBLE to outfit generation!")
        print(f"   → Run metadata backfill or manually add occasion/style tags")
    
    if problems['occasion_in_tags_not_field']:
        print(f"\n2. Move occasion data from tags to occasion field for {len(problems['occasion_in_tags_not_field'])} items")
        print(f"   → Extract from tags array into structured 'occasion' field")
    
    if problems['style_in_tags_not_field']:
        print(f"\n3. Move style data from tags to style field for {len(problems['style_in_tags_not_field'])} items")
        print(f"   → Extract from tags array into structured 'style' field")
    
    if problems['missing_visual_attributes']:
        print(f"\n4. Add visualAttributes for {len(problems['missing_visual_attributes'])} items")
        print(f"   → Run metadata enhancement backfill (includes pattern, material, fit, layers)")
    
    if problems['missing_normalized']:
        print(f"\n5. Add normalized metadata for {len(problems['missing_normalized'])} items")
        print(f"   → Run normalization backfill for consistent filtering")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    try:
        audit_wardrobe()
    except Exception as e:
        print(f"\n❌ Error running audit: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

