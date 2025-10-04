from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from pytrends.request import TrendReq
from google.cloud import firestore
import uuid
import time

logger = logging.getLogger(__name__)

class FashionTrendsService:
    def __init__(self):
        self.db = firestore.Client()
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
        # Comprehensive fashion keywords for trend analysis
        self.fashion_keywords = [
            # Style Aesthetics
            "y2k fashion", "coastal chic", "grunge aesthetic", "old money style", 
            "techwear", "boho fashion", "minimalist fashion", "romantic core", 
            "dark academia", "streetwear", "cottagecore", "cyberpunk fashion",
            "vintage fashion", "preppy style", "goth fashion", "kawaii fashion",
            
            # Specific Trends
            "oversized blazer", "cargo pants", "platform shoes", "micro bags",
            "ballet flats", "corset tops", "low rise jeans", "high rise jeans",
            "mom jeans", "dad sneakers", "chunky sneakers", "mule shoes",
            
            # Colors & Patterns
            "sage green fashion", "millennial pink", "gen z yellow", "bubblegum pink",
            "checkerboard pattern", "animal print", "floral print", "stripes fashion",
            
            # Seasonal Trends
            "spring fashion 2024", "summer fashion 2024", "fall fashion 2024",
            "winter fashion 2024", "holiday fashion", "resort wear"
        ]
        
        # Gender-specific fashion keywords
        self.gender_specific_keywords = {
            "female": [
                # Women's specific trends
                "women's fashion", "feminine style", "dress trends", "women's blazer",
                "women's jeans", "women's shoes", "women's accessories",
                "women's summer fashion", "women's winter fashion",
                "women's workwear", "women's casual fashion", "women's formal wear",
                "women's streetwear", "women's vintage fashion", "women's boho fashion",
                "women's minimalist fashion", "women's romantic fashion",
                "women's dark academia", "women's cottagecore", "women's y2k fashion",
                "women's coastal chic", "women's old money style", "women's techwear"
            ],
            "male": [
                # Men's specific trends
                "men's fashion", "masculine style", "men's suits", "men's blazer",
                "men's jeans", "men's shoes", "men's accessories",
                "men's summer fashion", "men's winter fashion",
                "men's workwear", "men's casual fashion", "men's formal wear",
                "men's streetwear", "men's vintage fashion", "men's minimalist fashion",
                "men's dark academia", "men's techwear", "men's streetwear",
                "men's y2k fashion", "men's coastal chic", "men's old money style",
                "men's grunge aesthetic", "men's preppy style"
            ],
            "unisex": [
                # Unisex/neutral trends
                "unisex fashion", "gender neutral fashion", "androgynous style",
                "unisex streetwear", "unisex minimalist fashion", "unisex vintage fashion",
                "unisex techwear", "unisex dark academia", "unisex y2k fashion",
                "unisex coastal chic", "unisex old money style", "unisex grunge aesthetic"
            ]
        }
        
        # Gender-specific fashion items (inherently gendered)
        self.gender_specific_items = {
            "female": [
                # Women's specific items
                "ballet flats", "heels", "stilettos", "pumps", "mules", "mary janes",
                "dresses", "skirts", "blouses", "corsets", "bras", "lingerie",
                "handbags", "purses", "clutches", "tote bags", "crossbody bags",
                "jewelry", "necklaces", "earrings", "bracelets", "rings",
                "makeup", "lipstick", "foundation", "eyeshadow", "mascara",
                "nail polish", "perfume", "hair accessories", "headbands", "hair clips",
                "scarves", "shawls", "wraps", "cardigans", "sweaters",
                "romantic", "feminine", "girly", "cute", "elegant", "graceful"
            ],
            "male": [
                # Men's specific items
                "suits", "ties", "bow ties", "cufflinks", "dress shirts", "oxford shirts",
                "dress pants", "slacks", "khakis", "chinos", "dress shoes", "oxfords",
                "loafers", "wingtips", "derby shoes", "boots", "work boots",
                "wallets", "briefcases", "messenger bags", "duffel bags",
                "cologne", "aftershave", "beard oil", "beard trimmer",
                "watches", "belts", "socks", "boxers", "briefs",
                "masculine", "rugged", "strong", "bold", "confident", "powerful"
            ]
        }
        
        # Style mappings for better categorization
        self.style_mappings = {
            "y2k fashion": ["y2k", "retro", "nostalgic", "early 2000s"],
            "coastal chic": ["coastal", "beach", "resort", "summer"],
            "grunge aesthetic": ["grunge", "edgy", "rock", "alternative"],
            "old money style": ["preppy", "elegant", "sophisticated", "luxury"],
            "techwear": ["tech", "futuristic", "urban", "functional"],
            "boho fashion": ["bohemian", "hippie", "free-spirited", "artistic"],
            "minimalist fashion": ["minimal", "clean", "simple", "essential"],
            "romantic core": ["romantic", "feminine", "soft", "dreamy"],
            "dark academia": ["academic", "intellectual", "mysterious", "scholarly"],
            "streetwear": ["urban", "casual", "trendy", "street"],
            "cottagecore": ["cottage", "rural", "whimsical", "nature"],
            "cyberpunk fashion": ["cyber", "futuristic", "edgy", "tech"],
            "vintage fashion": ["vintage", "retro", "classic", "timeless"],
            "preppy style": ["preppy", "classic", "traditional", "clean"],
            "goth fashion": ["goth", "dark", "mysterious", "alternative"],
            "kawaii fashion": ["kawaii", "cute", "japanese", "playful"]
        }

    async def fetch_and_store_trends(self) -> Dict[str, Any]:
        """Fetch fashion trends and store in Firestore."""
        try:
            logger.info("Starting fashion trends fetch")
            
            # Check if we already fetched today
            if await self._already_fetched_today():
                logger.info("Trends already fetched today, skipping")
                return {"status": "skipped", "reason": "already_fetched_today"}
            
            # Fetch trends in batches to avoid rate limits
            all_trends = []
            batch_size = 5  # Google Trends allows 5 keywords per request
            
            for i in range(0, len(self.fashion_keywords), batch_size):
                batch = self.fashion_keywords[i:i + batch_size]
                logger.info(f"Fetching batch {i//batch_size + 1}: {batch}")
                
                try:
                    # Build payload and fetch data
                    self.pytrends.build_payload(
                        batch, 
                        cat=0,  # All categories
                        timeframe='now 7-d',  # Last 7 days
                        geo='US'  # United States
                    )
                    
                    # Get interest over time data
                    data = self.pytrends.interest_over_time()
                    
                    if data.empty:
                        logger.warning(f"No data returned for batch: {batch}")
                        continue
                    
                    # Process each trend in the batch
                    for trend in batch:
                        if trend in data.columns:
                            # Calculate average score for the week
                            avg_score = float(data[trend].mean())
                            
                            # Get trend direction (increasing/decreasing)
                            trend_direction = self._calculate_trend_direction(data[trend])
                            
                            # Create trend document
                            trend_doc = {
                                "id": str(uuid.uuid4()),
                                "name": trend,
                                "display_name": self._format_display_name(trend),
                                "score": round(avg_score, 2),
                                "trend_direction": trend_direction,
                                "category": self._categorize_trend(trend),
                                "related_styles": style_mappings.get(trend, []) if style_mappings else []),
                                "source": "google_trends",
                                "geo": "US",
                                "timeframe": "7d",
                                "timestamp": datetime.now().isoformat(),
                                "last_updated": datetime.now().isoformat()
                            }
                            
                            all_trends.append(trend_doc)
                            
                            # Store in Firestore
                            await self._store_trend(trend_doc)
                            
                            logger.info(f"Stored trend: {trend} (score: {avg_score})")
                    
                    # Rate limiting - wait between batches
                    if i + batch_size < len(self.fashion_keywords):
                        await asyncio.sleep(2)  # 2 second delay between batches
                        
                except Exception as e:
                    logger.error(f"Error fetching batch {batch}: {str(e)}")
                    continue
            
            # Store fetch timestamp
            await self._store_fetch_timestamp()
            
            logger.info(f"Successfully fetched and stored {len(all_trends)} trends")
            return {
                "status": "success",
                "trends_fetched": len(all_trends),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_and_store_trends: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_trending_styles(self, gender: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trending styles from Firestore, optionally filtered by gender."""
        try:
            # print(f"🔍 Trends Service: Starting get_trending_styles with gender: {gender}")
            
            # Get trends from the last 7 days, sorted by score
            trends_ref = self.db.collection("fashion_trends")
            query = trends_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(50)  # Get more to filter
            
            docs = query.stream()
            trends = []
            all_trends = []
            seen_trend_names = set()  # Track seen trend names to avoid duplicates
            
            for doc in docs:
                trend_data = doc.to_dict()
                trend_name = (trend_data.get("name", "") if trend_data else "").lower()
                all_trends.append(trend_name)
                
                # Skip if we've already seen this trend name (deduplication)
                if trend_name in seen_trend_names:
                    print(f"🔄 Skipping duplicate trend: {trend_name}")
                    continue
                
                # Filter by gender if specified
                if gender and gender.lower() in ["male", "female"]:
                    should_include = self._is_trend_appropriate_for_gender(trend_name, gender.lower())
                    if should_include:
                        trends.append(self._format_trend_data(trend_data))
                        seen_trend_names.add(trend_name)  # Mark as seen
                else:
                    # For unisex or no gender specified, include all trends
                    trends.append(self._format_trend_data(trend_data))
                    seen_trend_names.add(trend_name)  # Mark as seen
                
                # Limit to top 20 after filtering
                if len(trends) >= 20:
                    break
            
            # print(f"🔍 Trends Service: Total trends found: {len(all_trends)}")
            # print(f"🔍 Trends Service: Trends after gender filtering and deduplication: {len(trends)}")
            # print(f"🔍 Trends Service: Sample trends before filtering: {all_trends[:5]}")
            # print(f"🔍 Trends Service: Sample trends after filtering: {[(t.get('name', '') if t else '') for t in trends[:5]]}")
            
            # Check for ballet flats specifically
            ballet_flats_before = [t for t in all_trends if 'ballet' in t]
            ballet_flats_after = [((t.get('name', '') if t else '') if t else '') for t in trends if 'ballet' in ((t.get('name', '') if t else '') if t else '').lower()]
            # print(f"🔍 Trends Service: Ballet flats before filtering: {ballet_flats_before}")
            # print(f"🔍 Trends Service: Ballet flats after filtering: {ballet_flats_after}")
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting trending styles: {str(e)}")
            return []

    def _is_trend_appropriate_for_gender(self, trend_name: str, gender: str) -> bool:
        """Check if a trend is appropriate for the specified gender."""
        trend_lower = trend_name.lower()
        
        # print(f"🔍 Gender Filter: Checking trend '{trend_name}' for gender '{gender}'")
        
        if gender == "female":
            # For female users, include:
            # 1. Women's specific keywords
            # 2. Women's specific items
            # 3. General/unisex trends
            # 4. Exclude men's specific items
            
            # Check for women's specific keywords
            for keyword in gender_specific_keywords.get("female", []) if gender_specific_keywords else []):
                if keyword.lower() in trend_lower:
                    # print(f"✅ Gender Filter: '{trend_name}' matches female keyword '{keyword}'")
                    return True
            
            # Check for women's specific items
            for item in gender_specific_items.get("female", []) if gender_specific_items else []):
                if item.lower() in trend_lower:
                    # print(f"✅ Gender Filter: '{trend_name}' matches female item '{item}'")
                    return True
            
            # Check for unisex keywords
            for keyword in gender_specific_keywords.get("unisex", []) if gender_specific_keywords else []):
                if keyword.lower() in trend_lower:
                    # print(f"✅ Gender Filter: '{trend_name}' matches unisex keyword '{keyword}'")
                    return True
            
            # Exclude men's specific items
            for item in gender_specific_items.get("male", []) if gender_specific_items else []):
                if item.lower() in trend_lower:
                    # print(f"❌ Gender Filter: '{trend_name}' excluded - matches male item '{item}'")
                    return False
            
            # Exclude men's specific keywords
            for keyword in gender_specific_keywords.get("male", []) if gender_specific_keywords else []):
                if keyword.lower() in trend_lower:
                    # print(f"❌ Gender Filter: '{trend_name}' excluded - matches male keyword '{keyword}'")
                    return False
            
            # Include general trends that don't have gender-specific terms
            # print(f"✅ Gender Filter: '{trend_name}' included as general trend for female")
            return True
            
        elif gender == "male":
            # For male users, include:
            # 1. Men's specific keywords
            # 2. Men's specific items
            # 3. General/unisex trends
            # 4. Exclude women's specific items
            
            # Check for men's specific keywords
            for keyword in gender_specific_keywords.get("male", []) if gender_specific_keywords else []):
                if keyword.lower() in trend_lower:
                    # print(f"✅ Gender Filter: '{trend_name}' matches male keyword '{keyword}'")
                    return True
            
            # Check for men's specific items
            for item in gender_specific_items.get("male", []) if gender_specific_items else []):
                if item.lower() in trend_lower:
                    # print(f"✅ Gender Filter: '{trend_name}' matches male item '{item}'")
                    return True
            
            # Check for unisex keywords
            for keyword in gender_specific_keywords.get("unisex", []) if gender_specific_keywords else []):
                if keyword.lower() in trend_lower:
                    # print(f"✅ Gender Filter: '{trend_name}' matches unisex keyword '{keyword}'")
                    return True
            
            # Exclude women's specific items
            for item in gender_specific_items.get("female", []) if gender_specific_items else []):
                if item.lower() in trend_lower:
                    # print(f"❌ Gender Filter: '{trend_name}' excluded - matches female item '{item}'")
                    return False
            
            # Exclude women's specific keywords
            for keyword in gender_specific_keywords.get("female", []) if gender_specific_keywords else []):
                if keyword.lower() in trend_lower:
                    # print(f"❌ Gender Filter: '{trend_name}' excluded - matches female keyword '{keyword}'")
                    return False
            
            # Include general trends that don't have gender-specific terms
            # print(f"✅ Gender Filter: '{trend_name}' included as general trend for male")
            return True
        
        # For unisex or unknown gender, include everything
        # print(f"✅ Gender Filter: '{trend_name}' included for unisex")
        return True

    def _format_trend_data(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format trend data for consistent output."""
        return {
            "name": ((trend_data.get("display_name", trend_data.get("name") if trend_data else trend_data.get("name") if trend_data else trend_data.get("name")),
            "description": self._generate_trend_description(trend_data),
            "popularity": int((trend_data.get("score", 0) if trend_data else 0)),
            "trend_direction": (trend_data.get("trend_direction", "stable") if trend_data else "stable"),
            "category": (trend_data.get("category", "general") if trend_data else "general"),
            "key_items": self._get_key_items_for_trend(trend_data),
            "colors": self._get_colors_for_trend(trend_data),
            "related_styles": (trend_data.get("related_styles", []) if trend_data else []),
            "last_updated": (trend_data.get("last_updated") if trend_data else None)
        }

    async def _already_fetched_today(self) -> bool:
        """Check if trends were already fetched today."""
        try:
            today = datetime.now().date().isoformat()
            fetch_log_ref = self.db.collection("fashion_trends_fetch_log").document(today)
            doc = fetch_log_ref.get() if fetch_log_ref else None
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking fetch log: {str(e)}")
            return False

    async def _store_fetch_timestamp(self):
        """Store the fetch timestamp."""
        try:
            today = datetime.now().date().isoformat()
            fetch_log_ref = self.db.collection("fashion_trends_fetch_log").document(today)
            fetch_log_ref.set({
                "date": today,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            })
        except Exception as e:
            logger.error(f"Error storing fetch timestamp: {str(e)}")

    async def _store_trend(self, trend_doc: Dict[str, Any]):
        """Store a single trend in Firestore."""
        try:
            # Store in fashion_trends collection
            trends_ref = self.db.collection("fashion_trends").document(trend_doc["id"])
            trends_ref.set(trend_doc)
            
            # Also store in a daily collection for historical tracking
            today = datetime.now().date().isoformat()
            daily_ref = self.db.collection("fashion_trends_daily").document(today)
            daily_doc = daily_ref.get() if daily_ref else None
            
            if daily_doc.exists:
                daily_data = daily_doc.to_dict()
                daily_data["trends"].append(trend_doc)
                daily_ref.update({"trends": daily_data["trends"]})
            else:
                daily_ref.set({
                    "date": today,
                    "trends": [trend_doc],
                    "created_at": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error storing trend {trend_doc['name']}: {str(e)}")

    def _calculate_trend_direction(self, trend_data) -> str:
        """Calculate if trend is increasing, decreasing, or stable."""
        try:
            if len(trend_data) < 2:
                return "stable"
            
            # Compare first and last values
            first_value = trend_data.iloc[0]
            last_value = trend_data.iloc[-1]
            
            if last_value > first_value + 5:
                return "increasing"
            elif last_value < first_value - 5:
                return "decreasing"
            else:
                return "stable"
        except:
            return "stable"

    def _format_display_name(self, trend_name: str) -> str:
        """Format trend name for display."""
        # Convert "y2k fashion" to "Y2K Fashion"
        words = trend_name.split()
        formatted_words = []
        
        for word in words:
            if word.lower() == "y2k":
                formatted_words.append("Y2K")
            elif word.lower() in ["fashion", "style", "aesthetic"]:
                formatted_words.append(word.title())
            else:
                formatted_words.append(word.title())
        
        return " ".join(formatted_words)

    def _categorize_trend(self, trend_name: str) -> str:
        """Categorize trend into main categories."""
        trend_lower = trend_name.lower()
        
        if any(word in trend_lower for word in ["y2k", "vintage", "retro"]):
            return "nostalgic"
        elif any(word in trend_lower for word in ["coastal", "beach", "resort"]):
            return "seasonal"
        elif any(word in trend_lower for word in ["grunge", "goth", "dark"]):
            return "alternative"
        elif any(word in trend_lower for word in ["old money", "preppy", "elegant"]):
            return "sophisticated"
        elif any(word in trend_lower for word in ["tech", "cyber", "futuristic"]):
            return "futuristic"
        elif any(word in trend_lower for word in ["boho", "hippie", "free"]):
            return "bohemian"
        elif any(word in trend_lower for word in ["minimal", "clean", "simple"]):
            return "minimalist"
        elif any(word in trend_lower for word in ["romantic", "feminine", "soft"]):
            return "romantic"
        elif any(word in trend_lower for word in ["academic", "intellectual"]):
            return "intellectual"
        elif any(word in trend_lower for word in ["street", "urban", "casual"]):
            return "urban"
        elif any(word in trend_lower for word in ["cottage", "rural", "nature"]):
            return "nature"
        elif any(word in trend_lower for word in ["kawaii", "cute", "playful"]):
            return "playful"
        else:
            return "general"

    def _generate_trend_description(self, trend_data: Dict[str, Any]) -> str:
        """Generate a description for the trend."""
        name = ((trend_data.get("display_name", trend_data.get("name", "") if trend_data else "") if trend_data else ""))
        category = (trend_data.get("category", "general") if trend_data else "general")
        direction = (trend_data.get("trend_direction", "stable") if trend_data else "stable")
        
        descriptions = {
            "nostalgic": f"Reviving {name} with modern twists",
            "seasonal": f"Perfect {name} for current weather",
            "alternative": f"Edgy {name} for bold fashion statements",
            "sophisticated": f"Elegant {name} for refined style",
            "futuristic": f"Forward-thinking {name} with tech influences",
            "bohemian": f"Free-spirited {name} with artistic flair",
            "minimalist": f"Clean and simple {name} approach",
            "romantic": f"Dreamy and feminine {name} aesthetic",
            "intellectual": f"Thoughtful {name} with academic inspiration",
            "urban": f"Street-ready {name} for city life",
            "nature": f"Earth-inspired {name} with natural elements",
            "playful": f"Fun and whimsical {name} style"
        }
        
        base_desc = (descriptions.get(category, f"Trending {name} style") if descriptions else f"Trending {name} style")
        
        if direction == "increasing":
            return f"{base_desc} (gaining popularity)"
        elif direction == "decreasing":
            return f"{base_desc} (declining trend)"
        else:
            return base_desc

    def _get_key_items_for_trend(self, trend_data: Dict[str, Any]) -> List[str]:
        """Get key items for a trend."""
        name = (trend_data.get("name", "") if trend_data else "").lower()
        
        # Define key items for different trends
        key_items_map = {
            "y2k fashion": ["Low-rise jeans", "Crop tops", "Platform shoes", "Micro bags"],
            "coastal chic": ["Linen dresses", "Straw hats", "Boat shoes", "Light cardigans"],
            "grunge aesthetic": ["Oversized flannels", "Distressed jeans", "Combat boots", "Band tees"],
            "old money style": ["Blazers", "Polo shirts", "Khaki pants", "Loafers"],
            "techwear": ["Cargo pants", "Technical jackets", "Hiking boots", "Utility vests"],
            "boho fashion": ["Maxi dresses", "Fringe jackets", "Ankle boots", "Wide-brim hats"],
            "minimalist fashion": ["Basic tees", "Straight-leg jeans", "Simple dresses", "Clean sneakers"],
            "romantic core": ["Floral dresses", "Lace tops", "Pastel colors", "Delicate jewelry"],
            "dark academia": ["Tweed blazers", "Pleated skirts", "Oxford shoes", "Turtlenecks"],
            "streetwear": ["Hoodies", "Joggers", "Sneakers", "Graphic tees"],
            "cottagecore": ["Puff-sleeve dresses", "Aprons", "Mary Jane shoes", "Floral prints"],
            "cyberpunk fashion": ["Neon colors", "Mesh tops", "Platform boots", "Futuristic accessories"],
            "vintage fashion": ["Retro dresses", "High-waisted pants", "Vintage blouses", "Classic accessories"],
            "preppy style": ["Polo shirts", "Khaki pants", "Sweater vests", "Loafers"],
            "goth fashion": ["Black clothing", "Leather jackets", "Combat boots", "Dark makeup"],
            "kawaii fashion": ["Pastel colors", "Cute accessories", "Frilly dresses", "Character prints"]
        }
        
        return (key_items_map.get(name, ["Stylish pieces", "Trending items", "Fashion essentials"]) if key_items_map else "Fashion essentials"])

    def _get_colors_for_trend(self, trend_data: Dict[str, Any]) -> List[str]:
        """Get colors for a trend."""
        name = (trend_data.get("name", "") if trend_data else "").lower()
        
        # Define colors for different trends
        colors_map = {
            "y2k fashion": ["Pink", "Purple", "Blue", "Silver"],
            "coastal chic": ["Beige", "White", "Navy", "Sage"],
            "grunge aesthetic": ["Black", "Gray", "Brown", "Olive"],
            "old money style": ["Navy", "Beige", "White", "Camel"],
            "techwear": ["Black", "Gray", "Olive", "Orange"],
            "boho fashion": ["Brown", "Orange", "Green", "Purple"],
            "minimalist fashion": ["White", "Black", "Gray", "Beige"],
            "romantic core": ["Pink", "Lavender", "Peach", "Mint"],
            "dark academia": ["Brown", "Burgundy", "Navy", "Olive"],
            "streetwear": ["Black", "White", "Gray", "Bright colors"],
            "cottagecore": ["Pastels", "White", "Pink", "Mint"],
            "cyberpunk fashion": ["Neon colors", "Black", "Purple", "Pink"],
            "vintage fashion": ["Muted tones", "Brown", "Beige", "Pastels"],
            "preppy style": ["Navy", "Red", "White", "Khaki"],
            "goth fashion": ["Black", "Purple", "Red", "Gray"],
            "kawaii fashion": ["Pastels", "Pink", "Blue", "Yellow"]
        }
        
        return (colors_map.get(name, ["Versatile colors", "Trending hues", "Classic tones"]) if colors_map else "Classic tones"]) 