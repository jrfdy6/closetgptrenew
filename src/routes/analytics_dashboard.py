"""
Analytics Dashboard endpoints for ClosetGPT.
Provides comprehensive analytics data for the dashboard.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

from ..core.logging import get_logger
from ..config.firebase import db
from ..models.analytics_event import AnalyticsEvent
from ..routes.auth import get_current_user_id

router = APIRouter()
logger = get_logger("analytics_dashboard")

@router.get("/dashboard")
async def get_dashboard_data(
    range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get comprehensive dashboard analytics data."""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        if range == "1d":
            start_time = end_time - timedelta(days=1)
        elif range == "7d":
            start_time = end_time - timedelta(days=7)
        elif range == "30d":
            start_time = end_time - timedelta(days=30)
        elif range == "90d":
            start_time = end_time - timedelta(days=90)
        else:
            start_time = end_time - timedelta(days=7)

        # Get analytics events for the time range
        events_ref = db.collection('analytics_events')
        events_query = events_ref.where('timestamp', '>=', start_time.isoformat())\
                                .where('timestamp', '<=', end_time.isoformat())
        
        events_docs = events_query.stream()
        events = [doc.to_dict() for doc in events_docs]

        # Calculate overview metrics
        overview = await calculate_overview_metrics(events, start_time, end_time)
        
        # Calculate event distribution
        event_distribution = calculate_event_distribution(events)
        
        # Calculate user activity over time
        user_activity = calculate_user_activity(events, start_time, end_time)
        
        # Get top events
        top_events = calculate_top_events(events)
        
        # Get error analytics
        errors = calculate_error_analytics(events)
        
        # Get performance metrics
        performance = calculate_performance_metrics(events)

        return {
            "overview": overview,
            "events": event_distribution,
            "user_activity": user_activity,
            "top_events": top_events,
            "errors": errors,
            "performance": performance,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "range": range
            }
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve dashboard data"
        )

