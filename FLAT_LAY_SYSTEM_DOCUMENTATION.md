# ClosetGPT Flat Lay Image Generation System

## Overview

The Flat Lay System automatically creates professional, styled flat lay images of complete outfits using the user's actual wardrobe item images. This provides a realistic, cohesive visualization that helps users see exactly how their outfit will look when arranged together.

## 🎨 Features

### Core Capabilities
- **Automatic Image Composition**: Combines individual wardrobe item images into a single flat lay
- **Smart Positioning**: Uses category-based templates for natural item arrangement
- **Background Removal**: Removes backgrounds from item images for clean composition
- **Shadow Effects**: Adds realistic drop shadows for depth and professionalism
- **Image Enhancement**: Applies sharpening, contrast, and color adjustments
- **Firebase Storage**: Automatically uploads and stores flat lay images
- **Frontend Display**: Beautiful viewer with fullscreen, download, and share capabilities

### Technical Features
- **Async Processing**: Non-blocking image generation pipeline
- **Error Handling**: Graceful fallback if flat lay generation fails
- **Feature Flag**: Easy toggle to enable/disable flat lay generation
- **Multi-format Support**: PNG (with transparency) and JPEG output
- **Configurable Layout**: Customizable canvas size, positions, and scales

---

## 📁 Architecture

### Backend Components

#### 1. **FlatLayCompositionService** (`backend/src/services/flat_lay_composition_service.py`)
The core service that creates flat lay images.

**Key Methods:**
```python
async def create_flat_lay(
    outfit_items: List[ClothingItem],
    outfit_id: str,
    output_format: str = "PNG"
) -> Tuple[Optional[Image.Image], Optional[str]]
```

**Features:**
- Downloads and preprocesses item images
- Categorizes items (top, bottom, shoes, accessories, etc.)
- Calculates positions and scales based on categories
- Composes all items onto a canvas with shadows
- Returns PIL Image object

**Category Scales:**
```python
{
    'TOP': 1.0,         # Full size
    'BOTTOM': 0.9,      # Slightly smaller
    'DRESS': 1.2,       # Larger (dress-only outfits)
    'OUTERWEAR': 1.1,   # Slightly larger
    'SHOES': 0.7,       # Smaller
    'ACCESSORY': 0.4,   # Much smaller
    'BAG': 0.6,         # Medium-small
    'HAT': 0.5          # Small
}
```

**Position Template:**
```python
{
    'TOP': (0.5, 0.28),       # Center-top
    'BOTTOM': (0.5, 0.60),    # Center-middle
    'DRESS': (0.5, 0.45),     # Center
    'OUTERWEAR': (0.5, 0.25), # Above top
    'SHOES': (0.5, 0.85),     # Bottom center
    'ACCESSORY': (0.25, 0.30),# Left side
    'BAG': (0.75, 0.50),      # Right side
    'HAT': (0.25, 0.15)       # Top left
}
```

#### 2. **FlatLayStorageService** (`backend/src/services/flat_lay_storage_service.py`)
Handles uploading flat lay images to Firebase Storage.

**Key Methods:**
```python
async def upload_flat_lay(
    image: Image.Image,
    outfit_id: str,
    user_id: str,
    format: str = "PNG"
) -> Optional[str]
```

**Storage Path Structure:**
```
flat_lays/
  └── {user_id}/
      └── {outfit_id}_{timestamp}.png
```

#### 3. **Image Processing Utilities** (`backend/src/utils/image_processing.py`)
Advanced image processing functions for professional results.

**Key Functions:**
- `remove_background_advanced()` - Smart background removal with edge smoothing
- `enhance_image_quality()` - Sharpening, contrast, and color enhancement
- `add_drop_shadow()` - Realistic shadow effects
- `create_realistic_shadow()` - Directional shadows with angle control
- `auto_crop_transparent()` - Remove excess transparent space
- `add_subtle_texture()` - Canvas background texture
- `apply_vignette()` - Focus-drawing vignette effect

### Frontend Components

#### 1. **FlatLayViewer** (`frontend/src/components/FlatLayViewer.tsx`)
React component for displaying flat lay images.

