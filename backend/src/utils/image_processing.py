#!/usr/bin/env python3
"""
Image Processing Utilities
Advanced image processing for flat lay composition
"""

import logging
from typing import Optional, Tuple
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

logger = logging.getLogger(__name__)


def remove_background_advanced(
    image: Image.Image,
    threshold: int = 240,
    edge_blur: int = 2
) -> Image.Image:
    """
    Advanced background removal with edge smoothing.
    
    Args:
        image: Input PIL Image
        threshold: Color threshold for background (0-255)
        edge_blur: Amount of blur to apply to edges
        
    Returns:
        Image with transparent background
    """
    try:
        # Convert to RGBA if needed
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Convert to numpy array for processing
        img_array = np.array(image)
        
        # Separate RGB and alpha channels
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3] if img_array.shape[2] == 4 else np.ones(rgb.shape[:2], dtype=np.uint8) * 255
        
        # Calculate brightness for each pixel
        brightness = np.mean(rgb, axis=2)
        
        # Create mask: pixels brighter than threshold become transparent
        mask = (brightness > threshold).astype(np.uint8) * 255
        
        # Invert mask (we want to keep dark pixels, remove bright ones)
        mask = 255 - mask
        
        # Apply the mask to alpha channel
        new_alpha = np.minimum(alpha, mask)
        
        # Combine RGB with new alpha
        result = np.dstack([rgb, new_alpha])
        
        # Convert back to PIL Image
        result_image = Image.fromarray(result.astype(np.uint8), 'RGBA')
        
        # Smooth edges
        if edge_blur > 0:
            result_image = smooth_edges(result_image, blur_radius=edge_blur)
        
        return result_image
        
    except Exception as e:
        logger.error(f"Error in advanced background removal: {e}")
        return image


def smooth_edges(image: Image.Image, blur_radius: int = 2) -> Image.Image:
    """
    Smooth edges of transparent image for better compositing.
    
    Args:
        image: PIL Image with alpha channel
        blur_radius: Radius for edge smoothing
        
    Returns:
        Image with smoothed edges
    """
    try:
        if image.mode != 'RGBA':
            return image
        
        # Extract alpha channel
        alpha = image.split()[3]
        
        # Apply slight blur to alpha for smooth edges
        alpha_blurred = alpha.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Put blurred alpha back
        image.putalpha(alpha_blurred)
        
        return image
        
    except Exception as e:
        logger.error(f"Error smoothing edges: {e}")
        return image


def enhance_image_quality(
    image: Image.Image,
    sharpen: bool = True,
    contrast: float = 1.1,
    color: float = 1.05
) -> Image.Image:
    """
    Enhance image quality for better flat lay appearance.
    
    Args:
        image: Input PIL Image
        sharpen: Whether to apply sharpening
        contrast: Contrast adjustment (1.0 = no change)
        color: Color saturation adjustment (1.0 = no change)
        
    Returns:
        Enhanced image
    """
    try:
        # Sharpen if requested
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)
        
        # Enhance contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        # Enhance color saturation
        if color != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(color)
        
        return image
        
    except Exception as e:
        logger.error(f"Error enhancing image: {e}")
        return image


def add_drop_shadow(
    image: Image.Image,
    offset: Tuple[int, int] = (10, 10),
    blur: int = 15,
    opacity: int = 128,
    color: Tuple[int, int, int] = (0, 0, 0)
) -> Image.Image:
    """
    Add a drop shadow to an image with transparency.
    
    Args:
        image: Input PIL Image with alpha channel
        offset: Shadow offset (x, y)
        blur: Shadow blur radius
        opacity: Shadow opacity (0-255)
        color: Shadow color (RGB)
        
    Returns:
        Image with drop shadow
    """
    try:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Calculate new size to accommodate shadow
        new_width = image.width + abs(offset[0]) * 2 + blur * 2
        new_height = image.height + abs(offset[1]) * 2 + blur * 2
        
        # Create shadow layer
        shadow = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
        
        # Create a colored shadow from the alpha channel
        shadow_color = Image.new('RGBA', image.size, color + (opacity,))
        shadow_mask = image.split()[3]  # Alpha channel as mask
        
        # Position for shadow
        shadow_x = blur + abs(offset[0]) + offset[0]
        shadow_y = blur + abs(offset[1]) + offset[1]
        
        # Paste colored shadow
        shadow.paste(shadow_color, (shadow_x, shadow_y), shadow_mask)
        
        # Blur the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        
        # Create result canvas
        result = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
        
        # Paste shadow
        result = Image.alpha_composite(result, shadow)
        
        # Paste original image on top
        image_x = blur + abs(offset[0])
        image_y = blur + abs(offset[1])
        result.paste(image, (image_x, image_y), image)
        
        return result
        
    except Exception as e:
        logger.error(f"Error adding drop shadow: {e}")
        return image


