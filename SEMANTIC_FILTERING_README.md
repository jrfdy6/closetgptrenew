# Semantic Filtering Implementation

This implementation adds semantic filtering capabilities to the outfit generation system, allowing for more intelligent matching between requested styles/occasions and available wardrobe items.

## 🎯 Overview

The semantic filtering system provides:
- **Style Compatibility**: Matches items based on semantic relationships (e.g., "business casual" items work for "formal" requests)
- **Mood Compatibility**: Matches items based on mood relationships (e.g., "confident" items work for "bold" requests)
- **Occasion Compatibility**: Matches items based on occasion relationships (e.g., "everyday" items work for "casual" requests)

## 📁 Files Created

### Backend Utilities
- `backend/src/utils/semantic_normalization.py` - Data normalization utilities
- `backend/src/utils/semantic_compatibility.py` - Semantic matching functions
- `backend/src/routes/debug_semantic_filtering.py` - Debug API endpoints

### Frontend Components
- `frontend/src/hooks/useSemanticFlag.ts` - React hook for semantic filtering toggle
- `frontend/src/components/SemanticFilterToggle.tsx` - UI component for toggling semantic filtering

### Scripts
- `scripts/backfill_normalize.py` - Backfill script for existing wardrobe data

### TypeScript Libraries (Reference)
- `lib/normalization.ts` - TypeScript normalization utilities
- `lib/styleMatrix.ts` - Style compatibility matrix
- `lib/compat.ts` - TypeScript semantic matching functions

## 🚀 Usage

### 1. Backend Integration

The semantic filtering is integrated into the `RobustOutfitGenerationService`:

```python
# Enable semantic filtering
debug_result = await robust_service._filter_suitable_items_with_debug(
    context, 
    semantic_filtering=True  # Enable semantic filtering
)
```

### 2. API Endpoints

#### Debug Filtering
```bash
# Test semantic filtering
GET /debug-filter?user_id=123&occasion=formal&style=business&semantic=true

# Compare traditional vs semantic
GET /compare-filtering?user_id=123&occasion=formal&style=business
```

### 3. Frontend Integration

```tsx
import { useSemanticFlag } from '../hooks/useSemanticFlag';
import { SemanticFilterToggle } from '../components/SemanticFilterToggle';

function OutfitGenerator() {
  const { semanticFlag, setSemanticFlag } = useSemanticFlag();
  
  const generateOutfit = async () => {
    const res = await fetch(`/api/outfits/generate?semantic=${semanticFlag}`);
    const { outfits } = await res.json();
  };
  
  return (
    <div>
      <SemanticFilterToggle onToggle={setSemanticFlag} />
      <button onClick={generateOutfit}>Generate Outfit</button>
    </div>
  );
}
```

## 🔧 Configuration

### Style Compatibility Matrix

The system uses predefined compatibility relationships:

```python
STYLE_COMPATIBILITY = {
    'classic': ['classic', 'casual', 'smart casual', 'business casual', 'traditional'],
    'casual': ['casual', 'classic', 'streetwear', 'athleisure', 'relaxed', 'everyday'],
    'business': ['business', 'business casual', 'professional', 'smart casual'],
    'formal': ['formal', 'elegant', 'semi-formal', 'business'],
    # ... more styles
}
```

### Custom Overrides

You can override the compatibility matrix by passing custom compatible styles:

```python
context = {
    "style": "formal",
    "style_matrix": {
        "compatible_styles": ["formal", "black tie", "white tie"],
        "enable_style_overlap": True
    }
}
```

## 📊 Data Normalization

### Normalize Item Metadata

```python
from utils.semantic_normalization import normalize_item_metadata

# Normalize item for semantic filtering
normalized_item = normalize_item_metadata(raw_item)
```

### Backfill Existing Data

```bash
# Run the backfill script
python scripts/backfill_normalize.py
```

## 🧪 Testing

### 1. Debug Endpoints

Test the semantic filtering with the debug endpoints:

```bash
# Test with semantic filtering enabled
curl "http://localhost:8000/debug-filter?user_id=test&occasion=formal&style=business&semantic=true"

# Compare both modes
curl "http://localhost:8000/compare-filtering?user_id=test&occasion=formal&style=business"
```

### 2. Frontend Testing

Use the toggle component to test semantic filtering in the UI:

```tsx
<SemanticFilterToggle 
  onToggle={(enabled) => console.log('Semantic filtering:', enabled)} 
/>
```

## 🔄 Migration Strategy

### Phase 1: Deploy with Feature Flag
- Deploy all code with semantic filtering disabled by default
- Test with debug endpoints

### Phase 2: Gradual Rollout
- Enable semantic filtering for specific user segments
- Monitor performance and accuracy

### Phase 3: Full Rollout
- Enable semantic filtering by default
- Remove feature flag

## 📈 Expected Improvements

- **Higher Success Rate**: More items pass filtering due to semantic compatibility
- **Better User Experience**: More relevant outfit suggestions
- **Reduced False Negatives**: Items that should work for a request are no longer rejected

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all utility files are in the correct paths
2. **Firebase Permissions**: Check Firestore permissions for backfill script
3. **Performance**: Monitor query performance with large wardrobes

### Debug Mode

Enable debug logging to see filtering decisions:

```python
import logging
logging.getLogger('robust_outfit_generation_service').setLevel(logging.DEBUG)
```

## 🔮 Future Enhancements

- **Machine Learning**: Learn compatibility relationships from user feedback
- **Personalization**: User-specific compatibility matrices
- **Dynamic Updates**: Real-time updates to compatibility rules
- **A/B Testing**: Compare different compatibility matrices

## 📝 Notes

- The semantic filtering is backward compatible - existing functionality remains unchanged
- The system gracefully falls back to traditional filtering if semantic filtering fails
- All compatibility matrices can be easily updated without code changes
- The system is designed to be performant with large wardrobes