**Features:**
- Responsive flat lay display (9:16 aspect ratio)
- Toggle between flat lay and grid view
- Fullscreen viewing mode
- Download functionality
- Share capability (native share API + clipboard fallback)
- Loading states and error handling
- Item grid fallback view

**Props:**
```typescript
interface FlatLayViewerProps {
  flatLayUrl?: string | null;
  outfitName?: string;
  outfitItems?: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
  }>;
  className?: string;
  showItemGrid?: boolean;
  onViewChange?: (view: 'flat-lay' | 'grid') => void;
}
```

#### 2. **OutfitResultsDisplay** Integration
The flat lay viewer is integrated into the outfit results display component, showing the flat lay automatically when available.

---

## 🔧 Configuration

### FlatLayConfig

```python
@dataclass
class FlatLayConfig:
    canvas_width: int = 1080           # Canvas width in pixels
    canvas_height: int = 1920          # Canvas height in pixels (9:16 ratio)
    background_color: Tuple = (245, 245, 245, 255)  # Light gray
    shadow_enabled: bool = True        # Enable drop shadows
    shadow_blur: int = 15              # Shadow blur radius
    shadow_offset: Tuple = (10, 10)   # Shadow offset (x, y)
    shadow_opacity: int = 40           # Shadow opacity (0-255)
    item_spacing: int = 50             # Spacing between items
    max_item_width: int = 400          # Max item width
    max_item_height: int = 500         # Max item height
```

### Feature Flag

In `OutfitGenerationService.__init__()`:
```python
self.enable_flat_lay_generation = True  # Toggle flat lay generation
```

---

## 🚀 Integration

### Backend Integration

The flat lay generation is integrated into the outfit generation pipeline:

```python
# In outfit_generation_service.py
outfit = await self._create_outfit_from_items(...)

# Generate flat lay image
if self.enable_flat_lay_generation and selected_items:
    flat_lay_url = await self._generate_and_store_flat_lay(
        outfit_items=selected_items,
        outfit_id=outfit.id,
        user_id=user_id
    )
    
    if flat_lay_url:
        outfit.metadata['flat_lay_url'] = flat_lay_url
```

### Firestore Data Structure

Flat lay URLs are stored in outfit records:

```json
{
  "id": "outfit_123",
  "name": "Casual Friday Look",
  "items": [...],
  "metadata": {
    "flat_lay_url": "https://storage.googleapis.com/bucket/flat_lays/user_123/outfit_123_20250105.png",
    "generation_strategy": "cohesive_composition",
    ...
  }
}
```

### Frontend Usage

```tsx
<FlatLayViewer
  flatLayUrl={outfit.metadata?.flat_lay_url}
  outfitName={outfit.name}
  outfitItems={outfit.items}
  showItemGrid={true}
/>
```

---

## 🎯 Workflow

### 1. Outfit Generation
```
User Request → Outfit Generation Service → Cohesive Outfit Composition
```

### 2. Flat Lay Creation
```
Selected Items → Download Images → Remove Backgrounds → Scale & Position → Compose → Add Shadows
```

### 3. Storage & Display
```
PIL Image → Firebase Storage → Public URL → Firestore Metadata → Frontend Display
```

---

## 📊 Performance Considerations

### Optimization Strategies

1. **Async Processing**: All image operations are async to avoid blocking
2. **Lazy Loading**: Images are downloaded only when needed
3. **Caching**: Firebase Storage provides CDN caching
4. **Error Resilience**: Flat lay generation failure doesn't break outfit generation
5. **Size Limits**: Max item dimensions prevent memory issues

### Typical Generation Times

- **2-3 items**: ~2-3 seconds
- **4-5 items**: ~3-5 seconds
- **6+ items**: ~5-8 seconds

*Times include download, processing, and upload*

---

## 🔍 Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

#### 1. Background Not Removed
**Issue**: White backgrounds not becoming transparent
**Solution**: Adjust threshold in `remove_background_advanced()`:
```python
remove_background_advanced(image, threshold=240, edge_blur=2)
```

#### 2. Items Too Large/Small
**Issue**: Poor item scaling
**Solution**: Adjust category scales in `FlatLayCompositionService`:
```python
self.category_scales = {
    ItemCategory.TOP: 1.0,  # Increase/decrease as needed
    ...
}
```

