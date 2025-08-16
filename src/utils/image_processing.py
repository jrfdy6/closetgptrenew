import os
import logging
from PIL import Image
import tempfile

# Set up logging
logger = logging.getLogger(__name__)

def process_image_for_analysis(image_path: str) -> str:
    """Process an image for analysis by resizing and optimizing it."""
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new dimensions while maintaining aspect ratio
            max_size = 1024  # Maximum dimension
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            # Resize image if it's larger than max_size
            if ratio < 1:
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Create a temporary file for the processed image
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Save as JPEG with quality optimization
                img.save(temp_file.name, 'JPEG', quality=85, optimize=True)
                return temp_file.name
                
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise ValueError(f"Failed to process image: {str(e)}") 