#!/usr/bin/env python3
"""
Show the expected wardrobe item structure based on the upload code
"""

def show_wardrobe_structure():
    """Show what fields are in a wardrobe item based on the upload code"""
    
    print("🔍 WARDROBE ITEM STRUCTURE")
    print("=" * 60)
    print("Based on the upload code analysis, here are ALL the fields in your wardrobe items:")
    print()
    
    # Core fields (always present)
    print("📋 CORE FIELDS (Always Present):")
    print("-" * 40)
    core_fields = [
        ("id", "string", "Unique item identifier"),
        ("userId", "string", "Your user ID (dANqjiI0CKgaitxzYtw1bhtvQrG3)"),
        ("name", "string", "Item name (from AI analysis or manual input)"),
        ("type", "string", "Item type (shirt, pants, shoes, etc.)"),
        ("color", "string", "Primary color"),
        ("imageUrl", "string", "URL to item image"),
        ("createdAt", "integer", "Timestamp when item was added"),
        ("updatedAt", "integer", "Timestamp when item was last updated"),
        ("favorite", "boolean", "Whether item is marked as favorite"),
        ("wearCount", "integer", "Number of times item has been worn"),
        ("lastWorn", "integer|null", "Timestamp of last wear or null")
    ]
    
    for field, field_type, description in core_fields:
        print(f"  🔹 {field}: {field_type} - {description}")
    
    print()
    print("📋 ARRAY FIELDS (From AI Analysis):")
    print("-" * 40)
    array_fields = [
        ("style", "array", "Style tags (casual, formal, athletic, etc.)"),
        ("occasion", "array", "Occasion tags (business, casual, athletic, etc.)"),
        ("season", "array", "Season tags (spring, summer, fall, winter)"),
        ("tags", "array", "Additional tags"),
        ("dominantColors", "array", "Color analysis results"),
        ("matchingColors", "array", "Matching color suggestions")
    ]
    
    for field, field_type, description in array_fields:
        print(f"  🔹 {field}: {field_type} - {description}")
    
    print()
    print("📁 METADATA OBJECT (Complex Structure):")
    print("-" * 40)
    print("  metadata: {")
    print("    🔹 analysisTimestamp: integer - When AI analysis was performed")
    print("    🔹 originalType: string - Original type from upload")
    print("    🔹 styleTags: array - Style tags from AI")
    print("    🔹 occasionTags: array - Occasion tags from AI")
    print("    🔹 colorAnalysis: {")
    print("        🔹 dominant: array - Dominant colors")
    print("        🔹 matching: array - Matching colors")
    print("    }")
    print("    🔹 visualAttributes: {")
    print("        🔹 pattern: string - Pattern type (solid, striped, etc.)")
    print("        🔹 formalLevel: string - Formality level (casual, formal)")
    print("        🔹 fit: string - Fit type (loose, fitted, etc.)")
    print("        🔹 material: string - Material type")
    print("        🔹 fabricWeight: string - Weight (light, medium, heavy)")
    print("    }")
    print("    🔹 itemMetadata: {")
    print("        🔹 tags: array - Additional tags")
    print("        🔹 careInstructions: string - Care instructions")
    print("    }")
    print("    🔹 aiAnalysis: object - Full AI analysis results")
    print("  }")
    
    print()
    print("📋 OPTIONAL FIELDS (May Be Present):")
    print("-" * 40)
    optional_fields = [
        ("brand", "string", "Brand name if detected"),
        ("material", "string", "Material type"),
        ("subType", "string", "More specific type (t-shirt, jeans, etc.)"),
        ("gender", "string", "Gender target (men's, women's, unisex)"),
        ("backgroundRemoved", "boolean", "Whether background was removed"),
        ("fileSize", "integer", "Original file size"),
        ("imageHash", "string", "Hash for duplicate detection")
    ]
    
    for field, field_type, description in optional_fields:
        print(f"  🔹 {field}: {field_type} - {description}")
    
    print()
    print("🎯 KEY FIELDS FOR OUTFIT GENERATION:")
    print("-" * 40)
    key_fields = [
        "name", "type", "color", "style", "occasion", "season", 
        "brand", "material", "metadata.visualAttributes.formalLevel"
    ]
    
    for field in key_fields:
        print(f"  ✅ {field}")
    
    print()
    print("💡 WHAT THIS MEANS FOR FILTERING:")
    print("-" * 40)
    print("✅ The 'occasion' field IS populated from AI analysis")
    print("✅ The 'style' field IS populated from AI analysis") 
    print("✅ The 'type' field is always present")
    print("✅ The 'name' field is always present")
    print("✅ Brand information may be present")
    print()
    print("🔧 CURRENT FILTERING APPROACH:")
    print("- Uses 'type' field (always present)")
    print("- Uses 'name' field (always present)")
    print("- Checks 'occasion' field if populated")
    print("- Uses brand recognition patterns")
    print("- Defaults to allowing items (conservative approach)")
    
    print()
    print("✅ This structure should work perfectly with our improved filtering logic!")

if __name__ == "__main__":
    show_wardrobe_structure()

