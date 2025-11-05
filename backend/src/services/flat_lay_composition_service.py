#!/usr/bin/env python3
"""
Flat Lay Composition Service
Creates professional flat lay images from outfit item images
"""

import io
import logging
import requests
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from enum import Enum

from src.custom_types.wardrobe import ClothingItem

logger = logging.getLogger(__name__)


class ItemCategory(Enum):
    """Clothing item categories for positioning"""
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORY = "accessory"
    BAG = "bag"
    HAT = "hat"


@dataclass
class LayoutPosition:
    """Position and scale for an item in the flat lay"""
    x: int  # X coordinate (center point)
    y: int  # Y coordinate (center point)
    scale: float  # Scale factor relative to base size
    rotation: int = 0  # Rotation in degrees
    layer: int = 0  # Z-index for layering


@dataclass
class FlatLayConfig:
    """Configuration for flat lay generation"""
    canvas_width: int = 1080
    canvas_height: int = 1350  # Changed from 1920 to make it less tall (4:3 ratio)
    background_color: Tuple[int, int, int, int] = (245, 245, 245, 255)  # Light gray
    shadow_enabled: bool = True
    shadow_blur: int = 15
    shadow_offset: Tuple[int, int] = (10, 10)
    shadow_opacity: int = 40
    item_spacing: int = 50
    max_item_width: int = 400
    max_item_height: int = 500