def create_realistic_shadow(
    image: Image.Image,
    angle: int = 45,
    distance: int = 15,
    blur: int = 20,
    opacity: float = 0.3
) -> Image.Image:
    """
    Create a realistic directional shadow for flat lay items.
    
    Args:
        image: Input PIL Image with alpha
        angle: Shadow angle in degrees
        distance: Shadow distance from object
        blur: Shadow blur amount
        opacity: Shadow opacity (0.0-1.0)
        
    Returns:
        Image with realistic shadow
    """
    try:
        import math
        
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Calculate shadow offset from angle
        angle_rad = math.radians(angle)
        offset_x = int(distance * math.cos(angle_rad))
        offset_y = int(distance * math.sin(angle_rad))
        
        # Calculate opacity as 0-255
        shadow_opacity = int(opacity * 255)
        
        return add_drop_shadow(
            image,
            offset=(offset_x, offset_y),
            blur=blur,
            opacity=shadow_opacity
        )
        
    except Exception as e:
        logger.error(f"Error creating realistic shadow: {e}")
        return image


def auto_crop_transparent(image: Image.Image, padding: int = 0) -> Image.Image:
    """
    Auto-crop image to remove excess transparent space.
    
    Args:
        image: PIL Image with alpha channel
        padding: Padding to add around cropped area
        
    Returns:
        Cropped image
    """
    try:
        if image.mode != 'RGBA':
            return image
        
        # Get bounding box of non-transparent pixels
        bbox = image.getbbox()
        
        if bbox:
            # Add padding
            bbox = (
                max(0, bbox[0] - padding),
                max(0, bbox[1] - padding),
                min(image.width, bbox[2] + padding),
                min(image.height, bbox[3] + padding)
            )
            return image.crop(bbox)
        
        return image
        
    except Exception as e:
        logger.error(f"Error auto-cropping: {e}")
        return image


def normalize_item_orientation(
    image: Image.Image,
    item_type: str
) -> Image.Image:
    """
    Normalize item orientation for consistent flat lay appearance.
    Some items (like shoes) may need rotation or special handling.
    
    Args:
        image: Input PIL Image
        item_type: Type of clothing item
        
    Returns:
        Normalized image
    """
    try:
        item_type_lower = item_type.lower()
        
        # Special handling for shoes - might need to be rotated
        if any(t in item_type_lower for t in ['shoes', 'sneakers', 'boots']):
            # Check aspect ratio to determine if rotation is needed
            aspect_ratio = image.width / image.height
            
            # If shoes are horizontal, might want to keep them that way
            # This is just an example - adjust based on your needs
            pass
        
        return image
        
    except Exception as e:
        logger.error(f"Error normalizing orientation: {e}")
        return image


def add_subtle_texture(
    canvas: Image.Image,
    texture_strength: float = 0.03
) -> Image.Image:
    """
    Add subtle texture to canvas background for more realistic appearance.
    
    Args:
        canvas: Background canvas
        texture_strength: Strength of texture (0.0-1.0)
        
    Returns:
        Canvas with subtle texture
    """
    try:
        # Create noise texture
        noise = np.random.normal(0, 255 * texture_strength, (canvas.height, canvas.width))
        
        # Convert canvas to array
        canvas_array = np.array(canvas)
        
        # Add noise to RGB channels only (not alpha)
        if canvas.mode == 'RGBA':
            for i in range(3):  # RGB channels only
                canvas_array[:, :, i] = np.clip(
                    canvas_array[:, :, i] + noise,
                    0,
                    255
                )
        else:
            canvas_array = np.clip(canvas_array + noise[:, :, np.newaxis], 0, 255)
        
        return Image.fromarray(canvas_array.astype(np.uint8), canvas.mode)
        
    except Exception as e:
        logger.error(f"Error adding texture: {e}")
        return canvas


def apply_vignette(
    image: Image.Image,
    strength: float = 0.3
) -> Image.Image:
    """
    Apply subtle vignette effect to draw focus to center.
    
    Args:
        image: Input PIL Image
        strength: Vignette strength (0.0-1.0)
        
    Returns:
        Image with vignette
    """
    try:
        # Create radial gradient for vignette
        width, height = image.size
        center_x, center_y = width // 2, height // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        # Create coordinate grids
        y, x = np.ogrid[:height, :width]
        
        # Calculate distance from center
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Create vignette mask (1.0 at center, fades to (1-strength) at edges)
        vignette = 1.0 - (dist_from_center / max_dist) * strength
        vignette = np.clip(vignette, 0, 1)
        
        # Apply vignette to image
        img_array = np.array(image)
        
        if image.mode == 'RGBA':
            # Apply to RGB channels only
            for i in range(3):
                img_array[:, :, i] = (img_array[:, :, i] * vignette).astype(np.uint8)
        else:
            img_array = (img_array * vignette[:, :, np.newaxis]).astype(np.uint8)
        
        return Image.fromarray(img_array, image.mode)
        
    except Exception as e:
        logger.error(f"Error applying vignette: {e}")
        return image