async def calculate_overview_metrics(events: List[Dict], start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """Calculate overview metrics."""
    try:
        # Get unique users
        unique_users = set()
        total_outfits = 0
        successful_outfits = 0
        total_api_calls = 0
        successful_api_calls = 0
        total_response_time = 0
        api_call_count = 0

        for event in events:
            user_id = event.get('user_id')
            if user_id:
                unique_users.add(user_id)

            event_type = event.get('event_type', '')
            metadata = event.get('metadata', {})

            if event_type == 'outfit_generated':
                total_outfits += 1
                if metadata.get('confidence_score', 0) > 0.5:
                    successful_outfits += 1

            elif event_type == 'api_call':
                total_api_calls += 1
                status = metadata.get('status', 0)
                if 200 <= status < 300:
                    successful_api_calls += 1
                
                duration = metadata.get('duration', 0)
                if duration:
                    total_response_time += duration
                    api_call_count += 1

        # Get total users from users collection
        users_ref = db.collection('users')
        total_users = len(list(users_ref.stream()))

        # Get active users today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_events = [e for e in events if datetime.fromisoformat(e.get('timestamp', '')) >= today_start]
        active_users_today = len(set(e.get('user_id') for e in today_events if e.get('user_id')))

        return {
            "total_users": total_users,
            "active_users_today": active_users_today,
            "total_outfits_generated": total_outfits,
            "success_rate": round((successful_outfits / total_outfits * 100) if total_outfits > 0 else 0, 1),
            "average_response_time": round(total_response_time / api_call_count if api_call_count > 0 else 0, 1),
            "api_success_rate": round((successful_api_calls / total_api_calls * 100) if total_api_calls > 0 else 0, 1)
        }

    except Exception as e:
        logger.error(f"Error calculating overview metrics: {e}")
        return {
            "total_users": 0,
            "active_users_today": 0,
            "total_outfits_generated": 0,
            "success_rate": 0,
            "average_response_time": 0,
            "api_success_rate": 0
        }

def calculate_event_distribution(events: List[Dict]) -> List[Dict[str, Any]]:
    """Calculate event type distribution."""
    event_counts = {}
    total_events = len(events)

    for event in events:
        event_type = event.get('event_type', 'unknown')
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

    distribution = []
    for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
        distribution.append({
            "event_type": event_type,
            "count": count,
            "percentage": round((count / total_events * 100) if total_events > 0 else 0, 1)
        })

    return distribution

def calculate_user_activity(events: List[Dict], start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Calculate user activity over time."""
    activity_by_date = {}
    
    # Initialize all dates in range
    current_date = start_time.date()
    while current_date <= end_time.date():
        activity_by_date[current_date.isoformat()] = {
            "users": set(),
            "outfits": 0,
            "errors": 0
        }
        current_date += timedelta(days=1)

    # Count events by date
    for event in events:
        try:
            event_date = datetime.fromisoformat(event.get('timestamp', '')).date()
            if event_date in activity_by_date:
                user_id = event.get('user_id')
                if user_id:
                    activity_by_date[event_date]["users"].add(user_id)

                event_type = event.get('event_type', '')
                if event_type == 'outfit_generated':
                    activity_by_date[event_date]["outfits"] += 1
                elif 'error' in event_type.lower():
                    activity_by_date[event_date]["errors"] += 1

        except (ValueError, TypeError):
            continue

    # Convert to list format
    activity_list = []
    for date, data in sorted(activity_by_date.items()):
        activity_list.append({
            "date": date,
            "users": len(data["users"]),
            "outfits": data["outfits"],
            "errors": data["errors"]
        })

    return activity_list

def calculate_top_events(events: List[Dict]) -> List[Dict[str, Any]]:
    """Calculate top events with trends."""
    event_counts = {}
    
    # Count events by type
    for event in events:
        event_type = event.get('event_type', 'unknown')
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

    # Get top 10 events
    top_events = []
    for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        # Simple trend calculation (could be enhanced with historical data)
        trend = 'stable'
        if count > 100:
            trend = 'up'
        elif count < 10:
            trend = 'down'

        top_events.append({
            "event_type": event_type,
            "count": count,
            "trend": trend
        })

    return top_events

def calculate_error_analytics(events: List[Dict]) -> List[Dict[str, Any]]:
    """Calculate error analytics."""
    error_counts = {}
    error_last_occurrence = {}

    for event in events:
        event_type = event.get('event_type', '')
        if 'error' in event_type.lower():
            error_counts[event_type] = error_counts.get(event_type, 0) + 1
            
            timestamp = event.get('timestamp', '')
            if timestamp:
                if event_type not in error_last_occurrence or timestamp > error_last_occurrence[event_type]:
                    error_last_occurrence[event_type] = timestamp

    errors = []
    for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
        errors.append({
            "error_type": error_type,
            "count": count,
            "last_occurrence": error_last_occurrence.get(error_type, '')
        })

    return errors

def calculate_performance_metrics(events: List[Dict]) -> List[Dict[str, Any]]:
    """Calculate API performance metrics."""
    endpoint_stats = {}

    for event in events:
        if event.get('event_type') == 'api_call':
            metadata = event.get('metadata', {})
            endpoint = metadata.get('endpoint', 'unknown')
            status = metadata.get('status', 0)
            duration = metadata.get('duration', 0)

            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'total_calls': 0,
                    'successful_calls': 0,
                    'total_duration': 0,
                    'response_times': []
                }

            endpoint_stats[endpoint]['total_calls'] += 1
            if 200 <= status < 300:
                endpoint_stats[endpoint]['successful_calls'] += 1
            
            if duration:
                endpoint_stats[endpoint]['total_duration'] += duration
                endpoint_stats[endpoint]['response_times'].append(duration)

    performance = []
    for endpoint, stats in endpoint_stats.items():
        avg_response_time = round(stats['total_duration'] / len(stats['response_times']) if stats['response_times'] else 0, 1)
        success_rate = round((stats['successful_calls'] / stats['total_calls'] * 100) if stats['total_calls'] > 0 else 0, 1)

        performance.append({
            'endpoint': endpoint,
            'avg_response_time': avg_response_time,
            'success_rate': success_rate,
            'total_calls': stats['total_calls']
        })

    return sorted(performance, key=lambda x: x['total_calls'], reverse=True)

@router.get("/realtime")
async def get_realtime_metrics(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get real-time metrics for the dashboard."""
    try:
        # Get events from the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        events_ref = db.collection('analytics_events')
        events_query = events_ref.where('timestamp', '>=', one_hour_ago.isoformat())
        
        events_docs = events_query.stream()
        events = [doc.to_dict() for doc in events_docs]

        # Calculate real-time metrics
        active_users = len(set(e.get('user_id') for e in events if e.get('user_id')))
        total_events = len(events)
        error_count = len([e for e in events if 'error' in e.get('event_type', '').lower()])
        outfit_count = len([e for e in events if e.get('event_type') == 'outfit_generated'])

        return {
            "active_users": active_users,
            "events_per_minute": round(total_events / 60, 1),
            "error_rate": round((error_count / total_events * 100) if total_events > 0 else 0, 1),
            "outfits_generated": outfit_count,
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get realtime metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve realtime metrics"
        ) 