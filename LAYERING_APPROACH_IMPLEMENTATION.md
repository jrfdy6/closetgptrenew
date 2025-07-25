# Layering Approach Implementation

## Overview

This document describes the implementation of an improved layering approach for outfit generation that uses core category mapping with subtype/tags for better flexibility and layering support.

## Key Features

### 1. Core Category Mapping
Items are mapped to core categories that are essential for outfit structure:
- **Top**: Shirts, blouses, sweaters, etc.
- **Bottom**: Pants, jeans, skirts, etc.
- **Dress**: Complete dresses (sundress, cocktail dress, etc.)
- **Outerwear**: Jackets, coats, blazers, etc.
- **Shoes**: All footwear types
- **Accessory**: Hats, scarves, jewelry, etc.

### 2. Layer Level Classification
Items are classified by their layering position:
- **Base**: T-shirts, tank tops, underwear
- **Inner**: Shirts, blouses, polos
- **Middle**: Sweaters, cardigans, vests
- **Outer**: Jackets, coats, blazers

### 3. Warmth Factor
Items are categorized by their warmth level:
- **Light**: T-shirts, shorts, sandals
- **Medium**: Shirts, pants, sweaters
- **Heavy**: Jackets, coats, heavy sweaters

### 4. Layering Capabilities
- **Can Layer**: Whether an item can be layered with others
- **Max Layers**: Maximum number of layers an item can support

## Implementation Details

### Backend Changes

#### 1. Enhanced Clothing Types (`backend/src/types/wardrobe.py`)
Added comprehensive clothing types:
```python
class ClothingType(str, Enum):
    # Core types
    SHIRT = "shirt"
    T_SHIRT = "t-shirt"
    BLOUSE = "blouse"
    SWEATER = "sweater"
    HOODIE = "hoodie"
    CARDIGAN = "cardigan"
    # ... and many more
```

#### 2. New Layering Enums
```python
class LayerLevel(str, Enum):
    BASE = "base"
    INNER = "inner"
    MIDDLE = "middle"
    OUTER = "outer"

class WarmthFactor(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"

class CoreCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORY = "accessory"
```

#### 3. Enhanced Visual Attributes
Added layering properties to `VisualAttributes`:
```python
class VisualAttributes(BaseModel):
    # ... existing fields ...
    layerLevel: Optional[LayerLevel] = None
    warmthFactor: Optional[WarmthFactor] = None
    coreCategory: Optional[CoreCategory] = None
    canLayer: Optional[bool] = None
    maxLayers: Optional[int] = None
```

#### 4. Layering Utility (`backend/src/utils/layering.py`)
Comprehensive utility functions for layering logic:
- `get_core_category()`: Maps clothing types to core categories
- `get_layer_level()`: Determines layer level for items
- `get_warmth_factor()`: Gets warmth factor for temperature-based decisions
- `can_layer()`: Checks if an item can be layered
- `get_max_layers()`: Gets maximum layers an item can support
- `get_layering_rule()`: Temperature-based layering rules
- `validate_layering_compatibility()`: Validates outfit layering
- `get_layering_suggestions()`: Provides layering suggestions

### Frontend Changes

#### 1. Enhanced Type Definitions (`shared/types.ts`)
Added new enums and enhanced `ClothingTypeEnum`:
```typescript
export const ClothingTypeEnum = z.enum([
  'shirt', 't-shirt', 'blouse', 'sweater', 'hoodie', 'cardigan',
  'pants', 'jeans', 'shorts', 'skirt', 'dress', 'jacket', 'coat',
  // ... comprehensive list
]);

export const LayerLevelEnum = z.enum(['base', 'inner', 'middle', 'outer']);
export const WarmthFactorEnum = z.enum(['light', 'medium', 'heavy']);
export const CoreCategoryEnum = z.enum(['top', 'bottom', 'dress', 'outerwear', 'shoes', 'accessory']);
```

#### 2. Layering Utility (`shared/utils/layering.ts`)
Frontend utility with the same functionality as backend:
- Comprehensive mappings for all clothing types
- Temperature-based layering rules
- Validation and suggestion functions

