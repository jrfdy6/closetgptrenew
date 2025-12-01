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
        
        # Fetch outfit history for the month
        outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        outfits = []
        
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            created_at = outfit_data.get('createdAt') or outfit_data.get('created_at')
            
            # Handle both timestamp formats
            if isinstance(created_at, int):
                timestamp = created_at
            elif isinstance(created_at, str):
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    timestamp = int(dt.timestamp())
                except:
                    continue
            else:
                continue
            
            # Filter by month
            if month_start_ts <= timestamp < month_end_ts:
                outfits.append(outfit_data)
        
        logger.info(f"Found {len(outfits)} outfits for the month")
        
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
        prev_month_end_ts = int(prev_month_end.timestamp())
        
        prev_outfits = []
        for doc in outfits_ref.stream():
            outfit_data = doc.to_dict()
            created_at = outfit_data.get('createdAt') or outfit_data.get('created_at')
            
            if isinstance(created_at, int):
                timestamp = created_at
            elif isinstance(created_at, str):
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    timestamp = int(dt.timestamp())
                except:
                    continue
            else:
                continue
            
            if prev_month_start_ts <= timestamp < prev_month_end_ts:
                prev_outfits.append(outfit_data)
        
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
            
            # Fetch outfits for this month
            outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
            outfits = []
            
            for doc in outfits_ref.stream():
                outfit_data = doc.to_dict()
                created_at = outfit_data.get('createdAt') or outfit_data.get('created_at')
                
                if isinstance(created_at, int):
                    timestamp = created_at
                elif isinstance(created_at, str):
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        timestamp = int(dt.timestamp())
                    except:
                        continue
                else:
                    continue
                
                if month_start_ts <= timestamp < month_end_ts:
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
            
            trend_data.append({
                'period': month_start.strftime('%b'),
                'casual': style_counter['casual'],
                'business': style_counter['business'],
                'formal': style_counter['formal'],
                'athletic': style_counter['athletic'],
                'total': len(outfits)
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
        target_year = year or datetime.now(timezone.utc).year
        
        seasons = {
            'Winter': (datetime(target_year, 12, 1, tzinfo=timezone.utc), datetime(target_year + 1, 3, 1, tzinfo=timezone.utc)),
            'Spring': (datetime(target_year, 3, 1, tzinfo=timezone.utc), datetime(target_year, 6, 1, tzinfo=timezone.utc)),
            'Summer': (datetime(target_year, 6, 1, tzinfo=timezone.utc), datetime(target_year, 9, 1, tzinfo=timezone.utc)),
            'Fall': (datetime(target_year, 9, 1, tzinfo=timezone.utc), datetime(target_year, 12, 1, tzinfo=timezone.utc))
        }
        
        seasonal_data = []
        outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        
        for season_name, (start_date, end_date) in seasons.items():
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            outfits = []
            color_counter = Counter()
            
            for doc in outfits_ref.stream():
                outfit_data = doc.to_dict()
                created_at = outfit_data.get('createdAt') or outfit_data.get('created_at')
                
                if isinstance(created_at, int):
                    timestamp = created_at
                elif isinstance(created_at, str):
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        timestamp = int(dt.timestamp())
                    except:
                        continue
                else:
                    continue
                
                if start_ts <= timestamp < end_ts:
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

