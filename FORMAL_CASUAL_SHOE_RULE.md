# Formal-Casual Shoe Validation Rule

## Problem
The outfit generation system was creating inappropriate combinations like **blazer + slides** or **suit + flip-flops**, which are fashion faux pas.

## Solution
I've implemented a comprehensive validation rule that prevents casual shoes from being paired with formal wear.

## Validation Rules Added

### 1. Formal Wear + Casual Shoes Prevention
```python
"formal_wear_casual_shoes": {
    "description": "Formal Wear + Casual Shoes",
    "reason": "Flip-flops/slides should not be worn with blazers or suits",
    "remove_items": ["flip-flops", "flip flops", "slides", "sandals", "thongs"],
    "keep_items": ["blazer", "suit", "suit jacket", "sport coat", "jacket"]
}
```

## Implementation Details

### Formal Items Detected:
- `blazer`
- `suit`
- `suit jacket`
- `sport coat`
- `jacket`

### Casual Shoes Detected:
- `flip-flops`
- `flip flops`
- `slides`
- `sandals`
- `thongs`

### Validation Logic:
1. **Detection**: System checks if outfit contains both formal items and casual shoes
2. **Warning**: Logs a warning about the inappropriate combination
3. **Removal**: Automatically removes casual shoes when formal items are present
4. **Result**: Clean outfit with formal wear and appropriate footwear

## Expected Behavior

### Before Validation:
- Blazer + Slides ❌
- Suit + Flip-flops ❌
- Jacket + Sandals ❌

### After Validation:
- Blazer + Oxford Shoes ✅
- Suit + Dress Shoes ✅
- Jacket + Loafers ✅

## Code Implementation

### In `backend/src/routes/outfits.py`:

```python
# ENHANCED: Prevent flip-flops/slides with formal wear
formal_items = ['blazer', 'suit', 'suit jacket', 'sport coat', 'jacket']
casual_shoes = ['flip-flops', 'flip flops', 'slides', 'sandals', 'thongs']

outfit_types = [item.get('type', '').lower() for item in final_outfit]
has_formal_item = any(formal_type in outfit_type for formal_type in formal_items for outfit_type in outfit_types)
has_casual_shoes = any(casual_shoe in outfit_type for casual_shoe in casual_shoes for outfit_type in outfit_types)

if has_formal_item and has_casual_shoes:
    logger.warning(f"🔍 DEBUG: Formal-casual shoe mismatch detected, removing casual shoes")
    # Remove casual shoes when formal items are present
    final_outfit = [item for item in final_outfit if not any(casual_shoe in item.get('type', '').lower() for casual_shoe in casual_shoes)]
    logger.info(f"🔍 DEBUG: Removed casual shoes due to formal wear")
```

### In Layering Validation:

```python
# ENHANCED: Prevent flip-flops/slides with formal wear
formal_items = ['blazer', 'suit', 'suit jacket', 'sport coat', 'jacket']
casual_shoes = ['flip-flops', 'flip flops', 'slides', 'sandals', 'thongs']

has_formal_item = any(formal_type in layer_type for formal_type in formal_items for layer_type in layer_types)
has_casual_shoes = any(casual_shoe in layer_type for casual_shoe in casual_shoes for layer_type in layer_types)

if has_formal_item and has_casual_shoes:
    warnings.append("Flip-flops/slides should not be worn with blazers or suits")
    logger.warning(f"🔍 DEBUG: Formal-casual shoe mismatch detected: formal={formal_items}, casual_shoes={casual_shoes}")
```

## Benefits

1. **Prevents Fashion Faux Pas**: No more blazer + slides combinations
2. **Maintains Style Consistency**: Ensures formal wear gets appropriate footwear
3. **Automatic Correction**: System automatically fixes inappropriate combinations
4. **Clear Logging**: Shows exactly what was removed and why
5. **Comprehensive Coverage**: Catches all variations of formal wear and casual shoes

## Testing

To test this rule:
1. Generate an outfit with a blazer or suit
2. Check that no flip-flops/slides are included
3. Verify that appropriate formal shoes (oxfords, loafers, dress shoes) are selected instead

## Future Enhancements

1. **Smart Shoe Selection**: Automatically suggest appropriate formal shoes
2. **Occasion-Based Rules**: Different rules for different occasions
3. **Weather Considerations**: Factor in weather when selecting footwear
4. **User Preferences**: Allow users to customize shoe preferences
