"""
Robust outfit generation service wrapper.
"""

import logging
from typing import Dict, List, Any, Optional

from ...routes.outfits.models import OutfitRequest

logger = logging.getLogger(__name__)


class RobustOutfitGenerationService:
    """
    Wrapper for the robust outfit generation service.
    This handles the integration with the existing robust_outfit_generation_service.
    """
    
    def __init__(self):
        self.logger = logger
        self._service = None
        self._context_class = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the robust service and context class."""
        try:
            from ..robust_outfit_generation_service import RobustOutfitGenerationService as OriginalService
            from ..robust_outfit_generation_service import GenerationContext
            
            self._service = OriginalService()
            self._context_class = GenerationContext
            
            logger.info("✅ Robust outfit generation service initialized successfully")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import robust service: {e}")
            self._service = None
            self._context_class = None
    
    async def generate_outfit(self, context) -> Any:
        """
        Generate an outfit using the robust service.
        
        Args:
            context: GenerationContext object with wardrobe, occasion, style, etc.
            
        Returns:
            Generated outfit object
        """
        if not self._service:
            raise Exception("Robust service not available - initialization failed")
        
        try:
            # Call the original robust service
            outfit = await self._service.generate_outfit(context)
            
            if outfit is None:
                raise Exception("Robust service returned None")
            
            logger.info(f"✅ Robust service generated outfit successfully")
            return outfit
            
        except Exception as e:
            logger.error(f"❌ Robust service generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if the robust service is available."""
        return self._service is not None
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the robust service."""
        return {
            "available": self.is_available(),
            "service_type": "robust_outfit_generation",
            "context_class": str(self._context_class) if self._context_class else None
        }