#### 3. Poor Positioning
**Issue**: Items overlap or look misaligned
**Solution**: Adjust position templates:
```python
self.category_positions = {
    ItemCategory.TOP: (0.5, 0.30),  # Move up/down
    ...
}
```

#### 4. Firebase Upload Fails
**Issue**: Flat lay not appearing in UI
**Solution**: Check Firebase Storage permissions and bucket configuration

---

## 🎨 Customization Examples

### 1. Change Canvas Background

```python
config = FlatLayConfig(
    background_color=(255, 255, 255, 255)  # Pure white
)
flat_lay_service = FlatLayCompositionService(config)
```

### 2. Disable Shadows

```python
config = FlatLayConfig(
    shadow_enabled=False
)
```

### 3. Adjust Shadow Style

```python
config = FlatLayConfig(
    shadow_blur=20,              # More blur
    shadow_offset=(15, 15),      # Larger offset
    shadow_opacity=60            # Darker shadow
)
```

### 4. Add Canvas Texture

```python
from src.utils.image_processing import add_subtle_texture

canvas = add_subtle_texture(canvas, texture_strength=0.05)
```

---

## 🚦 Testing

### Unit Tests

```python
# Test flat lay creation
async def test_flat_lay_creation():
    service = FlatLayCompositionService()
    items = [...]  # Mock clothing items
    
    image, error = await service.create_flat_lay(
        outfit_items=items,
        outfit_id="test_123"
    )
    
    assert image is not None
    assert error is None
    assert image.size == (1080, 1920)
```

### Integration Tests

```python
# Test full pipeline
async def test_outfit_with_flat_lay():
    outfit_service = OutfitGenerationService()
    outfit_service.enable_flat_lay_generation = True
    
    outfit = await outfit_service.generate_outfit(...)
    
    assert outfit.metadata.get('flat_lay_url') is not None
```

---

## 📝 Future Enhancements

### Planned Features

1. **AI Background Removal**: Integrate `rembg` for better background removal
2. **Custom Templates**: User-selectable layout templates
3. **Animation**: Animated outfit assembly
4. **3D Mockups**: Outfit on 3D mannequin
5. **AR Preview**: Try outfit in AR
6. **Batch Generation**: Generate flat lays for multiple outfits
7. **Style Filters**: Instagram-style filters for flat lays
8. **Watermarking**: Optional branding/watermarks

### Advanced Image Processing

- **Smart Cropping**: ML-based item cropping
- **Color Correction**: Auto color balance
- **Lighting Adjustment**: Unified lighting across items
- **Fabric Simulation**: Realistic fabric draping
- **Shadow Diversity**: Multiple shadow styles

---

## 📚 Dependencies

### Python (Backend)
```
Pillow==10.0.1          # Image processing
numpy==2.2.6            # Array operations
requests==2.32.5        # Image downloading
firebase-admin==6.2.0   # Firebase Storage
```

### TypeScript (Frontend)
```
react                   # UI framework
lucide-react           # Icons
```

---

## 🤝 Contributing

### Adding New Item Categories

1. Add to `ItemCategory` enum in `flat_lay_composition_service.py`
2. Add scale to `category_scales`
3. Add position to `category_positions`
4. Update `_get_item_category()` mapping

### Adding New Image Effects

1. Add function to `image_processing.py`
2. Document parameters and usage
3. Add to composition pipeline in `_compose_items()`

---

## 📞 Support

For issues or questions about the Flat Lay System:

1. Check debug logs with `logger.setLevel(logging.DEBUG)`
2. Verify Firebase Storage permissions
3. Test with simple 2-item outfits first
4. Check image URLs are valid and accessible

---

## 🎉 Success Metrics

The Flat Lay System is working correctly when:

✅ Flat lay images appear in outfit generation results
✅ Images load quickly (< 3 seconds for typical outfit)
✅ Items are properly positioned without overlap
✅ Backgrounds are clean and transparent
✅ Shadows look realistic and add depth
✅ Download and share functions work
✅ Grid view toggle functions correctly
✅ Fullscreen mode displays properly

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Author**: ClosetGPT Development Team

