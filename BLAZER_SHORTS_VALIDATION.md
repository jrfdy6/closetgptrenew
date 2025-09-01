# Blazer + Shorts Validation Rule Integration

## Problem
The outfit generation system was creating inappropriate combinations like **blazer + shorts**, which are generally not acceptable in most contexts.

## Solution
I've created a comprehensive validation service that prevents inappropriate clothing combinations.

## Validation Rules Added

### 1. Blazer + Shorts Prevention
```python
"blazer_shorts": {
    "description": "Blazer + Shorts",
    "reason": "Blazers are formal wear and should not be paired with casual shorts",
    "remove_items": ["shorts", "athletic shorts", "basketball shorts"],
    "keep_items": ["blazer", "suit jacket", "sport coat"]
}
```

### 2. Formal Jacket + Casual Shorts
```python
"formal_jacket_casual_shorts": {
    "description": "Formal Jacket + Casual Shorts", 
    "reason": "Formal jackets require more formal bottoms",
    "remove_items": ["shorts", "athletic shorts", "basketball shorts"],
    "keep_items": ["blazer", "suit jacket", "sport coat", "coat"]
}
```

### 3. Business + Athletic Wear
```python
"business_athletic": {
    "description": "Business Wear + Athletic Wear",
    "reason": "Business items should not be mixed with athletic wear",
    "remove_items": ["athletic shorts", "basketball shorts", "sweatpants", "athletic pants"],
    "keep_items": ["blazer", "suit", "dress shirt", "dress pants"]
}
```

### 4. Formal Shoes + Casual Shorts
```python
"formal_shoes_casual_shorts": {
    "description": "Formal Shoes + Casual Shorts",
    "reason": "Formal shoes require more formal bottoms",
    "remove_items": ["shorts", "athletic shorts"],
    "keep_items": ["oxford", "loafers", "dress shoes", "heels"]
}
```

## Integration Steps

### 1. Import the Validation Service
```python
from src.services.outfit_validation_service import OutfitValidationService
```

### 2. Initialize in Your Service
```python
class YourOutfitService:
    def __init__(self):
        self.validation_service = OutfitValidationService()
```

### 3. Add Validation to Outfit Generation
```python
def generate_outfit(self, items, occasion):
    # ... your existing logic ...
    
    # Add validation after item selection
    print(f"🔍 Running outfit validation...")
    validated_items = self.validation_service.validate_outfit(items)
    
    # Add occasion-specific validation
    validated_items = self.validation_service.validate_by_occasion(validated_items, occasion)
    
    return validated_items
```

## Expected Behavior

### Before Validation
- Blazer + Shorts ❌
- Formal Jacket + Athletic Shorts ❌
- Business Blazer + Sweatpants ❌
- Oxford Shoes + Casual Shorts ❌

### After Validation
- Blazer + Pants ✅
- Formal Jacket + Dress Pants ✅
- Business Blazer + Dress Pants ✅
- Oxford Shoes + Dress Pants ✅

## Occasion-Specific Validation

The service also includes occasion-based validation:

### Business/Work Occasions
- Removes: Athletic shorts, basketball shorts, sweatpants
- Keeps: Professional items

### Formal/Interview Occasions
- Removes: Shorts, t-shirts, sneakers, hoodies, jeans
- Keeps: Formal items

### Athletic/Gym Occasions
- Removes: Blazers, suits, dress shirts, dress pants, oxfords, heels
- Keeps: Athletic items

## Usage Example

```python
# Initialize validation service
validation_service = OutfitValidationService()

# Validate an outfit
items = [blazer, shorts, pants, shoes]  # Inappropriate combination
validated_items = validation_service.validate_outfit(items)

# Result: [blazer, pants, shoes] - shorts removed
```

## Custom Rules

You can add custom validation rules:

```python
custom_rule = {
    "description": "Custom Rule",
    "reason": "Custom reason",
    "remove_items": ["item_type_1", "item_type_2"],
    "keep_items": ["item_type_3", "item_type_4"]
}

validation_service.add_custom_rule("custom_rule_name", custom_rule)
```

## Benefits

1. **Prevents Inappropriate Combinations**: No more blazer + shorts
2. **Maintains Style Consistency**: Ensures outfits make sense
3. **Occasion-Appropriate**: Validates based on the specific occasion
4. **Extensible**: Easy to add new validation rules
5. **Clear Logging**: Shows what was removed and why

## Files Created

1. `backend/src/services/outfit_validation_service.py` - Main validation service
2. `BLAZER_SHORTS_VALIDATION.md` - This integration guide

## Next Steps

1. Integrate the validation service into your existing outfit generation
2. Test with various combinations to ensure it works correctly
3. Add any additional custom rules specific to your use case
4. Monitor user feedback and adjust rules as needed
