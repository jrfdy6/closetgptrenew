from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
from ..services.outfit_service import OutfitService
from ..auth.auth_service import get_current_user, get_current_user_optional
from ..custom_types.profile import UserProfile
from ..models.analytics_event import AnalyticsEvent
from ..services.analytics_service import log_analytics_event
from ..config.firebase import db
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from ..services.analytics_service import (
    log_analytics_event,
    log_item_interaction,
    log_outfit_generation,
    log_outfit_feedback,
    get_user_favorites,
    get_favorite_by_type
)
from ..custom_types.profile import UserProfile
from ..auth.auth_service import get_current_user

router = APIRouter()

outfit_service = OutfitService()

@router.get("/outfit-analytics")
async def get_outfit_analytics(
    start_date: Optional[int] = Query(None, description="Start timestamp"),
    end_date: Optional[int] = Query(None, description="End timestamp"),
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive analytics about outfit generation performance.
    
    Returns:
    - Success/failure rates
    - Validation error patterns
    - User feedback statistics
    - Performance metrics
    - Base item usage patterns
    """
    try:
        # If no dates provided, default to last 30 days
        if not start_date:
            start_date = int((datetime.now() - timedelta(days=30)).timestamp())
        if not end_date:
            end_date = int(datetime.now().timestamp())
        
        analytics = await outfit_service.get_outfit_analytics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": analytics,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": (end_date - start_date) / (24 * 60 * 60)
            }
        }
        
    except Exception as e:
        print(f"Error getting outfit analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics"
        )

@router.get("/outfit-analytics/validation-errors")
async def get_validation_error_analytics(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed analysis of validation errors to identify common issues.
    """
    try:
        # Get all outfits for the user
        analytics = await outfit_service.get_outfit_analytics(user_id=current_user.id)
        
        validation_errors = (analytics.get("validation_errors", {}) if analytics else {})
        
        # Categorize errors
        error_categories = {
            "layering": [],
            "style": [],
            "weather": [],
            "occasion": [],
            "pairability": [],
            "other": []
        }
        
        for error, count in validation_errors.items():
            error_lower = error.lower()
            if "layer" in error_lower:
                error_categories["layering"].append({"error": error, "count": count})
            elif "style" in error_lower:
                error_categories["style"].append({"error": error, "count": count})
            elif "weather" in error_lower or "temperature" in error_lower:
                error_categories["weather"].append({"error": error, "count": count})
            elif "occasion" in error_lower:
                error_categories["occasion"].append({"error": error, "count": count})
            elif "pairability" in error_lower:
                error_categories["pairability"].append({"error": error, "count": count})
            else:
                error_categories["other"].append({"error": error, "count": count})
        
        return {
            "success": True,
            "data": {
                "total_errors": sum(validation_errors.values()),
                "error_categories": error_categories,
                "most_common_errors": sorted(validation_errors.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        }
        
    except Exception as e:
        print(f"Error getting validation error analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve validation error analytics"
        )

@router.get("/outfit-analytics/feedback")
async def get_feedback_analytics(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get analytics about user feedback patterns.
    """
    try:
        analytics = await outfit_service.get_outfit_analytics(user_id=current_user.id)
        
        feedback_stats = (analytics.get("feedback_stats", {}) if analytics else {})
        
        # Calculate feedback insights
        total_feedback = (feedback_stats.get("total_feedback", 0) if feedback_stats else 0)
        positive_feedback = (feedback_stats.get("positive_feedback", 0) if feedback_stats else 0)
        average_rating = (feedback_stats.get("average_rating", 0) if feedback_stats else 0)
        
        feedback_insights = {
            "total_feedback": total_feedback,
            "positive_feedback_rate": (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0,
            "average_rating": average_rating,
            "rating_distribution": {
                "excellent": 0,  # 4.5-5.0
                "good": 0,       # 3.5-4.4
                "average": 0,    # 2.5-3.4
                "poor": 0,       # 1.5-2.4
                "very_poor": 0   # 1.0-1.4
            }
        }
        
        return {
            "success": True,
            "data": feedback_insights
        }
        
    except Exception as e:
        print(f"Error getting feedback analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve feedback analytics"
        )

@router.get("/outfit-analytics/performance")
async def get_performance_metrics(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance metrics for outfit generation.
    """
    try:
        analytics = await outfit_service.get_outfit_analytics(user_id=current_user.id)
        
        total_outfits = (analytics.get("total_outfits", 0) if analytics else 0)
        successful_outfits = (analytics.get("successful_outfits", 0) if analytics else 0)
        failed_outfits = (analytics.get("failed_outfits", 0) if analytics else 0)
        base_item_usage_rate = (analytics.get("base_item_usage_rate", 0) if analytics else 0)
        
        performance_metrics = {
            "total_outfits_generated": total_outfits,
            "success_rate": (analytics.get("success_rate", 0) if analytics else 0),
            "failure_rate": (failed_outfits / total_outfits * 100) if total_outfits > 0 else 0,
            "base_item_usage_rate": base_item_usage_rate,
            "efficiency_score": (successful_outfits / total_outfits) if total_outfits > 0 else 0,
            "recommendations": []
        }
        
        # Generate recommendations based on metrics
        if performance_metrics["success_rate"] < 70:
            performance_metrics["recommendations"].append(
                "Consider adding more wardrobe items to improve outfit generation success rate"
            )
        
        if base_item_usage_rate < 20:
            performance_metrics["recommendations"].append(
                "Try using base items more often for better outfit customization"
            )
        
        if performance_metrics["failure_rate"] > 30:
            performance_metrics["recommendations"].append(
                "High failure rate detected. Check wardrobe diversity and item metadata quality"
            )
        
        return {
            "success": True,
            "data": performance_metrics
        }
        
    except Exception as e:
        print(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve performance metrics"
        ) 

@router.post("/analytics/event", status_code=201)
def create_analytics_event(event: AnalyticsEvent):
    try:
        event_id = log_analytics_event(event)
        return {"success": True, "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/diagnostics/outfit-traces")
async def get_outfit_generation_traces(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    outfit_id: Optional[str] = Query(None, description="Filter by specific outfit ID"),
    start_date: Optional[int] = Query(None, description="Start timestamp"),
    end_date: Optional[int] = Query(None, description="End timestamp"),
    generation_method: Optional[str] = Query(None, description="Filter by generation method"),
    success_only: Optional[bool] = Query(False, description="Show only successful generations"),
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get comprehensive outfit generation traces for diagnostics and analysis.
    
    This endpoint provides detailed pipeline traces, validation errors, fix attempts,
    and system context for outfit generation diagnostics.
    """
    try:
        # Get traces from the generation_traces collection
        traces_ref = db.collection('generation_traces')
        query = traces_ref
        
        # Apply filters
        if user_id:
            query = query.where('trace_data.user_id', '==', user_id)
        if outfit_id:
            query = query.where('trace_data.outfit_id', '==', outfit_id)
        if start_date:
            query = query.where('created_at', '>=', start_date)
        if end_date:
            query = query.where('created_at', '<=', end_date)
        
        # Get traces
        traces = []
        docs = query.stream()
        
        for doc in docs:
            trace_data = doc.to_dict()
            trace_data['trace_id'] = doc.id
            
            # Apply additional filters
            if generation_method and (trace_data.get('trace_data', {}) if trace_data else {}).get('generation_method') != generation_method:
                continue
                
            if success_only:
                outfit_success = (trace_data.get('trace_data', {}) if trace_data else {}).get('was_successful', True)
                if not outfit_success:
                    continue
            
            traces.append(trace_data)
        
        # Sort by creation time (newest first)
        traces.sort(key=lambda x: (x.get('created_at', 0) if x else 0), reverse=True)
        
        return {
            "success": True,
            "traces": traces,
            "count": len(traces),
            "filters_applied": {
                "user_id": user_id,
                "outfit_id": outfit_id,
                "start_date": start_date,
                "end_date": end_date,
                "generation_method": generation_method,
                "success_only": success_only
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving traces: {str(e)}")

@router.get("/diagnostics/outfit-traces/{outfit_id}")
async def get_outfit_trace_detail(
    outfit_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get detailed trace information for a specific outfit generation.
    
    This provides the complete pipeline trace, validation details, wardrobe snapshot,
    system context, and user session context for a single outfit generation.
    """
    try:
        # First try to get from the outfit document
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        
        # Extract trace information
        trace_info = {
            "outfit_id": outfit_id,
            "generation_trace": (outfit_data.get('generation_trace', []) if outfit_data else []),
            "validation_details": (outfit_data.get('validation_details', {}) if outfit_data else {}),
            "wardrobe_snapshot": (outfit_data.get('wardrobe_snapshot', {}) if outfit_data else {}),
            "system_context": (outfit_data.get('system_context', {}) if outfit_data else {}),
            "user_session_context": (outfit_data.get('user_session_context', {}) if outfit_data else {}),
            "generation_method": (outfit_data.get('generation_method', 'unknown') if outfit_data else 'unknown'),
            "was_successful": (outfit_data.get('wasSuccessful', False) if outfit_data else False),
            "validation_errors": (outfit_data.get('validationErrors', []) if outfit_data else []),
            "created_at": (outfit_data.get('createdAt', 0) if outfit_data else 0),
            "outfit_summary": {
                "name": (outfit_data.get('name', '') if outfit_data else ''),
                "occasion": (outfit_data.get('occasion', '') if outfit_data else ''),
                "style": (outfit_data.get('style', '') if outfit_data else ''),
                "items_count": len((outfit_data.get('items', []) if outfit_data else [])),
                "color_harmony": (outfit_data.get('colorHarmony', '') if outfit_data else ''),
                "style_notes": (outfit_data.get('styleNotes', '') if outfit_data else '')
            }
        }
        
        return {
            "success": True,
            "trace": trace_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trace: {str(e)}")

@router.get("/diagnostics/analytics")
async def get_diagnostic_analytics(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    days: Optional[int] = Query(7, description="Number of days to analyze"),
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get aggregated analytics from outfit generation traces.
    
    This provides insights into generation success rates, common errors,
    performance metrics, and system health indicators.
    """
    try:
        # Calculate time range
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)
        
        # Get outfits from the specified time range
        outfits_ref = db.collection('outfits')
        query = outfits_ref.where('createdAt', '>=', start_time).where('createdAt', '<=', end_time)
        
        if user_id:
            query = query.where('user_id', '==', user_id)
        
        outfits = []
        docs = query.stream()
        
        for doc in docs:
            outfit_data = doc.to_dict()
            outfit_data['outfit_id'] = doc.id
            outfits.append(outfit_data)
        
        # Calculate analytics
        total_generations = len(outfits)
        successful_generations = sum(1 for o in outfits if o.get('wasSuccessful', False))
        failed_generations = total_generations - successful_generations
        
        # Generation method breakdown
        method_counts = {}
        for outfit in outfits:
            method = (outfit.get('generation_method', 'unknown') if outfit else 'unknown')
            method_counts[method] = (method_counts.get(method, 0) if method_counts else 0) + 1
        
        # Common validation errors
        error_counts = {}
        for outfit in outfits:
            errors = (outfit.get('validationErrors', []) if outfit else [])
            for error in errors:
                # Extract error type from error message
                error_type = error.split(':')[0] if ':' in error else 'unknown'
                error_counts[error_type] = (error_counts.get(error_type, 0) if error_counts else 0) + 1
        
        # Performance metrics
        generation_times = []
        for outfit in outfits:
            trace = (outfit.get('generation_trace', []) if outfit else [])
            if trace:
                # Find the generation completion step
                for step in trace:
                    if step.get('step') == 'generation_completion':
                        duration = step.get('duration', 0)
                        if duration > 0:
                            generation_times.append(duration)
        
        avg_generation_time = sum(generation_times) / len(generation_times) if generation_times else 0
        
        # Wardrobe gap analysis
        wardrobe_gaps = {}
        for outfit in outfits:
            snapshot = (outfit.get('wardrobe_snapshot', {}) if outfit else {})
            gaps = (snapshot.get('gaps', []) if snapshot else [])
            for gap in gaps:
                category = (gap.get('category', 'unknown') if gap else 'unknown')
                severity = (gap.get('severity', 'unknown') if gap else 'unknown')
                if category not in wardrobe_gaps:
                    wardrobe_gaps[category] = {'high': 0, 'medium': 0, 'low': 0}
                wardrobe_gaps[category][severity] = wardrobe_gaps[category].get(severity, 0) + 1
        
        return {
            "success": True,
            "analytics": {
                "time_range": {
                    "start": start_time,
                    "end": end_time,
                    "days": days
                },
                "generation_stats": {
                    "total": total_generations,
                    "successful": successful_generations,
                    "failed": failed_generations,
                    "success_rate": (successful_generations / total_generations * 100) if total_generations > 0 else 0
                },
                "generation_methods": method_counts,
                "common_errors": dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                "performance": {
                    "avg_generation_time": avg_generation_time,
                    "total_generations_timed": len(generation_times)
                },
                "wardrobe_gaps": wardrobe_gaps
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating analytics: {str(e)}")

@router.get("/diagnostics/health")
async def get_system_health(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get system health indicators from recent outfit generations.
    
    This provides insights into system performance, error rates,
    and potential issues that need attention.
    """
    try:
        # Get recent outfits (last 24 hours)
        end_time = int(time.time())
        start_time = end_time - (24 * 60 * 60)
        
        outfits_ref = db.collection('outfits')
        recent_outfits = outfits_ref.where('createdAt', '>=', start_time).stream()
        
        outfits = []
        for doc in recent_outfits:
            outfit_data = doc.to_dict()
            outfit_data['outfit_id'] = doc.id
            outfits.append(outfit_data)
        
        # Calculate health metrics
        total_recent = len(outfits)
        successful_recent = sum(1 for o in outfits if o.get('wasSuccessful', False))
        error_rate = (total_recent - successful_recent) / total_recent * 100 if total_recent > 0 else 0
        
        # Check for common issues
        issues = []
        
        if error_rate > 20:
            issues.append({
                "type": "high_error_rate",
                "severity": "high",
                "message": f"Error rate is {error_rate:.1f}% (above 20% threshold)",
                "value": error_rate
            })
        
        # Check generation times
        slow_generations = 0
        for outfit in outfits:
            trace = (outfit.get('generation_trace', []) if outfit else [])
            for step in trace:
                if step.get('step') == 'generation_completion':
                    duration = step.get('duration', 0)
                    if duration > 30:  # More than 30 seconds
                        slow_generations += 1
                    break
        
        if slow_generations > 0:
            issues.append({
                "type": "slow_generations",
                "severity": "medium",
                "message": f"{slow_generations} generations took longer than 30 seconds",
                "value": slow_generations
            })
        
        # Check for fallback usage
        fallback_usage = sum(1 for o in outfits if o.get('generation_method') in ['fallback', 'final_fallback'])
        if fallback_usage > total_recent * 0.5:
            issues.append({
                "type": "high_fallback_usage",
                "severity": "medium",
                "message": f"Fallback methods used in {fallback_usage}/{total_recent} generations",
                "value": fallback_usage
            })
        
        return {
            "success": True,
            "health": {
                "status": "healthy" if not issues else "needs_attention",
                "last_24_hours": {
                    "total_generations": total_recent,
                    "successful_generations": successful_recent,
                    "error_rate": error_rate
                },
                "issues": issues,
                "timestamp": end_time
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking system health: {str(e)}")

@router.get("/diagnostics/health/public")
async def get_public_system_health():
    """
    Public health check endpoint for diagnostic testing.
    This endpoint doesn't require authentication.
    """
    try:
        # Get basic system info
        import time
        import platform
        import sys
        
        # Get outfit count from Firestore
        outfits_ref = db.collection('outfits')
        outfit_count = len(list(outfits_ref.stream()))
        
        # Get trace count
        traces_ref = db.collection('generation_traces')
        trace_count = len(list(traces_ref.stream()))
        
        return {
            "status": "healthy",
            "timestamp": int(time.time()),
            "system_info": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "uptime": "running"
            },
            "diagnostic_data": {
                "outfits_count": outfit_count,
                "traces_count": trace_count,
                "last_test_outfit_id": "c833709e-c1b6-4618-8c87-0ceede11acf7"
            },
            "message": "Diagnostic system is operational"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": int(time.time())
        }

@router.get("/diagnostics/outfit-traces/public")
async def get_public_outfit_traces():
    """
    Public outfit traces endpoint for diagnostic testing.
    This endpoint doesn't require authentication.
    """
    try:
        import time
        
        # Get the most recent outfit trace
        outfits_ref = db.collection('outfits')
        outfits = list(outfits_ref.order_by('createdAt', direction='DESCENDING').limit(1).stream())
        
        if not outfits:
            return {
                "status": "no_data",
                "message": "No outfit traces found",
                "timestamp": int(time.time())
            }
        
        outfit_data = outfits[0].to_dict()
        outfit_data['outfit_id'] = outfits[0].id
        
        return {
            "status": "success",
            "timestamp": int(time.time()),
            "latest_outfit": {
                "id": outfit_data['outfit_id'],
                "name": (outfit_data.get('name', 'Unknown') if outfit_data else 'Unknown'),
                "generation_method": (outfit_data.get('generation_method', 'unknown') if outfit_data else 'unknown'),
                "was_successful": (outfit_data.get('wasSuccessful', False) if outfit_data else False),
                "items_count": len((outfit_data.get('items', []) if outfit_data else [])),
                "created_at": (outfit_data.get('createdAt', 0) if outfit_data else 0),
                "validation_errors": (outfit_data.get('validationErrors', []) if outfit_data else []),
                "generation_trace": (outfit_data.get('generation_trace', []) if outfit_data else [])
            },
            "message": "Latest outfit trace retrieved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": int(time.time())
        }

@router.get("/test-alive")
async def test_alive():
    return {"status": "alive"} 

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)

@router.post("/outfit-worn")
async def track_outfit_worn(
    data: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Track when an outfit is marked as worn
    """
    try:
        logger.info(f"Tracking outfit worn for user {current_user.id}")
        
        # Extract data from request
        outfit_id = (data.get("outfitId") if data else None)
        date_worn = (data.get("dateWorn") if data else None)
        occasion = (data.get("occasion", "Casual") if data else "Casual")
        mood = (data.get("mood", "Comfortable") if data else "Comfortable")
        weather = (data.get("weather") if data else None)
        
        # Create analytics event
        event_data = {
            "user_id": current_user.id,
            "event_type": "outfit_worn",
            "outfit_id": outfit_id,
            "date_worn": date_worn,
            "occasion": occasion,
            "mood": mood,
            "weather": weather,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "outfit_history_api"
        }
        
        # Log to analytics collection
        log_analytics_event(event_data)
        
        logger.info(f"Successfully tracked outfit worn event for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Outfit worn event tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Error tracking outfit worn event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track outfit worn event")

@router.post("/outfit-history-update")
async def track_outfit_history_update(
    data: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Track outfit history updates
    """
    try:
        logger.info(f"Tracking outfit history update for user {current_user.id}")
        
        # Extract data from request
        entry_id = (data.get("entryId") if data else None)
        outfit_id = (data.get("outfitId") if data else None)
        updates = (data.get("updates", {}) if data else {})
        
        # Create analytics event
        event_data = {
            "user_id": current_user.id,
            "event_type": "outfit_history_updated",
            "entry_id": entry_id,
            "outfit_id": outfit_id,
            "updates": updates,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "outfit_history_api"
        }
        
        # Log to analytics collection
        log_analytics_event(event_data)
        
        logger.info(f"Successfully tracked outfit history update for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Outfit history update tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Error tracking outfit history update: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track outfit history update")

@router.post("/outfit-history-delete")
async def track_outfit_history_delete(
    data: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Track outfit history deletions
    """
    try:
        logger.info(f"Tracking outfit history deletion for user {current_user.id}")
        
        # Extract data from request
        entry_id = (data.get("entryId") if data else None)
        outfit_id = (data.get("outfitId") if data else None)
        outfit_name = (data.get("outfitName") if data else None)
        date_worn = (data.get("dateWorn") if data else None)
        occasion = (data.get("occasion") if data else None)
        mood = (data.get("mood") if data else None)
        
        # Create analytics event
        event_data = {
            "user_id": current_user.id,
            "event_type": "outfit_history_deleted",
            "entry_id": entry_id,
            "outfit_id": outfit_id,
            "outfit_name": outfit_name,
            "date_worn": date_worn,
            "occasion": occasion,
            "mood": mood,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "outfit_history_api"
        }
        
        # Log to analytics collection
        log_analytics_event(event_data)
        
        logger.info(f"Successfully tracked outfit history deletion for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Outfit history deletion tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Error tracking outfit history deletion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track outfit history deletion")

@router.get("/outfit-history-summary/{user_id}")
async def get_outfit_history_summary(
    user_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get outfit history analytics summary for a user
    """
    try:
        # Verify user can access this data
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this data")
        
        logger.info(f"Getting outfit history summary for user {user_id}")
        
        # Get analytics summary
        # summary = await analytics_service.get_outfit_history_summary(user_id)
        summary = {"message": "Not implemented in function-based analytics service"}
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting outfit history summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get outfit history summary")

@router.get("/outfit-wear-patterns/{user_id}")
async def get_outfit_wear_patterns(
    user_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get outfit wear patterns and insights
    """
    try:
        # Verify user can access this data
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this data")
        
        logger.info(f"Getting outfit wear patterns for user {user_id}")
        
        # Get wear patterns
        # patterns = await analytics_service.get_outfit_wear_patterns(user_id)
        patterns = {"message": "Not implemented in function-based analytics service"}
        
        return {
            "success": True,
            "patterns": patterns
        }
        
    except Exception as e:
        logger.error(f"Error getting outfit wear patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get outfit wear patterns") 