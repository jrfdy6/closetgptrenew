import logging
from .ai_runtime.vision_runtime import analyze_image_path_with_openai_vision

# Set up logging
logger = logging.getLogger(__name__)

async def analyze_image_with_gpt4(image_path: str) -> dict:
    """Analyze an image using the centralized vision runtime."""
    logger.info("Delegating image analysis to ai_runtime.vision_runtime")
    return await analyze_image_path_with_openai_vision(image_path)