class FlatLayCompositionService:
    """Service for composing flat lay outfit images"""
    
    def __init__(self, config: Optional[FlatLayConfig] = None):
        self.config = config or FlatLayConfig()
        
        # Define scale factors for each category
        self.category_scales = {
            ItemCategory.TOP: 1.0,
            ItemCategory.BOTTOM: 0.9,
            ItemCategory.DRESS: 1.2,
            ItemCategory.OUTERWEAR: 1.1,
            ItemCategory.SHOES: 0.7,
            ItemCategory.ACCESSORY: 0.4,
            ItemCategory.BAG: 0.6,
            ItemCategory.HAT: 0.5,
        }
        
        # Define base positions for each category (relative to canvas)
        self.category_positions = {
            ItemCategory.TOP: (0.5, 0.28),  # Center-top
            ItemCategory.BOTTOM: (0.5, 0.60),  # Center-middle
            ItemCategory.DRESS: (0.5, 0.45),  # Center (for dress-only outfits)
            ItemCategory.OUTERWEAR: (0.5, 0.25),  # Above top
            ItemCategory.SHOES: (0.5, 0.85),  # Bottom center
            ItemCategory.ACCESSORY: (0.25, 0.30),  # Left side
            ItemCategory.BAG: (0.75, 0.50),  # Right side
            ItemCategory.HAT: (0.25, 0.15),  # Top left
        }
    
    async def create_flat_lay(
        self,
        outfit_items: List[ClothingItem],
        outfit_id: str,
        output_format: str = "PNG"
    ) -> Tuple[Optional[Image.Image], Optional[str]]:
        """
        Create a flat lay image from outfit items.
        
        Args:
            outfit_items: List of clothing items in the outfit
            outfit_id: Unique identifier for the outfit
            output_format: Output image format (PNG, JPEG, etc.)
            
        Returns:
            Tuple of (PIL Image, error message if any)
        """
        try:
            logger.info(f"🎨 Creating flat lay for outfit {outfit_id} with {len(outfit_items)} items")
            
            # Step 1: Download and preprocess item images
            processed_items = await self._download_and_preprocess_images(outfit_items)
            
            if not processed_items:
                return None, "No valid item images found"
            
            logger.info(f"✅ Preprocessed {len(processed_items)} item images")
            
            # Step 2: Create canvas
            canvas = self._create_canvas()
            
            # Step 3: Categorize items
            categorized_items = self._categorize_items(processed_items)
            
            # Step 4: Calculate positions and scales
            layout_plan = self._calculate_layout(categorized_items)
            
            # Step 5: Compose items onto canvas
            final_image = self._compose_items(canvas, categorized_items, layout_plan)
            
            logger.info(f"✅ Flat lay created successfully for outfit {outfit_id}")
            
            return final_image, None
            
        except Exception as e:
            logger.error(f"❌ Error creating flat lay: {e}", exc_info=True)
            return None, f"Failed to create flat lay: {str(e)}"
    
    async def _download_and_preprocess_images(
        self,
        items: List[ClothingItem]
    ) -> List[Dict[str, Any]]:
        """Download and preprocess item images"""
        processed_items = []
        
        for item in items:
            try:
                # Get image URL
                image_url = getattr(item, 'imageUrl', None) or getattr(item, 'image_url', None)
                
                if not image_url or 'placeholder' in image_url.lower():
                    logger.warning(f"⚠️ No valid image URL for item {item.id}")
                    continue
                
                # Download image
                image = await self._download_image(image_url)
                
                if image is None:
                    logger.warning(f"⚠️ Failed to download image for item {item.id}")
                    continue
                
                # Remove background if not already transparent
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # Apply background removal (simple approach)
                image = self._remove_background(image)
                
                # Resize to reasonable dimensions
                image = self._resize_image(image, self.config.max_item_width, self.config.max_item_height)
                
                processed_items.append({
                    'item': item,
                    'image': image,
                    'category': self._get_item_category(item)
                })
                
            except Exception as e:
                logger.error(f"❌ Error preprocessing item {item.id}: {e}")
                continue
        
        return processed_items
    
    async def _download_image(self, url: str, timeout: int = 10) -> Optional[Image.Image]:
        """Download image from URL"""
        try:
            # Run blocking IO in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, timeout=timeout)
            )
            
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            else:
                logger.warning(f"Failed to download image: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None
    
    def _remove_background(self, image: Image.Image) -> Image.Image:
        """
        Simple background removal using PIL.
        For production, consider using rembg library or external API.
        """
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get pixel data
        data = image.getdata()
        
        # Simple approach: make white/light pixels transparent
        # This assumes items are photographed on white/light backgrounds
        new_data = []
        for item in data:
            # If pixel is mostly white (R, G, B > 240), make it transparent
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))  # Transparent
            else:
                new_data.append(item)
        
        image.putdata(new_data)
        return image
    
    def _resize_image(
        self,
        image: Image.Image,
        max_width: int,
        max_height: int
    ) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        # Get current dimensions
        width, height = image.size
        
        # Calculate scaling factor
        scale = min(max_width / width, max_height / height, 1.0)
        
        # Only resize if needed
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def _get_item_category(self, item: ClothingItem) -> ItemCategory:
        """Determine the category of an item"""
        item_type = item.type.lower()
        
        # Map item types to categories
        if any(t in item_type for t in ['shirt', 'blouse', 'top', 'tee', 'tank', 'sweater', 'polo']):
            return ItemCategory.TOP
        elif any(t in item_type for t in ['pants', 'jeans', 'shorts', 'trousers', 'skirt', 'leggings']):
            return ItemCategory.BOTTOM
        elif 'dress' in item_type:
            return ItemCategory.DRESS
        elif any(t in item_type for t in ['jacket', 'coat', 'blazer', 'cardigan', 'hoodie']):
            return ItemCategory.OUTERWEAR
        elif any(t in item_type for t in ['shoes', 'sneakers', 'boots', 'sandals', 'heels']):
            return ItemCategory.SHOES
        elif any(t in item_type for t in ['bag', 'purse', 'backpack', 'tote']):
            return ItemCategory.BAG
        elif 'hat' in item_type or 'cap' in item_type:
            return ItemCategory.HAT
        else:
            return ItemCategory.ACCESSORY
    
    def _create_canvas(self) -> Image.Image:
        """Create a blank canvas for the flat lay"""
        canvas = Image.new(
            'RGBA',
            (self.config.canvas_width, self.config.canvas_height),
            self.config.background_color
        )
        return canvas
    
    def _categorize_items(
        self,
        processed_items: List[Dict[str, Any]]
    ) -> Dict[ItemCategory, List[Dict[str, Any]]]:
        """Categorize items by type"""
        categorized = {}
        
        for item_data in processed_items:
            category = item_data['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(item_data)
        
        return categorized
    
    def _calculate_layout(
        self,
        categorized_items: Dict[ItemCategory, List[Dict[str, Any]]]
    ) -> Dict[str, LayoutPosition]:
        """Calculate position and scale for each item"""
        layout_plan = {}
        
        # Check if this is a dress-based outfit
        has_dress = ItemCategory.DRESS in categorized_items
        
        for category, items in categorized_items.items():
            # Get base position for this category
            if category in self.category_positions:
                base_x_ratio, base_y_ratio = self.category_positions[category]
            else:
                base_x_ratio, base_y_ratio = 0.5, 0.5
            
            # Get scale for this category
            scale = self.category_scales.get(category, 0.8)
            
            # If there's a dress, adjust other item positions
            if has_dress and category == ItemCategory.TOP:
                # Skip tops if there's a dress
                continue
            
            # Handle multiple items in same category (e.g., multiple accessories)
            for i, item_data in enumerate(items):
                item_id = item_data['item'].id
                
                # Calculate actual position
                x = int(base_x_ratio * self.config.canvas_width)
                y = int(base_y_ratio * self.config.canvas_height)
                
                # Offset if multiple items in same category
                if len(items) > 1:
                    # Spread items horizontally
                    offset = (i - len(items) / 2) * (self.config.item_spacing * 2)
                    x += int(offset)
                
                layout_plan[item_id] = LayoutPosition(
                    x=x,
                    y=y,
                    scale=scale,
                    rotation=0,
                    layer=self._get_category_layer(category)
                )
        
        return layout_plan
    
    def _get_category_layer(self, category: ItemCategory) -> int:
        """Get the z-index layer for a category"""
        # Lower layers are drawn first (background)
        layer_order = {
            ItemCategory.OUTERWEAR: 1,
            ItemCategory.TOP: 2,
            ItemCategory.DRESS: 2,
            ItemCategory.BOTTOM: 3,
            ItemCategory.SHOES: 4,
            ItemCategory.BAG: 5,
            ItemCategory.ACCESSORY: 6,
            ItemCategory.HAT: 7,
        }
        return layer_order.get(category, 5)
    
    def _compose_items(
        self,
        canvas: Image.Image,
        categorized_items: Dict[ItemCategory, List[Dict[str, Any]]],
        layout_plan: Dict[str, LayoutPosition]
    ) -> Image.Image:
        """Compose all items onto the canvas"""
        # Flatten items and sort by layer
        all_items = []
        for category, items in categorized_items.items():
            all_items.extend(items)
        
        # Sort by layer (z-index)
        all_items.sort(key=lambda x: layout_plan[x['item'].id].layer)
        
        # Draw each item
        for item_data in all_items:
            item_id = item_data['item'].id
            image = item_data['image']
            
            if item_id not in layout_plan:
                continue
            
            position = layout_plan[item_id]
            
            # Scale image
            scaled_image = self._scale_item_image(image, position.scale)
            
            # Add shadow if enabled
            if self.config.shadow_enabled:
                scaled_image = self._add_shadow(scaled_image)
            
            # Calculate paste position (center the image)
            paste_x = position.x - scaled_image.width // 2
            paste_y = position.y - scaled_image.height // 2
            
            # Paste image onto canvas
            canvas.paste(scaled_image, (paste_x, paste_y), scaled_image)
        
        return canvas
    
    def _scale_item_image(self, image: Image.Image, scale: float) -> Image.Image:
        """Scale an item image"""
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _add_shadow(self, image: Image.Image) -> Image.Image:
        """Add a subtle shadow behind the item"""
        # Create a shadow layer
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
        
        # Get the alpha channel
        alpha = image.split()[3]
        
        # Create shadow by darkening the alpha
        shadow_alpha = ImageEnhance.Brightness(alpha).enhance(0.3)
        shadow.putalpha(shadow_alpha)
        
        # Blur the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(self.config.shadow_blur))
        
        # Create a new image with shadow offset
        shadow_width = image.width + abs(self.config.shadow_offset[0]) * 2
        shadow_height = image.height + abs(self.config.shadow_offset[1]) * 2
        
        result = Image.new('RGBA', (shadow_width, shadow_height), (0, 0, 0, 0))
        
        # Paste shadow
        shadow_x = abs(self.config.shadow_offset[0]) + self.config.shadow_offset[0]
        shadow_y = abs(self.config.shadow_offset[1]) + self.config.shadow_offset[1]
        result.paste(shadow, (shadow_x, shadow_y), shadow)
        
        # Paste original image on top
        result.paste(image, (abs(self.config.shadow_offset[0]), abs(self.config.shadow_offset[1])), image)
        
        return result
    
    def save_image(
        self,
        image: Image.Image,
        output_path: str,
        format: str = "PNG",
        quality: int = 95
    ) -> bool:
        """Save the flat lay image to a file"""
        try:
            if format.upper() == "JPEG":
                # Convert to RGB for JPEG (no transparency)
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
                rgb_image.save(output_path, format=format, quality=quality)
            else:
                image.save(output_path, format=format, quality=quality)
            
            logger.info(f"✅ Saved flat lay image to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving image: {e}")
            return False
    
    def image_to_bytes(
        self,
        image: Image.Image,
        format: str = "PNG",
        quality: int = 95
    ) -> Optional[bytes]:
        """Convert PIL Image to bytes"""
        try:
            buffer = io.BytesIO()
            
            if format.upper() == "JPEG":
                # Convert to RGB for JPEG
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
                rgb_image.save(buffer, format=format, quality=quality)
            else:
                image.save(buffer, format=format, quality=quality)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error converting image to bytes: {e}")
            return None

