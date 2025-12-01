"""
Style Analytics Routes
Handles style report generation, trend analysis, and seasonal comparisons
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
import logging

from ..auth.auth_service import get_current_user_id
from ..config.firebase import db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["style-analytics"])


@router.get("/style-report")
async def get_style_report(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    year: Optional[int] = Query(None, description="Year"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate monthly style report for a user.
    
    Returns:
    - Total outfits created
    - Style breakdown (casual, business, formal, athletic)
    - Color palette analysis
    - Top worn items
    - Trend indicators
    """
    try:
        # Determine month/year to analyze
        if month:
            year_str, month_str = month.split("-")
            target_year = int(year_str)
            target_month = int(month_str)
        elif year:
            now = datetime.now(timezone.utc)
            target_year = year
            target_month = now.month
        else:
            now = datetime.now(timezone.utc)
            target_year = now.year
            target_month = now.month
        
        # Calculate month start/end timestamps
        month_start = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
        if target_month == 12:
            month_end = datetime(target_year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            month_end = datetime(target_year, target_month + 1, 1, tzinfo=timezone.utc)
        
        month_start_ts = int(month_start.timestamp())
        month_end_ts = int(month_end.timestamp())
        
        logger.info(f"Generating style report for user {user_id}, month {target_year}-{target_month:02d}")
        
        # Calculate previous month for trend comparison
        if target_month == 1:
            prev_month_start = datetime(target_year - 1, 12, 1, tzinfo=timezone.utc)
            prev_month_end = datetime(target_year, 1, 1, tzinfo=timezone.utc)
        else:
            prev_month_start = datetime(target_year, target_month - 1, 1, tzinfo=timezone.utc)
            prev_month_end = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
        
        prev_month_start_ts = int(prev_month_start.timestamp())
        # Use month_start_ts as the end for previous month (it's the same as prev_month_end_ts)
        
        # OPTIMIZATION: Fetch all outfits once covering both current and previous month, then filter in memory
        # Time range: from previous month start to current month end
        earliest_timestamp = prev_month_start_ts
        
        all_outfits = []
        seen_ids = set()
        
        # Helper function to parse timestamp
        def parse_timestamp(data, field_names):
            for field in field_names:
                value = data.get(field)
                if value is None:
                    continue
                if isinstance(value, int):
                    return value
                elif isinstance(value, str):
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        return int(dt.timestamp())
                    except:
                        continue
            return None
        
        # 1. outfit_history - with time range check
        outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        count = 0
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            timestamp = parse_timestamp(
                outfit_data,
                ['createdAt', 'created_at', 'date_worn', 'dateWorn']
            )
            if timestamp and timestamp >= earliest_timestamp:
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
                    count += 1
            if count > 5000:
                break
        
        # 2. outfits collection (user_id) - limit query
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id).limit(2000)
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            timestamp = parse_timestamp(
                outfit_data,
                ['createdAt', 'created_at', 'lastWorn', 'last_worn']
            )
            if timestamp and timestamp >= earliest_timestamp:
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
        
        # 3. outfits collection (userId) - limit query
        outfits_ref = db.collection('outfits').where('userId', '==', user_id).limit(2000)
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            timestamp = parse_timestamp(
                outfit_data,
                ['createdAt', 'created_at', 'lastWorn', 'last_worn']
            )
            if timestamp and timestamp >= earliest_timestamp:
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
        
        # 4. user subcollection - limit query
        try:
            user_outfits_ref = db.collection('users').document(user_id).collection('outfits').limit(2000)
            for doc in user_outfits_ref.stream():
                outfit_data = doc.to_dict()
                timestamp = parse_timestamp(
                    outfit_data,
                    ['createdAt', 'created_at', 'lastWorn', 'last_worn']
                )
                if timestamp and timestamp >= earliest_timestamp:
                    outfit_id = outfit_data.get('id') or doc.id
                    if outfit_id not in seen_ids:
                        all_outfits.append(outfit_data)
                        seen_ids.add(outfit_id)
        except Exception as e:
            logger.warning(f"Could not check user subcollection: {e}")
        
        # 5. daily_outfit_suggestions - limit query
        try:
            suggestions_ref = db.collection('daily_outfit_suggestions').where('user_id', '==', user_id).limit(1000)
            for doc in suggestions_ref.stream():
                suggestion_data = doc.to_dict()
                timestamp = parse_timestamp(
                    suggestion_data,
                    ['createdAt', 'created_at', 'date', 'suggestion_date']
                )
                if timestamp and timestamp >= earliest_timestamp:
                    if 'outfit' in suggestion_data:
                        outfit_data = suggestion_data.get('outfit', {})
                        outfit_id = outfit_data.get('id') or doc.id
                        if outfit_id not in seen_ids:
                            outfit_data['id'] = outfit_id
                            outfit_data['user_id'] = user_id
                            all_outfits.append(outfit_data)
                            seen_ids.add(outfit_id)
        except Exception as e:
            logger.warning(f"Could not check daily suggestions: {e}")
        
        logger.info(f"Fetched {len(all_outfits)} outfits in time range, now filtering by month")
        
        # Filter outfits for current month
        outfits = []
        for outfit_data in all_outfits:
            timestamp = parse_timestamp(
                outfit_data,
                ['createdAt', 'created_at', 'date_worn', 'dateWorn', 'lastWorn', 'last_worn', 'date', 'suggestion_date']
            )
            if timestamp and month_start_ts <= timestamp < month_end_ts:
                outfits.append(outfit_data)
        
        # Filter outfits for previous month
        prev_outfits = []
        for outfit_data in all_outfits:
            timestamp = parse_timestamp(
                outfit_data,
                ['createdAt', 'created_at', 'date_worn', 'dateWorn', 'lastWorn', 'last_worn', 'date', 'suggestion_date']
            )
            if timestamp and prev_month_start_ts <= timestamp < month_start_ts:
                prev_outfits.append(outfit_data)
        
        logger.info(f"Total unique outfits found for the month: {len(outfits)}, previous month: {len(prev_outfits)}")
        
        # If still no outfits, analyze wardrobe and profile data
        use_wardrobe_fallback = len(outfits) == 0
        
        # Analyze style breakdown
        style_counter = Counter()
        color_counter = Counter()
        item_wear_count = defaultdict(int)
        item_details = {}
        
        for outfit in outfits:
            # Count style/occasion
            occasion = outfit.get('occasion', 'casual').lower()
            style = outfit.get('style', 'casual').lower()
            
            # Map to standard categories
            if occasion in ['business', 'business casual', 'work', 'professional']:
                style_counter['business'] += 1
            elif occasion in ['formal', 'black tie', 'wedding']:
                style_counter['formal'] += 1
            elif occasion in ['athletic', 'sport', 'gym', 'workout']:
                style_counter['athletic'] += 1
            else:
                style_counter['casual'] += 1
            
            # Count colors from items
            items = outfit.get('items', [])
            for item in items:
                if isinstance(item, dict):
                    color = item.get('color', '').strip()
                    if color:
                        color_counter[color] += 1
                    
                    item_id = item.get('id') or item.get('itemId')
                    item_name = item.get('name', 'Unknown')
                    if item_id:
                        item_wear_count[item_id] += 1
                        if item_id not in item_details:
                            item_details[item_id] = {
                                'id': item_id,
                                'name': item_name,
                                'imageUrl': item.get('imageUrl') or item.get('image_url')
                            }
        
        # Get top items
        top_items = sorted(
            [
                {
                    **item_details[item_id],
                    'wearCount': count
                }
                for item_id, count in item_wear_count.items()
            ],
            key=lambda x: x['wearCount'],
            reverse=True
        )[:5]
        
        # Get top colors
        total_color_uses = sum(color_counter.values())
        top_colors = [
            {
                'color': color,
                'count': count,
                'percentage': round((count / total_color_uses) * 100, 1) if total_color_uses > 0 else 0
            }
            for color, count in color_counter.most_common(5)
        ]
        
        # Calculate trends (compare with previous month)
        trends = {
            'increasing': [],
            'decreasing': [],
            'stable': []
        }
        
        # Get previous month data for comparison
        if target_month == 1:
            prev_month_start = datetime(target_year - 1, 12, 1, tzinfo=timezone.utc)
            prev_month_end = datetime(target_year, 1, 1, tzinfo=timezone.utc)
        else:
            prev_month_start = datetime(target_year, target_month - 1, 1, tzinfo=timezone.utc)
            prev_month_end = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
        
        prev_month_start_ts = int(prev_month_start.timestamp())
        
        # Previous month outfits are already filtered above from all_outfits
        prev_style_counter = Counter()
        for outfit in prev_outfits:
            occasion = outfit.get('occasion', 'casual').lower()
            if occasion in ['business', 'business casual', 'work', 'professional']:
                prev_style_counter['business'] += 1
            elif occasion in ['formal', 'black tie', 'wedding']:
                prev_style_counter['formal'] += 1
            elif occasion in ['athletic', 'sport', 'gym', 'workout']:
                prev_style_counter['athletic'] += 1
            else:
                prev_style_counter['casual'] += 1
        
            # Compare trends
        for style in ['casual', 'business', 'formal', 'athletic']:
            current = style_counter[style]
            previous = prev_style_counter[style]
            
            if current > previous + 2:
                trends['increasing'].append(style.capitalize())
            elif current < previous - 2:
                trends['decreasing'].append(style.capitalize())
            else:
                trends['stable'].append(style.capitalize())
        
        # If no outfit data, analyze wardrobe and profile for insights
        if use_wardrobe_fallback:
            logger.info("No outfit data found, analyzing wardrobe and profile data")
            
            # Get wardrobe items - limit query for performance
            wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id).limit(1000)
            
            # Analyze wardrobe colors and styles
            for doc in wardrobe_ref.stream():
                item = doc.to_dict()
                item_id = item.get('id') or doc.id
                
                color = item.get('color', '').strip()
                if color:
                    color_counter[color] += 1
                
                # Count by item type/category to infer style
                item_type = item.get('type', '').lower() or item.get('category', '').lower()
                style_tags = item.get('style', []) or item.get('styleTags', []) or []
                occasion_tags = item.get('occasion', []) or item.get('occasionTags', []) or []
                
                # Infer style from item characteristics
                if any(tag in ['formal', 'business', 'professional'] for tag in style_tags + occasion_tags):
                    style_counter['business'] += 1
                elif any(tag in ['athletic', 'sport', 'gym'] for tag in style_tags + occasion_tags):
                    style_counter['athletic'] += 1
                elif any(tag in ['formal', 'black tie', 'wedding'] for tag in style_tags + occasion_tags):
                    style_counter['formal'] += 1
                else:
                    style_counter['casual'] += 1
                
                # Track item usage
                wear_count = item.get('wearCount', 0) or item.get('wear_count', 0)
                if item_id and wear_count > 0:
                    item_wear_count[item_id] = wear_count
                    if item_id not in item_details:
                        item_details[item_id] = {
                            'id': item_id,
                            'name': item.get('name', 'Unknown'),
                            'imageUrl': item.get('imageUrl') or item.get('image_url')
                        }
            
            # Get user profile for style preferences
            try:
                user_ref = db.collection('users').document(user_id)
                user_doc = user_ref.get()
                if user_doc.exists:
                    user_data = user_doc.to_dict() or {}
                    profile = user_data.get('profile', {}) or user_data.get('styleProfile', {})
                    
                    # Use profile style preferences
                    style_prefs = profile.get('style', []) or profile.get('stylePreferences', []) or []
                    for pref in style_prefs:
                        pref_lower = pref.lower()
                        if 'business' in pref_lower or 'professional' in pref_lower:
                            style_counter['business'] += 2  # Weight profile preferences higher
                        elif 'formal' in pref_lower:
                            style_counter['formal'] += 2
                        elif 'athletic' in pref_lower or 'sport' in pref_lower:
                            style_counter['athletic'] += 2
                        else:
                            style_counter['casual'] += 2
                    
                    # Use profile color preferences
                    color_palette = profile.get('colorPalette', {}) or {}
                    for color_list in [color_palette.get('primary', []), color_palette.get('secondary', [])]:
                        for color in color_list:
                            if color:
                                color_counter[color] += 2  # Weight profile colors higher
            except Exception as e:
                logger.warning(f"Could not fetch user profile: {e}")
        
        # Build response
        month_name = month_start.strftime('%B')
        
        return {
            'month': month_name,
            'year': target_year,
            'totalOutfits': len(outfits),
            'styleBreakdown': {
                'casual': style_counter['casual'],
                'business': style_counter['business'],
                'formal': style_counter['formal'],
                'athletic': style_counter['athletic']
            },
            'colorPalette': top_colors,
            'topItems': top_items,
            'trends': trends
        }
        
    except Exception as e:
        logger.error(f"Error generating style report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate style report: {str(e)}")


