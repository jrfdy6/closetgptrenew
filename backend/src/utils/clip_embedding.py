import torch
import clip
from PIL import Image
import numpy as np
from typing import List, Optional
import logging
import traceback

logger = logging.getLogger(__name__)

class CLIPEmbedder:
    def __init__(self):
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
            
            # Load CLIP model
            logger.info("Loading CLIP model...")
            self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
            logger.info("CLIP model loaded successfully")
            
            # Log model details
            logger.info(f"Model architecture: {self.model.__class__.__name__}")
            logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CLIP model: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def get_embedding(self, image: Image.Image) -> Optional[List[float]]:
        """
        Generate a CLIP embedding for an image
        Args:
            image: PIL Image object
        Returns:
            List of floats representing the normalized embedding vector
        """
        try:
            logger.info(f"Processing image of size: {image.size}")
            
            # Preprocess the image
            logger.info("Preprocessing image...")
            try:
                image_input = self.preprocess(image).unsqueeze(0).to(self.device)
                logger.info(f"Preprocessed image shape: {image_input.shape}")
            except Exception as e:
                logger.error(f"Image preprocessing failed: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None
            
            # Get image features
            logger.info("Generating image features...")
            try:
                with torch.no_grad():
                    image_features = self.model.encode_image(image_input)
                logger.info(f"Raw features shape: {image_features.shape}")
            except Exception as e:
                logger.error(f"Feature generation failed: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None
            
            # Normalize the features
            logger.info("Normalizing features...")
            try:
                image_features = image_features / image_features.norm(dim=1, keepdim=True)
                logger.info("Features normalized successfully")
            except Exception as e:
                logger.error(f"Feature normalization failed: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None
            
            # Convert to numpy and then to list
            logger.info("Converting features to list...")
            try:
                embedding = image_features.cpu().numpy()[0].tolist()
                logger.info(f"Generated embedding of length: {len(embedding)}")
                return embedding
            except Exception as e:
                logger.error(f"Feature conversion failed: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None
            
        except Exception as e:
            logger.error(f"Unexpected error in get_embedding: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

# Create a singleton instance
try:
    logger.info("Initializing CLIP embedder...")
    embedder = CLIPEmbedder()
    logger.info("CLIP embedder initialized successfully")
except Exception as e:
    logger.error(f"Failed to create CLIP embedder instance: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise 