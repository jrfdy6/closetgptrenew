from typing import List, Dict, Any, Optional
# Firebase imports moved inside methods to prevent import-time crashes
# from firebase_admin import firestore
from ..custom_types.wardrobe import ClothingItem, Metadata
from ..utils.style_analysis import analyze_item_style
import time
import logging

logger = logging.getLogger(__name__)

class MetadataEnhancementService:
    def __init__(self):
        # Firebase will be initialized when methods are called
        self.db = None
        self.wardrobe_collection = None
    
    def _ensure_firebase_connection(self):
        """Ensure Firebase connection is established"""
        if self.db is None:
            try:
                from firebase_admin import firestore
                self.db = firestore.client()
                self.wardrobe_collection = self.db.collection('wardrobe')
            except Exception as e:
                logger.warning(f"Failed to initialize Firebase in MetadataEnhancementService: {e}")
                raise
    
    async def ensure_metadata_consistency(self, user_id: str = None) -> Dict[str, Any]:
        """
        Ensure all wardrobe items have consistent and complete metadata.
        """
        try:
            # Ensure Firebase connection is established
            self._ensure_firebase_connection()
            
            # Get all wardrobe items
            query = self.wardrobe_collection
            if user_id:
                query = query.where('userId', '==', user_id)
            
            docs = query.stream()
            
            total_items = 0
            enhanced_items = 0
            skipped_items = 0
            failed_items = 0
            
            for doc in docs:
                total_items += 1
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                
                try:
                    # Check if item needs enhancement
                    if self._needs_enhancement(item_data):
                        enhanced_item = await self._enhance_item_metadata(item_data)
                        if enhanced_item:
                            # Update the item in Firestore
                            self.wardrobe_collection.document(doc.id).update(enhanced_item)
                            enhanced_items += 1
                            logger.info(f"Enhanced metadata for item: {(item_data.get('name', 'Unknown') if item_data else 'Unknown')}")
                        else:
                            failed_items += 1
                    else:
                        skipped_items += 1
                        
                except Exception as e:
                    logger.error(f"Error enhancing item {doc.id}: {e}")
                    failed_items += 1
            
            return {
                "success": True,
                "total_items": total_items,
                "enhanced_items": enhanced_items,
                "skipped_items": skipped_items,
                "failed_items": failed_items,
                "enhancement_rate": (enhanced_items / total_items * 100) if total_items > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error in metadata consistency check: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _needs_enhancement(self, item_data: Dict[str, Any]) -> bool:
        """
        Check if an item needs metadata enhancement.
        """
        # Check if item has basic required fields
        required_fields = ['name', 'type', 'color', 'style', 'occasion', 'season']
        for field in required_fields:
            if not (item_data.get(field) if item_data else None):
                return True
        
        # Check if item has enhanced metadata
        metadata = (item_data.get('metadata', {}) if item_data else {})
        if not metadata:
            return True
        
        # Check for enhanced analysis timestamp
        if not (metadata.get('analysisTimestamp') if metadata else None):
            return True
        
        # Check if style and occasion arrays are too short
        if len((item_data.get('style', []) if item_data else [])) < 2:
            return True
        
        if len((item_data.get('occasion', []) if item_data else [])) < 2:
            return True
        
        # Check if dominant colors are missing
        if not (item_data.get('dominantColors') if item_data else None):
            return True
        
        return False
    
    async def _enhance_item_metadata(self, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhance metadata for a single item.
        """
        try:
            enhanced_data = {}
            
            # Enhance basic fields if missing
            if not (item_data.get('style') if item_data else None):
                enhanced_data['style'] = self._infer_style_from_type((item_data.get('type', '') if item_data else ''))
            
            if not (item_data.get('occasion') if item_data else None):
                enhanced_data['occasion'] = self._infer_occasion_from_type((item_data.get('type', '') if item_data else ''))
            
            if not (item_data.get('season') if item_data else None):
                enhanced_data['season'] = ['all']  # Default to all seasons
            
            if not (item_data.get('dominantColors') if item_data else None):
                enhanced_data['dominantColors'] = [{
                    "name": (item_data.get('color', 'unknown') if item_data else 'unknown'),
                    "hex": self._get_color_hex((item_data.get('color', 'unknown') if item_data else 'unknown')),
                    "rgb": [0, 0, 0]  # Default RGB
                }]
            
            if not (item_data.get('matchingColors') if item_data else None):
                enhanced_data['matchingColors'] = self._get_matching_colors((item_data.get('color', 'unknown') if item_data else 'unknown'))
            
            # Create or enhance metadata object
            metadata = (item_data.get('metadata', {}) if item_data else {})
            enhanced_metadata = {
                "analysisTimestamp": int(time.time()),
                "originalType": (item_data.get('type', 'unknown') if item_data else 'unknown'),
                "styleTags": (item_data.get('style', []) if item_data else []),
                "occasionTags": (item_data.get('occasion', []) if item_data else []),
                "colorAnalysis": {
                    "dominant": [(color.get('name', 'unknown') if color else 'unknown') for color in (enhanced_data.get('dominantColors', []) if enhanced_data else [])],
                    "matching": [(color.get('name', 'unknown') if color else 'unknown') for color in (enhanced_data.get('matchingColors', []) if enhanced_data else [])]
                },
                "visualAttributes": {
                    "pattern": "solid",  # Default
                    "formalLevel": self._infer_formality(((item_data.get('type', '') if item_data else '') if item_data else ''), item_data.get('style', [])),
                    "fit": "regular",  # Default
                    "material": self._infer_material((item_data.get('type', '') if item_data else '')),
                    "fabricWeight": "medium"  # Default
                },
                "itemMetadata": {
                    "tags": (item_data.get('tags', []) if item_data else []),
                    "careInstructions": "Check care label"
                }
            }
            
            # Merge with existing metadata
            metadata.update(enhanced_metadata)
            enhanced_data['metadata'] = metadata
            
            # Update timestamps
            enhanced_data['updatedAt'] = int(time.time())
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing item metadata: {e}")
            return None
    
    def _infer_style_from_type(self, item_type: str) -> List[str]:
        """Infer style from item type."""
        style_mappings = {
            'shirt': ['casual', 'classic'],
            't-shirt': ['casual', 'minimalist'],
            'dress_shirt': ['business', 'formal', 'classic'],
            'pants': ['casual', 'classic'],
            'jeans': ['casual', 'streetwear'],
            'dress': ['elegant', 'feminine'],
            'jacket': ['casual', 'classic'],
            'sweater': ['casual', 'comfortable'],
            'shoes': ['classic', 'versatile'],
            'sneakers': ['casual', 'athletic'],
            'boots': ['casual', 'rugged']
        }
        
        return (style_mappings.get(item_type.lower() if style_mappings else None), ['casual'])
    
    def _infer_occasion_from_type(self, item_type: str) -> List[str]:
        """Infer occasion from item type."""
        occasion_mappings = {
            'shirt': ['casual', 'daily'],
            't-shirt': ['casual', 'daily'],
            'dress_shirt': ['business', 'formal'],
            'pants': ['casual', 'daily'],
            'jeans': ['casual', 'daily'],
            'dress': ['special_occasion', 'formal'],
            'jacket': ['casual', 'daily'],
            'sweater': ['casual', 'daily'],
            'shoes': ['casual', 'daily'],
            'sneakers': ['casual', 'athletic'],
            'boots': ['casual', 'outdoor']
        }
        
        return (occasion_mappings.get(item_type.lower() if occasion_mappings else None), ['casual'])
    
    def _get_color_hex(self, color_name: str) -> str:
        """Get hex color for a color name."""
        color_mappings = {
            'black': '#000000',
            'white': '#FFFFFF',
            'blue': '#0000FF',
            'red': '#FF0000',
            'green': '#00FF00',
            'yellow': '#FFFF00',
            'purple': '#800080',
            'orange': '#FFA500',
            'pink': '#FFC0CB',
            'brown': '#A52A2A',
            'gray': '#808080',
            'grey': '#808080',
            'navy': '#000080',
            'beige': '#F5F5DC',
            'cream': '#FFFDD0'
        }
        
        return (color_mappings.get(color_name.lower() if color_mappings else None), '#000000')
    
    def _get_matching_colors(self, color_name: str) -> List[Dict[str, Any]]:
        """Get matching colors for a given color."""
        color_matches = {
            'black': ['white', 'gray', 'red', 'blue'],
            'white': ['black', 'navy', 'red', 'blue'],
            'blue': ['white', 'gray', 'navy', 'beige'],
            'red': ['black', 'white', 'navy', 'gray'],
            'green': ['brown', 'beige', 'white', 'navy'],
            'brown': ['beige', 'cream', 'white', 'navy'],
            'gray': ['black', 'white', 'navy', 'red'],
            'navy': ['white', 'beige', 'gray', 'red']
        }
        
        matches = (color_matches.get(color_name.lower() if color_matches else None), ['black', 'white'])
        return [{"name": color, "hex": self._get_color_hex(color), "rgb": [0, 0, 0]} for color in matches]
    
    def _infer_formality(self, item_type: str, styles: List[str]) -> str:
        """Infer formality level from item type and styles."""
        formal_types = ['dress_shirt', 'dress', 'suit']
        casual_types = ['t-shirt', 'jeans', 'sneakers']
        
        if item_type in formal_types:
            return 'formal'
        elif item_type in casual_types:
            return 'casual'
        elif 'business' in styles or 'formal' in styles:
            return 'business'
        else:
            return 'casual'
    
    def _infer_material(self, item_type: str) -> str:
        """Infer material from item type."""
        material_mappings = {
            'shirt': 'cotton',
            't-shirt': 'cotton',
            'dress_shirt': 'cotton',
            'pants': 'cotton',
            'jeans': 'denim',
            'dress': 'silk',
            'jacket': 'cotton',
            'sweater': 'wool',
            'shoes': 'leather',
            'sneakers': 'canvas',
            'boots': 'leather'
        }
        
        return (material_mappings.get(item_type.lower() if material_mappings else None), 'cotton') 