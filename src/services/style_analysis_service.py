import torch
import numpy as np
from typing import List, Dict, Tuple, Optional
from PIL import Image
import logging
from ..utils.clip_embedding import embedder
import open_clip as clip

logger = logging.getLogger(__name__)

class StyleAnalysisService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, _, self.preprocess = clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        self.model = self.model.to(self.device)
        
        # Define comprehensive style prompts for CLIP
        self.style_prompts = {
            "Dark Academia": [
                "dark academia fashion, sophisticated intellectual style, tweed blazer, oxford shoes, vintage academic aesthetic",
                "dark academia clothing, muted colors, structured pieces, vintage-inspired, scholarly fashion",
                "dark academia outfit, brown and navy colors, elbow patches, pleated skirts, intellectual style"
            ],
            "Old Money": [
                "old money fashion, classic luxury style, polo shirts, pleated trousers, sophisticated elegance",
                "old money aesthetic, timeless pieces, cashmere sweaters, loafers, refined style",
                "old money clothing, understated luxury, quality materials, traditional cuts, elegant simplicity"
            ],
            "Streetwear": [
                "streetwear fashion, urban style, graphic tees, hoodies, sneakers, street culture",
                "streetwear clothing, baggy jeans, puffer jackets, cargo pants, urban aesthetic",
                "streetwear style, skate culture, street fashion, trendy urban wear, street culture clothing"
            ],
            "Y2K": [
                "Y2K fashion, 2000s style, baby tees, low-rise jeans, butterfly clips, retro 2000s",
                "Y2K aesthetic, early 2000s fashion, crop tops, platform shoes, nostalgic 2000s style",
                "Y2K clothing, 2000s retro fashion, butterfly motifs, pastel colors, early 2000s aesthetic"
            ],
            "Minimalist": [
                "minimalist fashion, clean simple style, neutral colors, timeless pieces, understated elegance",
                "minimalist clothing, clean lines, simple cuts, monochrome style, essential pieces",
                "minimalist aesthetic, simple fashion, clean design, basic pieces, understated style"
            ],
            "Boho": [
                "bohemian fashion, free-spirited style, flowing fabrics, ethnic prints, hippie aesthetic",
                "boho clothing, layered pieces, fringe details, earth tones, bohemian spirit",
                "bohemian style, hippie fashion, flowing dresses, ethnic influences, free-spirited clothing"
            ],
            "Preppy": [
                "preppy fashion, classic collegiate style, polo shirts, chinos, traditional elegance",
                "preppy clothing, ivy league style, button-down shirts, khakis, classic American fashion",
                "preppy aesthetic, traditional style, collegiate fashion, classic cuts, refined casual wear"
            ],
            "Grunge": [
                "grunge fashion, 90s alternative style, flannel shirts, ripped jeans, rock aesthetic",
                "grunge clothing, alternative fashion, distressed pieces, dark colors, rock culture style",
                "grunge style, 90s fashion, alternative aesthetic, distressed clothing, rock and roll fashion"
            ],
            "Classic": [
                "classic fashion, timeless style, traditional pieces, elegant simplicity, enduring fashion",
                "classic clothing, traditional cuts, timeless elegance, sophisticated style, enduring pieces",
                "classic aesthetic, traditional fashion, timeless design, elegant simplicity, classic elegance"
            ],
            "Techwear": [
                "techwear fashion, futuristic style, technical fabrics, urban utility, cyberpunk aesthetic",
                "techwear clothing, technical gear, urban survival, futuristic fashion, cyber aesthetic",
                "techwear style, technical fashion, urban utility wear, futuristic clothing, cyberpunk style"
            ],
            "Androgynous": [
                "androgynous fashion, gender-neutral style, unisex clothing, fluid fashion, neutral aesthetic",
                "androgynous clothing, gender-fluid style, unisex fashion, neutral cuts, fluid gender expression",
                "androgynous aesthetic, gender-neutral fashion, unisex style, fluid clothing, neutral gender expression"
            ],
            "Coastal Chic": [
                "coastal chic fashion, beach elegance, nautical style, sophisticated beachwear, coastal luxury",
                "coastal chic clothing, beach sophistication, nautical elegance, coastal luxury, beach elegance",
                "coastal chic aesthetic, beach luxury, nautical sophistication, coastal elegance, sophisticated beach style"
            ],
            "Business Casual": [
                "business casual fashion, professional style, smart casual, office wear, professional elegance",
                "business casual clothing, professional wear, smart casual style, office fashion, professional dress",
                "business casual aesthetic, professional style, smart casual wear, office elegance, professional clothing"
            ],
            "Avant-Garde": [
                "avant-garde fashion, experimental style, artistic fashion, innovative design, cutting-edge style",
                "avant-garde clothing, experimental fashion, artistic design, innovative style, cutting-edge fashion",
                "avant-garde aesthetic, experimental design, artistic style, innovative fashion, cutting-edge clothing"
            ],
            "Cottagecore": [
                "cottagecore fashion, romantic rural style, vintage pastoral, whimsical countryside, romantic rural aesthetic",
                "cottagecore clothing, romantic rural fashion, vintage pastoral style, whimsical countryside wear",
                "cottagecore aesthetic, romantic rural clothing, vintage pastoral fashion, whimsical countryside style"
            ],
            "Edgy": [
                "edgy fashion, bold rebellious style, dark aesthetic, alternative fashion, bold statement pieces",
                "edgy clothing, rebellious fashion, dark style, alternative aesthetic, bold fashion statements",
                "edgy aesthetic, bold rebellious clothing, dark fashion, alternative style, bold statement fashion"
            ],
            "Athleisure": [
                "athleisure fashion, athletic leisure style, sporty casual, comfortable athletic wear, active lifestyle fashion",
                "athleisure clothing, athletic leisure wear, sporty casual style, comfortable athletic fashion",
                "athleisure aesthetic, athletic leisure style, sporty casual fashion, comfortable athletic clothing"
            ],
            "Casual Cool": [
                "casual cool fashion, relaxed stylish, effortless cool, laid-back elegance, casual sophistication",
                "casual cool clothing, relaxed stylish wear, effortless cool style, laid-back elegant fashion",
                "casual cool aesthetic, relaxed stylish clothing, effortless cool fashion, laid-back elegant style"
            ],
            "Romantic": [
                "romantic fashion, soft feminine style, delicate details, soft colors, romantic elegance",
                "romantic clothing, soft feminine fashion, delicate style, soft aesthetic, romantic wear",
                "romantic aesthetic, soft feminine clothing, delicate fashion, soft style, romantic elegance"
            ],
            "Artsy": [
                "artsy fashion, creative artistic style, expressive clothing, creative design, artistic expression",
                "artsy clothing, creative artistic fashion, expressive style, creative aesthetic, artistic wear",
                "artsy aesthetic, creative artistic clothing, expressive fashion, creative style, artistic expression"
            ]
        }
        
        # Cache for style embeddings
        self.style_embeddings = {}
        self._initialize_style_embeddings()
    
    def _initialize_style_embeddings(self):
        """Initialize CLIP embeddings for all style prompts"""
        logger.info("Initializing style embeddings...")
        
        for style_name, prompts in self.style_prompts.items():
            try:
                # Tokenize all prompts for this style
                text_tokens = clip.tokenize(prompts).to(self.device)
                
                # Generate embeddings
                with torch.no_grad():
                    text_features = self.model.encode_text(text_tokens)
                    # Normalize features
                    text_features = text_features / text_features.norm(dim=1, keepdim=True)
                    # Average the embeddings for this style
                    style_embedding = text_features.mean(dim=0)
                    style_embedding = style_embedding / style_embedding.norm()
                
                self.style_embeddings[style_name] = style_embedding.cpu()
                logger.info(f"Generated embedding for {style_name}")
                
            except Exception as e:
                logger.error(f"Failed to generate embedding for {style_name}: {str(e)}")
                continue
        
        logger.info(f"Initialized {len(self.style_embeddings)} style embeddings")
    
    def analyze_style(self, image: Image.Image) -> List[Tuple[str, float]]:
        """
        Analyze a clothing item image and return ranked style matches
        
        Args:
            image: PIL Image of the clothing item
            
        Returns:
            List of tuples (style_name, similarity_score) ranked by similarity
        """
        try:
            # Generate image embedding
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features = image_features / image_features.norm(dim=1, keepdim=True)
            
            # Calculate cosine similarity with all styles
            similarities = []
            for style_name, style_embedding in self.style_embeddings.items():
                similarity = torch.cosine_similarity(
                    image_features, 
                    style_embedding.unsqueeze(0).to(self.device)
                ).item()
                similarities.append((style_name, similarity))
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Style analysis completed. Top match: {similarities[0]}")
            return similarities
            
        except Exception as e:
            logger.error(f"Error in style analysis: {str(e)}")
            return []
    
    def get_top_styles(self, image: Image.Image, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Get top-k style matches for an image
        
        Args:
            image: PIL Image of the clothing item
            top_k: Number of top styles to return
            
        Returns:
            List of top-k style matches with similarity scores
        """
        all_matches = self.analyze_style(image)
        return all_matches[:top_k]
    
    def get_style_confidence(self, image: Image.Image, style_name: str) -> float:
        """
        Get confidence score for a specific style
        
        Args:
            image: PIL Image of the clothing item
            style_name: Name of the style to check
            
        Returns:
            Confidence score (0-1) for the specified style
        """
        try:
            # Generate image embedding
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features = image_features / image_features.norm(dim=1, keepdim=True)
            
            # Get style embedding
            if style_name not in self.style_embeddings:
                logger.warning(f"Style '{style_name}' not found in embeddings")
                return 0.0
            
            style_embedding = self.style_embeddings[style_name].to(self.device)
            
            # Calculate cosine similarity
            similarity = torch.cosine_similarity(
                image_features, 
                style_embedding.unsqueeze(0)
            ).item()
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating style confidence: {str(e)}")
            return 0.0
    
    def get_style_breakdown(self, image: Image.Image) -> Dict[str, float]:
        """
        Get confidence scores for all styles
        
        Args:
            image: PIL Image of the clothing item
            
        Returns:
            Dictionary mapping style names to confidence scores
        """
        try:
            # Generate image embedding
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features = image_features / image_features.norm(dim=1, keepdim=True)
            
            # Calculate similarities for all styles
            breakdown = {}
            for style_name, style_embedding in self.style_embeddings.items():
                similarity = torch.cosine_similarity(
                    image_features, 
                    style_embedding.unsqueeze(0).to(self.device)
                ).item()
                breakdown[style_name] = similarity
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error generating style breakdown: {str(e)}")
            return {}

# Create singleton instance
style_analyzer = StyleAnalysisService() 