@router.get("/style-trends")
async def get_style_trends(
    months: int = Query(6, description="Number of months to analyze"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get style trends over multiple months.
    
    Returns timeline data for trend visualization.
    """
    try:
        now = datetime.now(timezone.utc)
        trend_data = []
        
        # Helper function to parse timestamp
        def parse_timestamp_trends(data, field_names):
            for field in field_names:
                value = data.get(field)
                if value is None:
                    continue
                if isinstance(value, int):
                    return value
                elif isinstance(value, str):
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        return int(dt.timestamp())
                    except:
                        continue
            return None
        
        # OPTIMIZATION: Only fetch outfits from the last N months (where N = months parameter + 1 for safety)
        # Calculate the earliest date we need
        earliest_date = now - timedelta(days=30 * (months + 1))
        earliest_timestamp = int(earliest_date.timestamp())
        
        logger.info(f"Fetching outfits for user {user_id} from last {months} months (since {earliest_date.date()})")
        all_outfits = []
        seen_ids = set()
        
        # Helper to check if outfit is in our time range
        def is_in_time_range(outfit_data, field_names):
            timestamp = parse_timestamp_trends(outfit_data, field_names)
            return timestamp and timestamp >= earliest_timestamp
        
        # 1. outfit_history - only fetch recent ones
        outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        count = 0
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            # Quick check: if createdAt/date_worn exists and is too old, skip
            if is_in_time_range(outfit_data, ['createdAt', 'created_at', 'date_worn', 'dateWorn']):
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
                    count += 1
            # Limit to prevent infinite loops - if we've checked 5000 and found enough, stop
            if count > 5000:
                break
        
        # 2. outfits collection (user_id) - limit query
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id).limit(2000)
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            if is_in_time_range(outfit_data, ['createdAt', 'created_at', 'lastWorn', 'last_worn']):
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
        
        # 3. outfits collection (userId) - limit query
        outfits_ref = db.collection('outfits').where('userId', '==', user_id).limit(2000)
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            if is_in_time_range(outfit_data, ['createdAt', 'created_at', 'lastWorn', 'last_worn']):
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
        
        # 4. user subcollection - limit query
        try:
            user_outfits_ref = db.collection('users').document(user_id).collection('outfits').limit(2000)
            for doc in user_outfits_ref.stream():
                outfit_data = doc.to_dict()
                if is_in_time_range(outfit_data, ['createdAt', 'created_at', 'lastWorn', 'last_worn']):
                    outfit_id = outfit_data.get('id') or doc.id
                    if outfit_id not in seen_ids:
                        all_outfits.append(outfit_data)
                        seen_ids.add(outfit_id)
        except Exception as e:
            logger.warning(f"Could not fetch user subcollection: {e}")
        
        logger.info(f"Fetched {len(all_outfits)} outfits in time range, now filtering by month")
        
        # Get wardrobe data once (for fallback) - limit to reasonable amount
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id).limit(1000)
        wardrobe_items = []
        for doc in wardrobe_ref.stream():
            wardrobe_items.append(doc.to_dict())
        
        # Now process each month using the pre-fetched data
        for i in range(months - 1, -1, -1):
            target_date = now - timedelta(days=30 * i)
            month_key = f"{target_date.year}-{target_date.month:02d}"
            
            # Get report for this month
            month_start = datetime(target_date.year, target_date.month, 1, tzinfo=timezone.utc)
            if target_date.month == 12:
                month_end = datetime(target_date.year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                month_end = datetime(target_date.year, target_date.month + 1, 1, tzinfo=timezone.utc)
            
            month_start_ts = int(month_start.timestamp())
            month_end_ts = int(month_end.timestamp())
            
            # Filter outfits for this month from pre-fetched data
            outfits = []
            for outfit_data in all_outfits:
                timestamp = parse_timestamp_trends(
                    outfit_data,
                    ['createdAt', 'created_at', 'date_worn', 'dateWorn', 'lastWorn', 'last_worn']
                )
                if timestamp and month_start_ts <= timestamp < month_end_ts:
                    outfits.append(outfit_data)
            
            # Count styles
            style_counter = Counter()
            for outfit in outfits:
                occasion = outfit.get('occasion', 'casual').lower()
                if occasion in ['business', 'business casual', 'work', 'professional']:
                    style_counter['business'] += 1
                elif occasion in ['formal', 'black tie', 'wedding']:
                    style_counter['formal'] += 1
                elif occasion in ['athletic', 'sport', 'gym', 'workout']:
                    style_counter['athletic'] += 1
                else:
                    style_counter['casual'] += 1
            
            # If no outfits, use wardrobe data for this month (from pre-fetched data)
            if len(outfits) == 0:
                wardrobe_count = len(wardrobe_items)
                for item in wardrobe_items:
                    # Infer style from wardrobe
                    style_tags = item.get('style', []) or item.get('styleTags', []) or []
                    occasion_tags = item.get('occasion', []) or item.get('occasionTags', []) or []
                    
                    if any(tag in ['formal', 'business', 'professional'] for tag in style_tags + occasion_tags):
                        style_counter['business'] += 1
                    elif any(tag in ['athletic', 'sport'] for tag in style_tags + occasion_tags):
                        style_counter['athletic'] += 1
                    elif any(tag in ['formal', 'black tie'] for tag in style_tags + occasion_tags):
                        style_counter['formal'] += 1
                    else:
                        style_counter['casual'] += 1
                
                # Estimate outfits based on wardrobe size (assume 1 outfit per 3 items)
                estimated_outfits = max(1, wardrobe_count // 3)
            else:
                estimated_outfits = len(outfits)
            
            trend_data.append({
                'period': month_start.strftime('%b'),
                'casual': style_counter['casual'],
                'business': style_counter['business'],
                'formal': style_counter['formal'],
                'athletic': style_counter['athletic'],
                'total': estimated_outfits
            })
        
        return {
            'trendData': trend_data,
            'monthsAnalyzed': months
        }
        
    except Exception as e:
        logger.error(f"Error generating style trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate trends: {str(e)}")


@router.get("/seasonal-comparison")
async def get_seasonal_comparison(
    year: Optional[int] = Query(None, description="Year to analyze"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get seasonal style comparison.
    
    Returns style breakdown by season (Winter, Spring, Summer, Fall).
    """
    try:
        # Use current year if not specified
        now = datetime.now(timezone.utc)
        target_year = year or now.year
        
        # Calculate time range we need (from earliest season to latest)
        earliest_season_start = datetime(target_year, 3, 1, tzinfo=timezone.utc)  # Spring
        earliest_timestamp = int(earliest_season_start.timestamp())
        
        logger.info(f"Fetching outfits for seasonal comparison, year {target_year}")
        
        # OPTIMIZATION: Fetch all outfits once, then filter by season in memory
        all_outfits = []
        seen_ids = set()
        
        def parse_timestamp_seasonal(data, field_names):
            for field in field_names:
                value = data.get(field)
                if value is None:
                    continue
                if isinstance(value, int):
                    return value
                elif isinstance(value, str):
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        return int(dt.timestamp())
                    except:
                        continue
            return None
        
        # 1. outfit_history - with time range check
        outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        count = 0
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            timestamp = parse_timestamp_seasonal(
                outfit_data,
                ['createdAt', 'created_at', 'date_worn', 'dateWorn']
            )
            if timestamp and timestamp >= earliest_timestamp:
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
                    count += 1
            if count > 5000:
                break
        
        # 2. outfits collection (user_id) - limit query
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id).limit(2000)
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            timestamp = parse_timestamp_seasonal(
                outfit_data,
                ['createdAt', 'created_at', 'lastWorn', 'last_worn']
            )
            if timestamp and timestamp >= earliest_timestamp:
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
        
        # 3. outfits collection (userId) - limit query
        outfits_ref = db.collection('outfits').where('userId', '==', user_id).limit(2000)
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            timestamp = parse_timestamp_seasonal(
                outfit_data,
                ['createdAt', 'created_at', 'lastWorn', 'last_worn']
            )
            if timestamp and timestamp >= earliest_timestamp:
                outfit_id = outfit_data.get('id') or doc.id
                if outfit_id not in seen_ids:
                    all_outfits.append(outfit_data)
                    seen_ids.add(outfit_id)
        
        # 4. user subcollection - limit query
        try:
            user_outfits_ref = db.collection('users').document(user_id).collection('outfits').limit(2000)
            for doc in user_outfits_ref.stream():
                outfit_data = doc.to_dict()
                timestamp = parse_timestamp_seasonal(
                    outfit_data,
                    ['createdAt', 'created_at', 'lastWorn', 'last_worn']
                )
                if timestamp and timestamp >= earliest_timestamp:
                    outfit_id = outfit_data.get('id') or doc.id
                    if outfit_id not in seen_ids:
                        all_outfits.append(outfit_data)
                        seen_ids.add(outfit_id)
        except Exception as e:
            logger.warning(f"Could not fetch user subcollection: {e}")
        
        logger.info(f"Fetched {len(all_outfits)} outfits for seasonal comparison")
        
        # Define seasons
        current_month = now.month
        seasons = {
            'Winter': (datetime(target_year, 12, 1, tzinfo=timezone.utc), datetime(target_year + 1, 3, 1, tzinfo=timezone.utc)),
            'Spring': (datetime(target_year, 3, 1, tzinfo=timezone.utc), datetime(target_year, 6, 1, tzinfo=timezone.utc)),
            'Summer': (datetime(target_year, 6, 1, tzinfo=timezone.utc), datetime(target_year, 9, 1, tzinfo=timezone.utc)),
            'Fall': (datetime(target_year, 9, 1, tzinfo=timezone.utc), datetime(target_year, 12, 1, tzinfo=timezone.utc))
        }
        
        if current_month == 12 and target_year == now.year:
            seasons['Winter'] = (datetime(target_year, 12, 1, tzinfo=timezone.utc), datetime(target_year + 1, 3, 1, tzinfo=timezone.utc))
        
        seasonal_data = []
        
        # Now process each season using pre-fetched data
        for season_name, (start_date, end_date) in seasons.items():
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            outfits = []
            color_counter = Counter()
            
            # Filter outfits for this season from pre-fetched data
            for outfit_data in all_outfits:
                timestamp = parse_timestamp_seasonal(
                    outfit_data,
                    ['createdAt', 'created_at', 'date_worn', 'dateWorn', 'lastWorn', 'last_worn']
                )
                if timestamp and start_ts <= timestamp < end_ts:
                    outfits.append(outfit_data)
                    # Count colors
                    for item in outfit_data.get('items', []):
                        if isinstance(item, dict):
                            color = item.get('color', '').strip()
                            if color:
                                color_counter[color] += 1
            
            # Count styles
            style_counter = Counter()
            for outfit in outfits:
                occasion = outfit.get('occasion', 'casual').lower()
                if occasion in ['business', 'business casual', 'work', 'professional']:
                    style_counter['business'] += 1
                elif occasion in ['formal', 'black tie', 'wedding']:
                    style_counter['formal'] += 1
                elif occasion in ['athletic', 'sport', 'gym', 'workout']:
                    style_counter['athletic'] += 1
                else:
                    style_counter['casual'] += 1
            
            # Calculate average outfits per week
            weeks = (end_date - start_date).days / 7
            avg_outfits = len(outfits) / weeks if weeks > 0 else 0
            
            seasonal_data.append({
                'season': season_name,
                'year': target_year,
                'styleBreakdown': {
                    'casual': style_counter['casual'],
                    'business': style_counter['business'],
                    'formal': style_counter['formal'],
                    'athletic': style_counter['athletic']
                },
                'topColors': [color for color, _ in color_counter.most_common(3)],
                'avgOutfitsPerWeek': round(avg_outfits, 1)
            })
        
        return {
            'seasonalData': seasonal_data,
            'year': target_year
        }
        
    except Exception as e:
        logger.error(f"Error generating seasonal comparison: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate seasonal comparison: {str(e)}")

