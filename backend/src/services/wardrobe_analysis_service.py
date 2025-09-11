from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from firebase_admin import firestore
from ..custom_types.wardrobe import ClothingItem, Color
from ..custom_types.outfit import OutfitGeneratedOutfit
from ..custom_types.profile import UserProfile
import logging

logger = logging.getLogger(__name__)

# Try to import inflect, but provide fallback if not available
try:
    import inflect
    p = inflect.engine()
    INFLECT_AVAILABLE = True
except ImportError:
    INFLECT_AVAILABLE = False
    # Simple fallback pluralization rules
    def simple_plural(word):
        """Simple pluralization rules as fallback."""
        if word.endswith('y'):
            return word[:-1] + 'ies'
        elif word.endswith('s') or word.endswith('sh') or word.endswith('ch') or word.endswith('x') or word.endswith('z'):
            return word + 'es'
        else:
            return word + 's'
    
    def simple_singular(word):
        """Simple singularization rules as fallback."""
        if word.endswith('ies'):
            return word[:-3] + 'y'
        elif word.endswith('es'):
            return word[:-2]
        elif word.endswith('s'):
            return word[:-1]
        else:
            return word

class WardrobeAnalysisService:
    def __init__(self):
        self.db = firestore.client()
    
    async def get_wardrobe_gaps(self, user_id: str) -> Dict[str, Any]:
        """Analyze wardrobe gaps based on outfit generation history and current wardrobe."""
        
        print(f"DEBUG: Starting wardrobe gap analysis for user: {user_id}")
        
        # Get user's wardrobe
        wardrobe = await self._get_user_wardrobe(user_id)
        print(f"DEBUG: Retrieved {len(wardrobe)} wardrobe items")
        
        # Get outfit generation history
        outfit_history = await self._get_outfit_history(user_id)
        print(f"DEBUG: Retrieved {len(outfit_history)} outfit history items")
        
        # Get validation errors
        validation_errors = await self._get_validation_errors(user_id)
        print(f"DEBUG: Retrieved {len(validation_errors)} validation errors")
        
        # Get trending styles
        trending_styles = await self._get_trending_styles()
        print(f"DEBUG: Retrieved {len(trending_styles)} trending styles")
        
        # Analyze gaps
        gaps = self._analyze_gaps(wardrobe, outfit_history, validation_errors, trending_styles)
        print(f"DEBUG: Found {len(gaps)} gaps")
        
        # Calculate coverage metrics
        coverage = self._calculate_coverage(wardrobe, gaps)
        print(f"DEBUG: Calculated coverage: {coverage}")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(wardrobe, gaps, validation_errors, trending_styles)
        print(f"DEBUG: Generated {len(recommendations)} recommendations")
        
        # Get wardrobe stats
        wardrobe_stats = self._get_wardrobe_stats(wardrobe)
        print(f"DEBUG: Wardrobe stats: {wardrobe_stats}")
        
        # Get shopping recommendations if there are gaps
        shopping_recommendations = None
        if gaps and len(gaps) > 0:
            try:
                from .shopping_recommendations_service import ShoppingRecommendationsService
                shopping_service = ShoppingRecommendationsService()
                
                # Get user profile for personalized recommendations
                user_profile = await self._get_user_profile(user_id)
                
                shopping_recommendations = await shopping_service.get_shopping_recommendations(
                    user_id=user_id,
                    gaps=gaps,
                    user_profile=user_profile,
                    budget_range=None,  # Will be determined by user preferences
                    preferred_stores=None
                )
                print(f"DEBUG: Generated shopping recommendations: {shopping_recommendations.get('success', False)}")
            except Exception as e:
                print(f"DEBUG: Error generating shopping recommendations: {e}")
                shopping_recommendations = None

        result = {
            "gaps": gaps,
            "coverage": coverage,
            "recommendations": recommendations,
            "trending_styles": trending_styles,
            "wardrobe_stats": wardrobe_stats,
            "shopping_recommendations": shopping_recommendations,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        print(f"DEBUG: Returning result with {len(wardrobe)} wardrobe items")
        return result
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile for personalized recommendations."""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return {
                    'id': user_id,
                    'gender': user_data.get('gender', 'unisex'),
                    'bodyType': user_data.get('bodyType', 'average'),
                    'stylePreferences': user_data.get('stylePreferences', []),
                    'colorPreferences': user_data.get('colorPreferences', []),
                    'age': user_data.get('age', 25),
                    'name': user_data.get('name', 'User')
                }
            else:
                return {
                    'id': user_id,
                    'gender': 'unisex',
                    'bodyType': 'average',
                    'stylePreferences': [],
                    'colorPreferences': [],
                    'age': 25,
                    'name': 'User'
                }
        except Exception as e:
            print(f"DEBUG: Error getting user profile: {e}")
            return {
                'id': user_id,
                'gender': 'unisex',
                'bodyType': 'average',
                'stylePreferences': [],
                'colorPreferences': [],
                'age': 25,
                'name': 'User'
            }
    
    async def _get_user_wardrobe(self, user_id: str) -> List[ClothingItem]:
        """Get user's complete wardrobe from Firestore."""
        try:
            print(f"DEBUG: Getting wardrobe for user ID: {user_id}")
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            docs = wardrobe_ref.stream()
            
            wardrobe = []
            doc_count = 0
            raw_data_list = []  # Store raw data for debugging
            
            for doc in docs:
                doc_count += 1
                item_data = doc.to_dict()
                raw_data_list.append(item_data)  # Store raw data
                
                print(f"DEBUG: Processing doc {doc_count}: {doc.id}")
                print(f"DEBUG: Item data keys: {list(item_data.keys())}")
                print(f"DEBUG: Item type: {item_data.get('type', 'N/A')}")
                print(f"DEBUG: Item brand: {item_data.get('brand', 'N/A')}")
                print(f"DEBUG: Item userId: {item_data.get('userId', 'N/A')}")
                
                # Preprocess the data to fix validation issues
                processed_data = self._preprocess_item_data(item_data)
                # Convert Firestore timestamps to int if needed
                for ts_field in ["createdAt", "updatedAt"]:
                    if ts_field in processed_data:
                        val = processed_data[ts_field]
                        if hasattr(val, 'timestamp'):
                            processed_data[ts_field] = int(val.timestamp())
                        elif isinstance(val, float):
                            processed_data[ts_field] = int(val)
                try:
                    clothing_item = ClothingItem(**processed_data)
                    wardrobe.append(clothing_item)
                    print(f"DEBUG: ✓ Successfully parsed item {doc.id}")
                except Exception as e:
                    print(f"DEBUG: ✗ Error parsing wardrobe item {doc.id}: {e}")
                    print(f"DEBUG:   Raw data: {item_data}")
                    print(f"DEBUG:   Processed data keys: {list(processed_data.keys())}")
                    # Try to create a minimal valid item with fallback values
                    try:
                        def create_color_objects(color_list):
                            if not color_list:
                                return [Color(name="Unknown", hex="#000000", rgb=[0, 0, 0])]
                            colors = []
                            for color_data in color_list:
                                if isinstance(color_data, dict):
                                    colors.append(Color(
                                        name=color_data.get('name', 'Unknown'),
                                        hex=color_data.get('hex', '#000000'),
                                        rgb=color_data.get('rgb', [0, 0, 0])
                                    ))
                                elif isinstance(color_data, str):
                                    colors.append(Color.from_string(color_data))
                                else:
                                    colors.append(Color(name="Unknown", hex="#000000", rgb=[0, 0, 0]))
                            return colors
                        # Convert Firestore timestamps to int for fallback
                        fallback_created = item_data.get('createdAt', 0)
                        fallback_updated = item_data.get('updatedAt', 0)
                        if hasattr(fallback_created, 'timestamp'):
                            fallback_created = int(fallback_created.timestamp())
                        elif isinstance(fallback_created, float):
                            fallback_created = int(fallback_created)
                        if hasattr(fallback_updated, 'timestamp'):
                            fallback_updated = int(fallback_updated.timestamp())
                        elif isinstance(fallback_updated, float):
                            fallback_updated = int(fallback_updated)
                        # Minimal valid metadata
                        fallback_metadata = {
                            'analysisTimestamp': fallback_created or 0,
                            'originalType': item_data.get('type', 'other'),
                            'colorAnalysis': {
                                'dominant': [{'name': 'Unknown', 'hex': '#000000', 'rgb': [0, 0, 0]}],
                                'matching': [{'name': 'Unknown', 'hex': '#000000', 'rgb': [0, 0, 0]}]
                            }
                        }
                        fallback_data = {
                            'id': item_data.get('id', doc.id),
                            'type': item_data.get('type', 'other'),
                            'color': item_data.get('color', 'Unknown'),
                            'style': item_data.get('style', ['Casual']),
                            'season': item_data.get('season', ['all']),
                            'occasion': item_data.get('occasion', ['Casual']),
                            'gender': item_data.get('gender', 'unisex'),
                            'userId': item_data.get('userId', user_id),
                            'imageUrl': item_data.get('imageUrl', ''),
                            'name': item_data.get('name', 'Unknown item'),
                            'createdAt': fallback_created,
                            'updatedAt': fallback_updated,
                            'tags': item_data.get('tags', []),
                            'mood': item_data.get('mood', ['Neutral']),
                            'brand': item_data.get('brand', None),
                            'bodyTypeCompatibility': item_data.get('bodyTypeCompatibility', []),
                            'backgroundRemoved': item_data.get('backgroundRemoved', False),
                            'colorName': item_data.get('colorName', None),
                            'dominantColors': create_color_objects(item_data.get('dominantColors', [])),
                            'matchingColors': create_color_objects(item_data.get('matchingColors', [])),
                            'subType': item_data.get('subType', None),
                            'weatherCompatibility': item_data.get('weatherCompatibility', []),
                            'metadata': fallback_metadata
                        }
                        if not fallback_data['id']:
                            fallback_data['id'] = doc.id
                        if not fallback_data['type']:
                            fallback_data['type'] = 'other'
                        if not fallback_data['userId']:
                            fallback_data['userId'] = user_id
                        clothing_item = ClothingItem(**fallback_data)
                        wardrobe.append(clothing_item)
                        print(f"DEBUG: ✓ Created fallback item for {doc.id}")
                    except Exception as fallback_error:
                        print(f"DEBUG: ✗ Failed to create fallback item for {doc.id}: {fallback_error}")
                        print(f"DEBUG:   Fallback data: {fallback_data}")
                        continue
            
            print(f"DEBUG: Found {len(wardrobe)} wardrobe items for user {user_id}")
            print(f"DEBUG: Total documents processed: {doc_count}")
            print(f"DEBUG: Raw data count: {len(raw_data_list)}")
            
            # Print summary of raw data
            print(f"DEBUG: Raw data summary:")
            for i, raw_data in enumerate(raw_data_list[:5]):  # Show first 5 items
                print(f"DEBUG:   Item {i+1}: type={raw_data.get('type', 'N/A')}, userId={raw_data.get('userId', 'N/A')}")
            
            # Also check if there are any items without userId field
            all_wardrobe_ref = self.db.collection('wardrobe')
            all_docs = all_wardrobe_ref.stream()
            total_items = 0
            for doc in all_docs:
                total_items += 1
                item_data = doc.to_dict()
                if 'userId' not in item_data:
                    print(f"DEBUG: Found item without userId: {doc.id}")
            
            print(f"DEBUG: Total items in wardrobe collection: {total_items}")
            
            # Let's also check what user IDs exist in the wardrobe
            user_ids = set()
            all_wardrobe_ref = self.db.collection('wardrobe')
            all_docs = all_wardrobe_ref.stream()
            for doc in all_docs:
                item_data = doc.to_dict()
                if 'userId' in item_data:
                    user_ids.add(item_data['userId'])
            
            print(f"DEBUG: User IDs found in wardrobe: {user_ids}")
            
            return wardrobe
        except Exception as e:
            print(f"DEBUG: Error getting wardrobe: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _get_outfit_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get outfit generation history for the user."""
        try:
            # Get outfits from the last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            
            outfits_ref = self.db.collection('outfits').where('userId', '==', user_id)
            docs = outfits_ref.stream()
            
            history = []
            for doc in docs:
                outfit_data = doc.to_dict()
                
                # Convert timestamp with error handling
                if 'createdAt' in outfit_data and hasattr(outfit_data['createdAt'], 'timestamp'):
                    try:
                        timestamp_val = outfit_data['createdAt'].timestamp()
                        # Handle both seconds and milliseconds timestamps
                        if timestamp_val > 1e12:  # Likely milliseconds
                            timestamp_seconds = timestamp_val / 1000.0
                        else:
                            timestamp_seconds = timestamp_val
                        # Sanity check: Unix timestamps should be roughly between 2000-2100
                        if 946684800 <= timestamp_seconds <= 4102444800:
                            created_at = datetime.fromtimestamp(timestamp_seconds)
                            if created_at >= cutoff_date:
                                history.append(outfit_data)
                        else:
                            logger.warning(f"⚠️ Skipping outfit with invalid timestamp: {timestamp_val} (computed: {timestamp_seconds})")
                    except (ValueError, OverflowError, OSError) as e:
                        logger.warning(f"⚠️ Failed to convert timestamp for outfit {outfit_data.get('id', 'unknown')}: {e}")
                        # Skip this outfit instead of crashing
            
            return history
        except Exception as e:
            print(f"Error getting outfit history: {e}")
            return []
    
    async def _get_validation_errors(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get validation errors from outfit generation attempts."""
        try:
            # Get logs that contain validation errors
            cutoff_date = datetime.now() - timedelta(days=days)
            
            logs_ref = self.db.collection('logs').where('userId', '==', user_id)
            docs = logs_ref.stream()
            
            errors = []
            for doc in docs:
                log_data = doc.to_dict()
                
                # Check if this log has validation errors
                if 'validationErrors' in log_data and log_data['validationErrors']:
                    # Convert timestamp with error handling
                    if 'timestamp' in log_data and hasattr(log_data['timestamp'], 'timestamp'):
                        try:
                            timestamp_val = log_data['timestamp'].timestamp()
                            # Handle both seconds and milliseconds timestamps
                            if timestamp_val > 1e12:  # Likely milliseconds
                                timestamp_seconds = timestamp_val / 1000.0
                            else:
                                timestamp_seconds = timestamp_val
                            # Sanity check: Unix timestamps should be roughly between 2000-2100
                            if 946684800 <= timestamp_seconds <= 4102444800:
                                log_time = datetime.fromtimestamp(timestamp_seconds)
                                if log_time >= cutoff_date:
                                    errors.append(log_data)
                            else:
                                logger.warning(f"⚠️ Skipping log with invalid timestamp: {timestamp_val} (computed: {timestamp_seconds})")
                        except (ValueError, OverflowError, OSError) as e:
                            logger.warning(f"⚠️ Failed to convert timestamp for log {log_data.get('id', 'unknown')}: {e}")
                            # Skip this log instead of crashing
            
            return errors
        except Exception as e:
            print(f"Error getting validation errors: {e}")
            return []
    
    async def _get_trending_styles(self) -> List[Dict[str, Any]]:
        """Get trending styles from the fashion trends service."""
        try:
            print("🔄 Attempting to get real trends from fashion trends service...")
            
            # Import the fashion trends service using absolute import
            from src.services.fashion_trends_service import FashionTrendsService
            
            # Create service instance and get real trends
            trends_service = FashionTrendsService()
            trending_styles = await trends_service.get_trending_styles()
            
            print(f"📊 Fashion trends service returned {len(trending_styles)} trends")
            
            # If no real trends are available, fall back to curated data
            if not trending_styles:
                print("⚠️ Warning: No real trends available, using fallback data")
                trending_styles = [
                    {
                        "name": "Coastal Grandmother",
                        "description": "Relaxed, sophisticated beach-inspired style",
                        "popularity": 85,
                        "key_items": ["Linen dresses", "Straw hats", "Boat shoes", "Light cardigans"],
                        "colors": ["Beige", "White", "Navy", "Sage"]
                    },
                    {
                        "name": "Dark Academia",
                        "description": "Intellectual, vintage-inspired dark aesthetic",
                        "popularity": 78,
                        "key_items": ["Tweed blazers", "Pleated skirts", "Oxford shoes", "Turtlenecks"],
                        "colors": ["Black", "Brown", "Burgundy", "Navy"]
                    },
                    {
                        "name": "Cottagecore",
                        "description": "Romantic, rural-inspired feminine style",
                        "popularity": 72,
                        "key_items": ["Floral dresses", "Aprons", "Mary Jane shoes", "Puff sleeves"],
                        "colors": ["Pink", "Mint", "Lavender", "Cream"]
                    },
                    {
                        "name": "Y2K Revival",
                        "description": "Early 2000s nostalgic fashion",
                        "popularity": 68,
                        "key_items": ["Low-rise jeans", "Crop tops", "Platform shoes", "Mini skirts"],
                        "colors": ["Pink", "Purple", "Silver", "Neon"]
                    },
                    {
                        "name": "Minimalist Luxury",
                        "description": "Clean, high-quality essentials",
                        "popularity": 82,
                        "key_items": ["Cashmere sweaters", "Tailored pants", "Leather bags", "Simple jewelry"],
                        "colors": ["Black", "White", "Beige", "Gray"]
                    }
                ]
            else:
                print("✅ Successfully retrieved real trends!")
                for i, trend in enumerate(trending_styles[:3], 1):
                    print(f"   {i}. {trend['name']} ({trend['popularity']}%)")
            
            return trending_styles
        except Exception as e:
            print(f"❌ Error getting trending styles: {e}")
            print(f"❌ Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            # Return fallback data if there's an error
            return [
                {
                    "name": "Coastal Grandmother",
                    "description": "Relaxed, sophisticated beach-inspired style",
                    "popularity": 85,
                    "key_items": ["Linen dresses", "Straw hats", "Boat shoes", "Light cardigans"],
                    "colors": ["Beige", "White", "Navy", "Sage"]
                },
                {
                    "name": "Dark Academia",
                    "description": "Intellectual, vintage-inspired dark aesthetic",
                    "popularity": 78,
                    "key_items": ["Tweed blazers", "Pleated skirts", "Oxford shoes", "Turtlenecks"],
                    "colors": ["Black", "Brown", "Burgundy", "Navy"]
                }
            ]
    
    def _get_wardrobe_stats(self, wardrobe: List[ClothingItem]) -> Dict[str, Any]:
        """Get comprehensive statistics about the user's wardrobe."""
        print(f"DEBUG: _get_wardrobe_stats called with {len(wardrobe)} items")
        
        if not wardrobe:
            print("DEBUG: No wardrobe items found")
            return {
                "total_items": 0,
                "item_types": {},
                "colors": {},
                "styles": {},
                "seasons": {},
                "brands": {},
                "price_range": {"min": 0, "max": 0, "avg": 0}
            }
        
        # Count item types
        item_types = {}
        colors = {}
        styles = {}
        seasons = {}
        brands = {}
        prices = []
        
        for i, item in enumerate(wardrobe):
            try:
                print(f"DEBUG: Processing item {i+1}: type={getattr(item, 'type', 'unknown')}, color={getattr(item, 'color', 'unknown')}")
                
                # Item types - safely get type
                item_type = getattr(item, 'type', 'unknown')
                if item_type:
                    item_types[str(item_type)] = item_types.get(str(item_type), 0) + 1
                
                # Colors - safely get color
                item_color = getattr(item, 'color', None)
                if item_color:
                    colors[str(item_color)] = colors.get(str(item_color), 0) + 1
                
                # Styles - safely get style list
                item_styles = getattr(item, 'style', [])
                if item_styles and isinstance(item_styles, list):
                    for style in item_styles:
                        if style:
                            styles[str(style)] = styles.get(str(style), 0) + 1
                
                # Seasons - safely get season list
                item_seasons = getattr(item, 'season', [])
                if item_seasons and isinstance(item_seasons, list):
                    for season in item_seasons:
                        if season:
                            seasons[str(season)] = seasons.get(str(season), 0) + 1
                
                # Brands - safely get brand
                item_brand = getattr(item, 'brand', None)
                if item_brand:
                    brands[str(item_brand)] = brands.get(str(item_brand), 0) + 1
                
                # Prices (if available) - safely get price
                item_price = getattr(item, 'price', None)
                if item_price:
                    try:
                        prices.append(float(item_price))
                    except (ValueError, TypeError):
                        print(f"DEBUG: Skipping invalid price for item {i+1}: {item_price}")
                        continue
                        
            except Exception as e:
                print(f"DEBUG: Error processing item {i+1}: {e}")
                print(f"DEBUG: Item data: {item}")
                continue
        
        print(f"DEBUG: Final item_types: {item_types}")
        print(f"DEBUG: Final colors: {colors}")
        print(f"DEBUG: Final styles: {styles}")
        
        # Calculate price statistics
        price_stats = {"min": 0, "max": 0, "avg": 0}
        if prices:
            try:
                price_stats = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": sum(prices) / len(prices)
                }
            except Exception as e:
                print(f"DEBUG: Error calculating price stats: {e}")
                price_stats = {"min": 0, "max": 0, "avg": 0}
        
        stats = {
            "total_items": len(wardrobe),
            "item_types": item_types,
            "colors": colors,
            "styles": styles,
            "seasons": seasons,
            "brands": brands,
            "price_range": price_stats
        }
        
        print(f"DEBUG: Returning stats: {stats}")
        return stats
    
    def _analyze_gaps(self, wardrobe: List[ClothingItem], outfit_history: List[Dict], validation_errors: List[Dict], trending_styles: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze wardrobe gaps based on multiple factors."""
        gaps = []
        
        # 1. Essential item gaps
        essential_gaps = self._analyze_essential_items(wardrobe)
        gaps.extend(essential_gaps)
        
        # 2. Occasion-based gaps
        occasion_gaps = self._analyze_occasion_coverage(wardrobe)
        gaps.extend(occasion_gaps)
        
        # 3. Style-based gaps
        style_gaps = self._analyze_style_coverage(wardrobe)
        gaps.extend(style_gaps)
        
        # 4. Trending style gaps
        trending_gaps = self._analyze_trending_style_gaps(wardrobe, trending_styles)
        gaps.extend(trending_gaps)
        
        # 5. Validation error-based gaps
        validation_gaps = self._analyze_validation_errors(validation_errors)
        gaps.extend(validation_gaps)
        
        # 6. Outfit generation failure gaps
        failure_gaps = self._analyze_outfit_failures(outfit_history)
        gaps.extend(failure_gaps)
        
        return gaps
    
    def _analyze_essential_items(self, wardrobe: List[ClothingItem]) -> List[Dict[str, Any]]:
        """Analyze missing essential wardrobe items."""
        gaps = []
        
        # Get all item types from wardrobe
        item_types = [item.type for item in wardrobe]
        
        # Debug: Print all item types found
        print(f"DEBUG: Found item types in wardrobe: {set(item_types)}")
        print(f"DEBUG: Total items: {len(wardrobe)}")
        
        # Create a mapping of item types to their counts
        type_counts = {}
        for item_type in item_types:
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        print(f"DEBUG: Type counts: {type_counts}")
        
        # Updated essential requirements based on actual wardrobe data
        # Map common item types to essential categories
        essential_mapping = {
            'shirt': ['shirt'],
            'pants': ['pants'],
            'shoes': ['shoes'],
            'jacket': ['jacket'],
            'sweater': ['sweater'],
            'shorts': ['shorts'],
            'accessory': ['accessory']
        }
        
        # Count items by essential category
        essential_counts = {}
        for essential, types in essential_mapping.items():
            count = 0
            for item_type in types:
                count += type_counts.get(item_type, 0)
            essential_counts[essential] = count
        
        print(f"DEBUG: Essential category counts: {essential_counts}")
        
        essential_requirements = {
            'shirt': {'min': 3, 'name': 'Tops/Shirts', 'priority': 'high'},
            'pants': {'min': 2, 'name': 'Bottoms', 'priority': 'high'},
            'shoes': {'min': 2, 'name': 'Shoes', 'priority': 'high'},
            'jacket': {'min': 1, 'name': 'Outerwear', 'priority': 'medium'},
            'sweater': {'min': 1, 'name': 'Sweaters', 'priority': 'medium'}
        }
        
        for item_type, requirement in essential_requirements.items():
            count = essential_counts.get(item_type, 0)
            print(f"DEBUG: Checking {item_type}: found {count}, need {requirement['min']}")
            
            if count < requirement['min']:
                gaps.append({
                    'id': f'essential-{item_type}',
                    'type': 'essential',
                    'category': 'Essentials',
                    'title': f"Missing {requirement['name']}",
                    'description': f"You have {count} {requirement['name'].lower()}, but need at least {requirement['min']} for a complete wardrobe.",
                    'severity': 'high' if count == 0 else 'medium',
                    'suggestedItems': self._get_suggestions_for_type(item_type),
                    'priority': requirement['min'] - count,
                    'data': {
                        'current_count': count,
                        'required_count': requirement['min'],
                        'item_type': item_type
                    }
                })
        
        print(f"DEBUG: Found {len(gaps)} essential gaps")
        return gaps
    
    def _analyze_occasion_coverage(self, wardrobe: List[ClothingItem]) -> List[Dict[str, Any]]:
        """Analyze wardrobe coverage for different occasions."""
        gaps = []
        
        occasion_requirements = {
            'casual': {
                'required_types': ['shirt', 'pants', 'shoes'],
                'suggested_styles': ['Casual', 'Comfortable'],
                'priority': 'medium'
            },
            'business': {
                'required_types': ['shirt', 'pants', 'shoes', 'jacket'],
                'suggested_styles': ['Business', 'Professional', 'Business Casual'],
                'priority': 'high'
            },
            'formal': {
                'required_types': ['shirt', 'pants', 'shoes', 'jacket'],
                'suggested_styles': ['Formal', 'Classic'],
                'priority': 'medium'
            }
        }
        
        for occasion, requirements in occasion_requirements.items():
            # Check if user has items for this occasion
            suitable_items = []
            for item in wardrobe:
                if (item.type in requirements['required_types'] and 
                    item.style and 
                    any(style in requirements['suggested_styles'] for style in item.style)):
                    suitable_items.append(item)
            
            if len(suitable_items) < len(requirements['required_types']):
                gaps.append({
                    'id': f'occasion-{occasion}',
                    'type': 'occasion',
                    'category': 'Occasions',
                    'title': f"Limited {occasion} wardrobe",
                    'description': f"You have {len(suitable_items)} suitable items for {occasion} occasions, but need more variety.",
                    'severity': 'high' if len(suitable_items) == 0 else 'medium',
                    'suggestedItems': self._get_suggestions_for_occasion(occasion),
                    'priority': len(requirements['required_types']) - len(suitable_items),
                    'data': {
                        'suitable_items': len(suitable_items),
                        'required_types': requirements['required_types'],
                        'occasion': occasion
                    }
                })
        
        return gaps
    
    def _analyze_style_coverage(self, wardrobe: List[ClothingItem]) -> List[Dict[str, Any]]:
        """Analyze coverage across different styles."""
        gaps = []
        
        # Extract all styles from wardrobe
        all_styles = set()
        for item in wardrobe:
            if item.style:
                all_styles.update(item.style)
        
        popular_styles = ['Casual', 'Business Casual', 'Formal', 'Classic', 'Preppy', 'Minimalist']
        
        for style in popular_styles:
            items_with_style = [item for item in wardrobe if item.style and style in item.style]
            
            if len(items_with_style) < 2:
                gaps.append({
                    'id': f'style-{style.lower().replace(" ", "-")}',
                    'type': 'style',
                    'category': 'Styles',
                    'title': f"Limited {style} items",
                    'description': f"You have {len(items_with_style)} {style.lower()} items. Consider adding more for variety.",
                    'severity': 'high' if len(items_with_style) == 0 else 'medium',
                    'suggestedItems': self._get_suggestions_for_style(style),
                    'priority': 2 - len(items_with_style),
                    'data': {
                        'style': style,
                        'item_count': len(items_with_style),
                        'available_styles': list(all_styles)
                    }
                })
        
        return gaps
    
    def _analyze_validation_errors(self, validation_errors: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze patterns in validation errors to identify gaps."""
        gaps = []
        
        if not validation_errors:
            return gaps
        
        # Count error types
        error_counts = {}
        for error_log in validation_errors:
            errors = error_log.get('validationErrors', [])
            for error in errors:
                error_counts[error] = error_counts.get(error, 0) + 1
        
        # Identify frequent errors
        for error, count in error_counts.items():
            if count >= 2:  # Error occurs frequently
                gaps.append({
                    'id': f'validation-{error.lower().replace(" ", "-")}',
                    'type': 'validation',
                    'category': 'Validation Errors',
                    'title': f"Frequent error: {error}",
                    'description': f"This error occurred {count} times in recent outfit generations.",
                    'severity': 'high' if count >= 5 else 'medium',
                    'suggestedItems': self._get_suggestions_for_validation_error(error),
                    'priority': count,
                    'data': {
                        'error_type': error,
                        'occurrence_count': count,
                        'last_occurrence': validation_errors[-1].get('timestamp', 'unknown')
                    }
                })
        
        return gaps
    
    def _analyze_outfit_failures(self, outfit_history: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze outfit generation failures to identify gaps."""
        gaps = []
        
        if not outfit_history:
            return gaps
        
        # Count failed vs successful outfits
        failed_outfits = [outfit for outfit in outfit_history if not outfit.get('wasSuccessful', True)]
        successful_outfits = [outfit for outfit in outfit_history if outfit.get('wasSuccessful', True)]
        
        failure_rate = len(failed_outfits) / len(outfit_history) if outfit_history else 0
        
        if failure_rate > 0.3:  # More than 30% failure rate
            gaps.append({
                'id': 'outfit-failure-rate',
                'type': 'validation',
                'category': 'Outfit Generation',
                'title': 'High outfit generation failure rate',
                'description': f"{(failure_rate * 100):.1f}% of outfit generation attempts failed. This suggests missing essential items.",
                'severity': 'high' if failure_rate > 0.5 else 'medium',
                'suggestedItems': ['Basic t-shirt', 'Jeans', 'Sneakers', 'Dress shirt', 'Dress pants'],
                'priority': int(failure_rate * 10),
                'data': {
                    'failure_rate': failure_rate,
                    'total_attempts': len(outfit_history),
                    'failed_attempts': len(failed_outfits),
                    'successful_attempts': len(successful_outfits)
                }
            })
        
        return gaps
    
    def _analyze_trending_style_gaps(self, wardrobe: List[ClothingItem], trending_styles: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze gaps in trending styles with robust matching."""
        gaps = []

        # Synonym map for common items (expand as needed)
        synonym_map = {
            'ballet flats': ['ballet flat', 'flats', 'flat shoes', 'ballet shoes'],
            'loafers': ['loafer', 'slip-ons'],
            'sneakers': ['sneaker', 'trainers', 'kicks'],
            'boots': ['boot', 'ankle boots', 'combat boots', 'chelsea boots'],
            'heels': ['heel', 'pumps', 'stilettos'],
            'sandals': ['sandal', 'slides'],
            # Add more as needed
        }

        def normalize(text):
            return text.lower().replace('-', ' ').replace('_', ' ').strip()

        def get_plural(word):
            """Get plural form of word."""
            if INFLECT_AVAILABLE:
                return p.plural_noun(word) or word
            else:
                return simple_plural(word)

        def get_singular(word):
            """Get singular form of word."""
            if INFLECT_AVAILABLE:
                return p.singular_noun(word) or word
            else:
                return simple_singular(word)

        for trend in trending_styles:
            trend_name = trend["name"]
            key_items = trend["key_items"]
            trend_colors = trend["colors"]

            # Expand key_items with synonyms and plural/singular forms
            expanded_key_items = set()
            for key_item in key_items:
                norm = normalize(key_item)
                expanded_key_items.add(norm)
                # Add plural and singular forms
                expanded_key_items.add(get_singular(norm))
                expanded_key_items.add(get_plural(norm))
                # Add synonyms
                for syn in synonym_map.get(norm, []):
                    expanded_key_items.add(normalize(syn))
                    expanded_key_items.add(get_singular(normalize(syn)))
                    expanded_key_items.add(get_plural(normalize(syn)))

            matching_items = []
            for item in wardrobe:
                fields_to_check = [
                    getattr(item, 'name', ''),
                    getattr(item, 'type', ''),
                    getattr(item, 'subType', ''),
                ]
                # Add tags from item
                fields_to_check.extend(getattr(item, 'tags', []))
                # Add tags from metadata.itemMetadata.tags if present
                if item.metadata and getattr(item.metadata, 'itemMetadata', None):
                    fields_to_check.extend(getattr(item.metadata.itemMetadata, 'tags', []))
                # Add styleTags from metadata if present
                if item.metadata and getattr(item.metadata, 'styleTags', None):
                    fields_to_check.extend(getattr(item.metadata, 'styleTags', []))
                # Normalize all fields
                fields_to_check = [normalize(str(f)) for f in fields_to_check if f]

                # Check for any match
                matches_key_item = any(
                    any(key in field or field in key for key in expanded_key_items)
                    for field in fields_to_check
                )
                # Check if item color matches trend colors
                matches_color = item.color in trend_colors if item.color else False
                # Check if item style might match trend (as before)
                matches_style = False
                if item.style:
                    style_keywords = {
                        "Coastal Grandmother": ["linen", "beach", "relaxed", "sophisticated"],
                        "Dark Academia": ["tweed", "vintage", "intellectual", "dark"],
                        "Cottagecore": ["floral", "romantic", "feminine", "rural"],
                        "Y2K Revival": ["retro", "nostalgic", "bold", "fun"],
                        "Minimalist Luxury": ["minimal", "luxury", "clean", "simple"]
                    }
                    trend_keywords = style_keywords.get(trend_name, [])
                    matches_style = any(keyword in style.lower() for style in item.style for keyword in trend_keywords)

                if matches_key_item or matches_color or matches_style:
                    matching_items.append(item)

            # If user has less than 2 items matching this trend, it's a gap
            if len(matching_items) < 2:
                gaps.append({
                    'id': f'trending-{trend_name.lower().replace(" ", "-")}',
                    'type': 'trending',
                    'category': 'Trending Styles',
                    'title': f"Limited {trend_name} items",
                    'description': f"You have {len(matching_items)} items that match the trending '{trend_name}' style. This style is {trend['popularity']}% popular right now.",
                    'severity': 'medium' if len(matching_items) == 1 else 'low',
                    'suggestedItems': trend["key_items"],
                    'priority': trend["popularity"] // 10,
                    'data': {
                        'trend_name': trend_name,
                        'trend_popularity': trend["popularity"],
                        'matching_items': len(matching_items),
                        'trend_colors': trend_colors,
                        'key_items': key_items
                    }
                })

        return gaps
    
    def _calculate_coverage(self, wardrobe: List[ClothingItem], gaps: List[Dict]) -> Dict[str, int]:
        """Calculate coverage percentages for different categories."""
        total_essentials = 5  # shirt, pants, shoes, jacket, sweater
        total_occasions = 3   # casual, business, formal
        total_styles = 6      # popular styles
        total_seasons = 4     # seasons
        
        essential_gaps = len([g for g in gaps if g['type'] == 'essential'])
        occasion_gaps = len([g for g in gaps if g['type'] == 'occasion'])
        style_gaps = len([g for g in gaps if g['type'] == 'style'])
        season_gaps = len([g for g in gaps if g['type'] == 'season'])
        
        return {
            'essentials': max(0, round(((total_essentials - essential_gaps) / total_essentials) * 100)),
            'occasions': max(0, round(((total_occasions - occasion_gaps) / total_occasions) * 100)),
            'styles': max(0, round(((total_styles - style_gaps) / total_styles) * 100)),
            'seasons': max(0, round(((total_seasons - season_gaps) / total_seasons) * 100))
        }
    
    def _generate_recommendations(self, wardrobe: List[ClothingItem], gaps: List[Dict], validation_errors: List[Dict], trending_styles: List[Dict]) -> List[str]:
        """Generate smart recommendations based on comprehensive analysis of style gaps, trends, and expansion opportunities."""
        recommendations = []
        
        # 1. Style Gap Analysis
        style_gaps = self._analyze_style_gaps(wardrobe)
        if style_gaps:
            recommendations.extend(style_gaps)
        
        # 2. Trend Integration Analysis
        trend_recommendations = self._analyze_trend_integration(wardrobe, trending_styles)
        if trend_recommendations:
            recommendations.extend(trend_recommendations)
        
        # 3. Style Expansion Opportunities
        expansion_recommendations = self._analyze_style_expansion(wardrobe)
        if expansion_recommendations:
            recommendations.extend(expansion_recommendations)
        
        # 4. Color Palette Enhancement
        color_recommendations = self._analyze_color_palette(wardrobe)
        if color_recommendations:
            recommendations.extend(color_recommendations)
        
        # 5. Occasion Coverage Analysis
        occasion_recommendations = self._analyze_occasion_coverage_for_recommendations(wardrobe)
        if occasion_recommendations:
            recommendations.extend(occasion_recommendations)
        
        # 6. Seasonal Optimization
        seasonal_recommendations = self._analyze_seasonal_optimization(wardrobe)
        if seasonal_recommendations:
            recommendations.extend(seasonal_recommendations)
        
        # 7. Validation Error Based Recommendations
        error_recommendations = self._analyze_validation_errors_for_recommendations(validation_errors)
        if error_recommendations:
            recommendations.extend(error_recommendations)
        
        # 8. Versatility Enhancement
        versatility_recommendations = self._analyze_versatility_enhancement(wardrobe)
        if versatility_recommendations:
            recommendations.extend(versatility_recommendations)
        
        # Limit to top 10 most impactful recommendations
        return recommendations[:10]
    
    def _analyze_style_gaps(self, wardrobe: List[ClothingItem]) -> List[str]:
        """Analyze gaps in style coverage and suggest improvements."""
        recommendations = []
        
        # Collect all styles from wardrobe
        all_styles = set()
        style_counts = {}
        for item in wardrobe:
            if item.style:
                for style in item.style:
                    all_styles.add(style)
                    style_counts[style] = style_counts.get(style, 0) + 1
        
        # Identify underrepresented styles
        total_items = len(wardrobe)
        underrepresented_styles = []
        for style, count in style_counts.items():
            if count < max(1, total_items * 0.1):  # Less than 10% of wardrobe
                underrepresented_styles.append(style)
        
        # Check for missing major style categories
        major_styles = {
            'Casual', 'Business Casual', 'Formal', 'Classic', 'Trendy', 
            'Minimalist', 'Preppy', 'Streetwear', 'Athleisure'
        }
        missing_major_styles = major_styles - all_styles
        
        if missing_major_styles:
            missing_list = ', '.join(list(missing_major_styles)[:3])
            recommendations.append(f"Expand your style repertoire by adding {missing_list} pieces for more outfit variety.")
        
        if underrepresented_styles:
            style_list = ', '.join(underrepresented_styles[:3])
            recommendations.append(f"Strengthen your {style_list} collection to create more balanced outfits.")
        
        return recommendations
    
    def _analyze_trend_integration(self, wardrobe: List[ClothingItem], trending_styles: List[Dict]) -> List[str]:
        """Analyze how to integrate trending styles into existing wardrobe."""
        recommendations = []
        
        if not trending_styles:
            return recommendations
        
        # Get current wardrobe styles
        current_styles = set()
        for item in wardrobe:
            if item.style:
                current_styles.update(item.style)
        
        # Analyze trending styles that complement current wardrobe
        compatible_trends = []
        for trend in trending_styles[:5]:  # Top 5 trends
            trend_name = trend.get('name', '').lower()
            trend_styles = trend.get('related_styles', [])
            
            # Check if trend complements existing styles
            if any(style.lower() in current_styles for style in trend_styles):
                compatible_trends.append(trend_name)
        
        if compatible_trends:
            trend_list = ', '.join(compatible_trends[:3])
            recommendations.append(f"Integrate trending {trend_list} pieces that complement your existing style.")
        
        # Suggest trend-based additions
        if len(trending_styles) > 0:
            top_trend = trending_styles[0].get('name', 'trending styles')
            recommendations.append(f"Consider adding {top_trend} pieces to stay current while maintaining your personal style.")
        
        return recommendations
    
    def _analyze_style_expansion(self, wardrobe: List[ClothingItem]) -> List[str]:
        """Analyze opportunities for style expansion and experimentation."""
        recommendations = []
        
        # Analyze current style distribution
        style_distribution = {}
        for item in wardrobe:
            if item.style:
                for style in item.style:
                    style_distribution[style] = style_distribution.get(style, 0) + 1
        
        # Find dominant styles
        if style_distribution:
            dominant_style = max(style_distribution, key=style_distribution.get)
            dominant_count = style_distribution[dominant_style]
            total_items = len(wardrobe)
            
            if dominant_count > total_items * 0.4:  # More than 40% of wardrobe
                recommendations.append(f"Your wardrobe is heavily {dominant_style}-focused. Consider experimenting with contrasting styles for more outfit variety.")
        
        # Suggest style combinations
        if len(style_distribution) >= 3:
            recommendations.append("Mix and match your diverse style collection to create unique outfit combinations.")
        
        return recommendations
    
    def _analyze_color_palette(self, wardrobe: List[ClothingItem]) -> List[str]:
        """Analyze color palette and suggest improvements."""
        recommendations = []
        
        # Collect all colors
        colors = {}
        for item in wardrobe:
            color = item.color.lower() if item.color else 'unknown'
            colors[color] = colors.get(color, 0) + 1
        
        # Analyze color distribution
        if colors:
            total_items = len(wardrobe)
            neutral_colors = {'black', 'white', 'gray', 'grey', 'beige', 'navy', 'brown'}
            neutral_count = sum(colors.get(color, 0) for color in neutral_colors)
            
            if neutral_count > total_items * 0.7:  # More than 70% neutral
                recommendations.append("Your wardrobe is mostly neutral. Add colorful statement pieces to create more vibrant outfits.")
            elif neutral_count < total_items * 0.3:  # Less than 30% neutral
                recommendations.append("Add more neutral basics to create versatile foundation pieces for your colorful wardrobe.")
            
            # Check for color variety
            if len(colors) < 5:
                recommendations.append("Expand your color palette with complementary and contrasting colors for more outfit options.")
        
        return recommendations
    
    def _analyze_occasion_coverage_for_recommendations(self, wardrobe: List[ClothingItem]) -> List[str]:
        """Analyze occasion coverage and suggest improvements."""
        recommendations = []
        
        # Collect all occasions
        occasions = {}
        for item in wardrobe:
            if item.occasion:
                for occasion in item.occasion:
                    occasions[occasion] = occasions.get(occasion, 0) + 1
        
        # Check for missing essential occasions
        essential_occasions = {'casual', 'business casual', 'formal'}
        missing_occasions = essential_occasions - set(occasions.keys())
        
        if missing_occasions:
            missing_list = ', '.join(list(missing_occasions))
            recommendations.append(f"Add pieces for {missing_list} occasions to ensure you're prepared for any event.")
        
        # Check for weak occasion coverage
        total_items = len(wardrobe)
        weak_occasions = []
        for occasion, count in occasions.items():
            if count < max(1, total_items * 0.15):  # Less than 15% of wardrobe
                weak_occasions.append(occasion)
        
        if weak_occasions:
            weak_list = ', '.join(weak_occasions[:2])
            recommendations.append(f"Strengthen your {weak_list} wardrobe to create more outfit options for these occasions.")
        
        return recommendations
    
    def _analyze_seasonal_optimization(self, wardrobe: List[ClothingItem]) -> List[str]:
        """Analyze seasonal coverage and suggest optimizations."""
        recommendations = []
        
        # Collect seasonal distribution
        seasons = {}
        for item in wardrobe:
            if item.season:
                for season in item.season:
                    seasons[season] = seasons.get(season, 0) + 1
        
        # Check for seasonal gaps
        essential_seasons = {'spring', 'summer', 'fall', 'winter'}
        missing_seasons = essential_seasons - set(seasons.keys())
        
        if missing_seasons:
            missing_list = ', '.join(list(missing_seasons))
            recommendations.append(f"Add pieces for {missing_list} to ensure year-round wardrobe coverage.")
        
        # Check for seasonal balance
        if seasons:
            total_items = len(wardrobe)
            weak_seasons = []
            for season, count in seasons.items():
                if count < max(1, total_items * 0.2):  # Less than 20% of wardrobe
                    weak_seasons.append(season)
            
            if weak_seasons:
                weak_list = ', '.join(weak_seasons[:2])
                recommendations.append(f"Enhance your {weak_list} collection for better seasonal balance.")
        
        return recommendations
    
    def _analyze_validation_errors_for_recommendations(self, validation_errors: List[Dict]) -> List[str]:
        """Analyze validation errors to generate targeted recommendations."""
        recommendations = []
        
        if not validation_errors:
            return recommendations
        
        # Analyze error patterns
        error_types = {}
        for error in validation_errors:
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Generate recommendations based on error types
        if error_types.get("missing_items", 0) > 0:
            recommendations.append("Add missing essential items to improve outfit generation success.")
        
        if error_types.get("style_mismatch", 0) > 0:
            recommendations.append("Add more versatile pieces that work across different styles.")
        
        if error_types.get("color_clash", 0) > 0:
            recommendations.append("Add neutral and complementary colored items to avoid color conflicts.")
        
        if error_types.get("seasonal_mismatch", 0) > 0:
            recommendations.append("Improve seasonal coverage to create weather-appropriate outfits.")
        
        return recommendations
    
    def _analyze_versatility_enhancement(self, wardrobe: List[ClothingItem]) -> List[str]:
        """Analyze opportunities to enhance wardrobe versatility."""
        recommendations = []
        
        # Check for layering pieces
        layering_items = [item for item in wardrobe if item.type in ['sweater', 'jacket', 'cardigan']]
        if len(layering_items) < 3:
            recommendations.append("Add more layering pieces to create versatile outfits for different temperatures and occasions.")
        
        # Check for transitional pieces
        transitional_items = [item for item in wardrobe if 'all' in item.season or len(item.season) > 2]
        if len(transitional_items) < 5:
            recommendations.append("Add more transitional pieces that work across multiple seasons for better wardrobe efficiency.")
        
        # Check for multi-occasion pieces
        multi_occasion_items = [item for item in wardrobe if len(item.occasion) > 2]
        if len(multi_occasion_items) < 5:
            recommendations.append("Invest in versatile pieces that work for multiple occasions to maximize your wardrobe's potential.")
        
        return recommendations
    
    def _get_suggestions_for_type(self, item_type: str) -> List[str]:
        """Get suggested items for a specific type."""
        suggestions = {
            'shirt': ['Basic t-shirt', 'Button-up shirt', 'Polo shirt', 'Dress shirt'],
            'pants': ['Jeans', 'Dress pants', 'Chinos', 'Khakis'],
            'shoes': ['Casual sneakers', 'Dress shoes', 'Boots', 'Loafers'],
            'jacket': ['Blazer', 'Cardigan', 'Light jacket', 'Suit jacket'],
            'sweater': ['Pullover sweater', 'Cardigan', 'Turtleneck', 'Cable knit sweater']
        }
        return suggestions.get(item_type, [])
    
    def _get_suggestions_for_occasion(self, occasion: str) -> List[str]:
        """Get suggested items for a specific occasion."""
        suggestions = {
            'casual': ['Casual t-shirt', 'Jeans', 'Sneakers', 'Hoodie'],
            'business': ['Dress shirt', 'Dress pants', 'Dress shoes', 'Blazer'],
            'formal': ['Formal shirt', 'Suit pants', 'Oxford shoes', 'Suit jacket']
        }
        return suggestions.get(occasion, [])
    
    def _get_suggestions_for_style(self, style: str) -> List[str]:
        """Get suggested items for a specific style."""
        suggestions = {
            'Casual': ['Casual shirt', 'Jeans', 'Sneakers'],
            'Business Casual': ['Button-up shirt', 'Chinos', 'Loafers'],
            'Formal': ['Dress shirt', 'Suit pants', 'Dress shoes'],
            'Classic': ['Classic shirt', 'Dress pants', 'Oxford shoes'],
            'Preppy': ['Polo shirt', 'Khakis', 'Loafers'],
            'Minimalist': ['Basic t-shirt', 'Simple pants', 'Clean sneakers']
        }
        return suggestions.get(style, [])
    
    def _get_suggestions_for_validation_error(self, error: str) -> List[str]:
        """Get suggested items based on validation error."""
        error_suggestions = {
            'missing shoes': ['Casual sneakers', 'Dress shoes', 'Boots'],
            'missing pants': ['Jeans', 'Dress pants', 'Chinos'],
            'missing shirt': ['T-shirt', 'Button-up shirt', 'Polo shirt'],
            'incompatible colors': ['Neutral colored items', 'Black basics', 'White basics'],
            'inappropriate for occasion': ['Dress shirt', 'Dress pants', 'Formal shoes']
        }
        
        for error_key, suggestions in error_suggestions.items():
            if error_key in error.lower():
                return suggestions
        
        return ['Basic wardrobe essentials']

    def _analyze_error_patterns(self, validation_errors: List[Dict], outfit_history: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in validation errors and outfit failures."""
        if not validation_errors and not outfit_history:
            return {
                "common_errors": [],
                "error_frequency": {},
                "failure_reasons": [],
                "improvement_areas": []
            }
        
        # Analyze validation errors
        error_types = {}
        for error in validation_errors:
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Analyze outfit failures
        failure_reasons = []
        for outfit in outfit_history:
            if not outfit.get("success", True):
                reason = outfit.get("error", "Unknown failure")
                failure_reasons.append(reason)
        
        # Find most common errors
        common_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Identify improvement areas
        improvement_areas = []
        if error_types.get("missing_items", 0) > 0:
            improvement_areas.append("Add missing essential items")
        if error_types.get("style_mismatch", 0) > 0:
            improvement_areas.append("Improve style coordination")
        if error_types.get("color_clash", 0) > 0:
            improvement_areas.append("Add more versatile color options")
        if error_types.get("seasonal_mismatch", 0) > 0:
            improvement_areas.append("Improve seasonal coverage")
        
        return {
            "common_errors": common_errors,
            "error_frequency": error_types,
            "failure_reasons": failure_reasons,
            "improvement_areas": improvement_areas,
            "total_errors": len(validation_errors),
            "failure_rate": len([o for o in outfit_history if not o.get("success", True)]) / max(len(outfit_history), 1) * 100
        }

    def _preprocess_item_data(self, item_data: dict) -> dict:
        """Preprocess item data to fix common validation issues."""
        try:
            # Create a copy to avoid modifying the original
            processed_data = item_data.copy()
            
            # Fix timestamp fields - convert float to int if needed
            if 'createdAt' in processed_data and isinstance(processed_data['createdAt'], float):
                processed_data['createdAt'] = int(processed_data['createdAt'])
            if 'updatedAt' in processed_data and isinstance(processed_data['updatedAt'], float):
                processed_data['updatedAt'] = int(processed_data['updatedAt'])
            
            # Fix material enum issues in metadata
            if 'metadata' in processed_data and isinstance(processed_data['metadata'], dict):
                metadata = processed_data['metadata']
                
                # Fix visualAttributes material issues
                if 'visualAttributes' in metadata and isinstance(metadata['visualAttributes'], dict):
                    va = metadata['visualAttributes']
                    
                    # Fix material field
                    if 'material' in va and isinstance(va['material'], str):
                        va['material'] = self._normalize_material(va['material'])
                    
                    # Fix materialCompatibility issues
                    if 'materialCompatibility' in va and isinstance(va['materialCompatibility'], dict):
                        mc = va['materialCompatibility']
                        
                        # Fix compatibleMaterials
                        if 'compatibleMaterials' in mc and isinstance(mc['compatibleMaterials'], list):
                            mc['compatibleMaterials'] = [
                                self._normalize_material(mat) if isinstance(mat, str) else mat 
                                for mat in mc['compatibleMaterials']
                            ]
                        
                        # Fix weatherAppropriate materials
                        if 'weatherAppropriate' in mc and isinstance(mc['weatherAppropriate'], dict):
                            for season, materials in mc['weatherAppropriate'].items():
                                if isinstance(materials, list):
                                    mc['weatherAppropriate'][season] = [
                                        self._normalize_material(mat) if isinstance(mat, str) else mat 
                                        for mat in materials
                                    ]
                    
                    # Fix temperatureCompatibility issues
                    if 'temperatureCompatibility' in va and isinstance(va['temperatureCompatibility'], dict):
                        tc = va['temperatureCompatibility']
                        
                        # Fix minTemp and maxTemp - handle non-numeric values
                        if 'minTemp' in tc:
                            if isinstance(tc['minTemp'], str):
                                # Extract numeric value from strings like ">32°F" or "32"
                                import re
                                match = re.search(r'(\d+)', tc['minTemp'])
                                if match:
                                    tc['minTemp'] = int(match.group(1))
                                else:
                                    tc['minTemp'] = 32  # Default fallback
                            elif isinstance(tc['minTemp'], float):
                                tc['minTemp'] = int(tc['minTemp'])
                        
                        if 'maxTemp' in tc:
                            if isinstance(tc['maxTemp'], str):
                                # Extract numeric value from strings like "<85°F" or "85"
                                import re
                                match = re.search(r'(\d+)', tc['maxTemp'])
                                if match:
                                    tc['maxTemp'] = int(match.group(1))
                                else:
                                    tc['maxTemp'] = 85  # Default fallback
                            elif isinstance(tc['maxTemp'], float):
                                tc['maxTemp'] = int(tc['maxTemp'])
                        
                        # Fix materialPreferences
                        if 'materialPreferences' in tc and isinstance(tc['materialPreferences'], list):
                            tc['materialPreferences'] = [
                                self._normalize_material(mat) if isinstance(mat, str) else mat 
                                for mat in tc['materialPreferences']
                            ]
            
            return processed_data
            
        except Exception as e:
            print(f"Error preprocessing item data: {e}")
            return item_data
    
    def _normalize_material(self, material: str) -> str:
        """Normalize material strings to valid enum values."""
        if not isinstance(material, str):
            return material
        
        material_lower = material.lower()
        
        # Map common material variations to valid enum values
        material_mapping = {
            # Standard materials
            'cotton': 'cotton',
            'wool': 'wool',
            'silk': 'silk',
            'linen': 'linen',
            'denim': 'denim',
            'leather': 'leather',
            'synthetic': 'synthetic',
            'knit': 'knit',
            'fleece': 'fleece',
            
            # Common variations and synonyms
            'polyester': 'synthetic',
            'mesh': 'synthetic',
            'chinos': 'cotton',  # Chinos are typically cotton
            'synthetic blends': 'synthetic',
            'light cotton': 'cotton',
            'corduroy': 'cotton',  # Corduroy is typically cotton
            
            # Handle capitalized versions
            'cotton': 'cotton',
            'linen': 'linen',
            'wool': 'wool',
            'denim': 'denim',
            'leather': 'leather',
            'synthetic': 'synthetic',
            'knit': 'knit',
            'fleece': 'fleece',
            'polyester': 'synthetic',
            'mesh': 'synthetic',
            'chinos': 'cotton',
            'synthetic blends': 'synthetic',
            'light cotton': 'cotton',
            'corduroy': 'cotton'
        }
        
        return material_mapping.get(material_lower, 'other')
    