#### 3. Enhanced Validation (`shared/utils/validation.ts`)
Updated validation to use core categories:
```typescript
export const normalizeClothingType = (type: string | null | undefined): ClothingType => {
  // Enhanced mapping with specific types
  const type_mapping = {
    "t-shirt": ClothingType.T_SHIRT,
    "blouse": ClothingType.BLOUSE,
    "jeans": ClothingType.JEANS,
    // ... comprehensive mapping
  };
};
```

## Temperature-Based Layering Rules

The system implements intelligent temperature-based layering:

| Temperature | Min Layers | Max Layers | Preferred Warmth | Notes |
|-------------|------------|------------|------------------|-------|
| < 32°F | 3 | 5 | Medium, Heavy | Heavy layering required |
| 32-50°F | 2 | 4 | Medium, Heavy | Medium layering |
| 50-65°F | 1 | 3 | Light, Medium | Light layering |
| 65-75°F | 1 | 2 | Light, Medium | Single layer |
| 75-85°F | 1 | 2 | Light | Light, breathable |
| > 85°F | 1 | 1 | Light | Minimal clothing |

## Benefits of This Approach

### 1. **Flexibility**
- Any clothing type can be recognized and mapped to core categories
- Subtype and tags provide additional context
- Easy to add new clothing types without breaking existing logic

### 2. **Layering Support**
- Explicit layer level classification
- Temperature-based layering rules
- Validation of layering compatibility
- Intelligent suggestions for missing layers

### 3. **Temperature Awareness**
- Warmth factor classification
- Temperature-appropriate outfit generation
- Weather-based validation and suggestions

### 4. **Maintainability**
- Clear separation of concerns
- Comprehensive utility functions
- Easy to extend and modify

## Usage Examples

### 1. Core Category Mapping
```python
# Backend
from utils.layering import get_core_category
category = get_core_category(ClothingType.T_SHIRT)  # Returns CoreCategory.TOP

# Frontend
import { getCoreCategory } from '@shared/utils/layering';
const category = getCoreCategory('t-shirt');  // Returns 'top'
```

### 2. Layering Validation
```python
# Backend
from utils.layering import validate_layering_compatibility
outfit = [{"type": "t-shirt"}, {"type": "sweater"}, {"type": "jacket"}]
validation = validate_layering_compatibility(outfit, 30)  # Cold weather
print(validation['is_valid'])  # True
print(validation['warnings'])  # ['t-shirt may be too light for 30°F weather']
```

### 3. Layering Suggestions
```python
# Backend
from utils.layering import get_layering_suggestions
outfit = [{"type": "t-shirt"}, {"type": "pants"}]
suggestions = get_layering_suggestions(outfit, 25)  # Cold weather
print(suggestions)  # ['Add 2 more layer(s) for 25°F weather', 'Add a outerwear item for complete outfit']
```

## Testing

A comprehensive test script (`test_layering_approach.py`) demonstrates all features:

```bash
python test_layering_approach.py
```

The test covers:
- Core category mapping
- Layer level classification
- Warmth factor mapping
- Layering capabilities
- Temperature-based rules
- Validation and suggestions
- Comprehensive outfit examples

## Future Enhancements

### 1. **Material-Based Layering**
- Consider material properties in layering decisions
- Material compatibility validation
- Fabric weight considerations

### 2. **Style-Based Layering**
- Style-specific layering rules
- Fashion trend considerations
- Occasion-based layering adjustments

### 3. **Personalization**
- User preference learning
- Body type considerations
- Comfort level preferences

### 4. **Advanced Validation**
- Pattern mixing validation
- Color harmony with layering
- Seasonal appropriateness

## Conclusion

This layering approach provides a robust foundation for outfit generation that:
- Recognizes any clothing item effectively
- Supports sophisticated layering logic
- Provides temperature-aware recommendations
- Maintains flexibility for future enhancements
- Ensures complete and appropriate outfits

The implementation is conducive for layering because it explicitly models layer relationships, temperature considerations, and provides validation and suggestions to ensure proper outfit composition. 