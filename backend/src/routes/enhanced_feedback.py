from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import firebase_admin
from firebase_admin import firestore, auth
from enum import Enum
import json
import logging
import traceback
import psutil
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enhanced-feedback", tags=["enhanced-feedback"])

# Initialize Firestore
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}")
    db = None

class GenerationMethod(str, Enum):
    AI_PRIMARY = "ai_primary"
    AI_FALLBACK = "ai_fallback"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"
    MANUAL = "manual"

class SystemPerformanceData(BaseModel):
    api_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    model_confidence_score: Optional[float]
    fallback_triggered: bool
    fallback_reason: Optional[str]
    error_count: int
    warnings: List[str]

class WardrobeContextData(BaseModel):
    total_items: int
    available_items: int
    items_by_type: Dict[str, int]
    items_by_color: Dict[str, int]
    items_by_season: Dict[str, int]
    missing_categories: List[str]
    image_quality_scores: Dict[str, float]
    metadata_completeness: Dict[str, float]

class GenerationPipelineData(BaseModel):
    generation_steps: List[Dict[str, Any]]
    applied_rules: List[str]
    filtered_items: List[str]
    included_items: List[str]
    decision_points: List[Dict[str, Any]]
    style_matches: Dict[str, float]
    color_compatibility_scores: Dict[str, float]

class UserContextData(BaseModel):
    session_id: str
    previous_outfits: List[str]
    user_preferences: Dict[str, Any]
    stated_preferences: Dict[str, Any]
    feedback_history: Dict[str, Any]
    generation_frequency: Dict[str, int]

class EnhancedFeedbackRequest(BaseModel):
    outfit_id: str
    feedback_type: str
    user_rating: Optional[int]
    issue_category: Optional[str]
    issue_description: Optional[str]
    
    # Enhanced diagnostic data
    system_performance: SystemPerformanceData
    wardrobe_context: WardrobeContextData
    generation_pipeline: GenerationPipelineData
    user_context: UserContextData
    
    # Additional context
    weather_data: Optional[Dict[str, Any]]
    occasion_context: Optional[Dict[str, Any]]
    style_preferences: Optional[Dict[str, Any]]

class EnhancedFeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: str
    diagnostic_insights: List[str]
    recommended_fixes: List[Dict[str, Any]]

async def get_current_user(request: Request):
    """Extract user from Firebase token"""
    try:
        auth_header = request.headers.get("Authorization") if headers else None)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = auth_header.split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

def analyze_performance_issues(performance_data: SystemPerformanceData) -> List[str]:
    """Analyze system performance and identify issues"""
    insights = []
    
    if performance_data.api_response_time > 10.0:
        insights.append("High API response time detected - consider caching or optimization")
    
    if performance_data.memory_usage_mb > 1000:
        insights.append("High memory usage - potential memory leak or inefficient processing")
    
    if performance_data.cpu_usage_percent > 80:
        insights.append("High CPU usage - consider async processing or load balancing")
    
    if performance_data.fallback_triggered:
        insights.append(f"Fallback method triggered: {performance_data.fallback_reason}")
    
    if performance_data.error_count > 0:
        insights.append(f"Multiple errors during generation: {performance_data.error_count} errors")
    
    return insights

def analyze_wardrobe_issues(wardrobe_data: WardrobeContextData) -> List[str]:
    """Analyze wardrobe context and identify issues"""
    insights = []
    
    if wardrobe_data.total_items < 10:
        insights.append("Limited wardrobe size - consider encouraging more uploads")
    
    if len(wardrobe_data.missing_categories) > 3:
        insights.append(f"Missing key categories: {', '.join(wardrobe_data.missing_categories)}")
    
    low_quality_count = sum(1 for score in wardrobe_data.image_quality_scores.values() if score < 0.7)
    if low_quality_count > 0:
        insights.append(f"Low quality images detected: {low_quality_count} items")
    
    incomplete_metadata = sum(1 for score in wardrobe_data.metadata_completeness.values() if score < 0.8)
    if incomplete_metadata > 0:
        insights.append(f"Incomplete metadata: {incomplete_metadata} items")
    
    return insights

def analyze_generation_issues(pipeline_data: GenerationPipelineData) -> List[str]:
    """Analyze generation pipeline and identify issues"""
    insights = []
    
    if len(pipeline_data.filtered_items) > len(pipeline_data.included_items) * 2:
        insights.append("Over-filtering detected - too many items being excluded")
    
    low_style_matches = sum(1 for score in pipeline_data.style_matches.values() if score < 0.6)
    if low_style_matches > 0:
        insights.append(f"Low style match scores: {low_style_matches} items")
    
    if len(pipeline_data.applied_rules) == 0:
        insights.append("No style rules applied - consider rule-based generation")
    
    return insights

def generate_fix_recommendations(insights: List[str], feedback_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate specific fix recommendations based on insights"""
    recommendations = []
    
    for insight in insights:
        if "High API response time" in insight:
            recommendations.append({
                "category": "performance",
                "priority": "high",
                "title": "Optimize API Response Time",
                "description": "Implement caching, database indexing, or async processing",
                "code_changes": [
                    "Add Redis caching for outfit generation",
                    "Optimize database queries with proper indexing",
                    "Implement async processing for non-critical operations"
                ],
                "estimated_effort": "medium"
            })
        
        elif "Limited wardrobe size" in insight:
            recommendations.append({
                "category": "user_experience",
                "priority": "medium",
                "title": "Encourage Wardrobe Expansion",
                "description": "Implement onboarding flows and incentives for adding more items",
                "code_changes": [
                    "Add wardrobe completion progress indicators",
                    "Implement batch upload features",
                    "Add wardrobe gap analysis and recommendations"
                ],
                "estimated_effort": "low"
            })
        
        elif "Fallback method triggered" in insight:
            recommendations.append({
                "category": "reliability",
                "priority": "high",
                "title": "Improve Primary Generation Method",
                "description": "Analyze why fallback was needed and improve primary method",
                "code_changes": [
                    "Add better error handling in primary generation",
                    "Implement progressive fallback strategies",
                    "Add monitoring for fallback triggers"
                ],
                "estimated_effort": "medium"
            })
        
        elif "Low quality images" in insight:
            recommendations.append({
                "category": "data_quality",
                "priority": "medium",
                "title": "Improve Image Quality Detection",
                "description": "Implement better image quality assessment and user guidance",
                "code_changes": [
                    "Add image quality validation during upload",
                    "Implement image enhancement suggestions",
                    "Add user guidance for better photos"
                ],
                "estimated_effort": "low"
            })
    
    return recommendations

@router.post("/outfit", response_model=EnhancedFeedbackResponse)
async def submit_enhanced_feedback(
    feedback: EnhancedFeedbackRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Submit enhanced feedback with comprehensive diagnostic data
    """
    try:
        user_id = (current_user.get("uid") if current_user else None)
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        # Get the outfit details for context
        outfit_ref = db.collection("outfits").document(feedback.outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        
        # Analyze the diagnostic data
        performance_insights = analyze_performance_issues(feedback.system_performance)
        wardrobe_insights = analyze_wardrobe_issues(feedback.wardrobe_context)
        generation_insights = analyze_generation_issues(feedback.generation_pipeline)
        
        all_insights = performance_insights + wardrobe_insights + generation_insights
        
        # Generate fix recommendations
        recommendations = generate_fix_recommendations(all_insights, feedback.dict())
        
        # Create comprehensive feedback document
        enhanced_feedback_data = {
            "user_id": user_id,
            "outfit_id": feedback.outfit_id,
            "feedback_type": feedback.feedback_type,
            "user_rating": feedback.user_rating,
            "issue_category": feedback.issue_category,
            "issue_description": feedback.issue_description,
            
            # Enhanced diagnostic data
            "system_performance": feedback.system_performance.dict(),
            "wardrobe_context": feedback.wardrobe_context.dict(),
            "generation_pipeline": feedback.generation_pipeline.dict(),
            "user_context": feedback.user_context.dict(),
            
            # Analysis results
            "diagnostic_insights": all_insights,
            "recommended_fixes": recommendations,
            
            # Additional context
            "weather_data": feedback.weather_data,
            "occasion_context": feedback.occasion_context,
            "style_preferences": feedback.style_preferences,
            
            # Metadata
            "timestamp": datetime.utcnow().isoformat(),
            "outfit_context": {
                "occasion": (outfit_data.get("occasion") if outfit_data else None),
                "mood": (outfit_data.get("mood") if outfit_data else None),
                "style": (outfit_data.get("style") if outfit_data else None),
                "generation_method": (outfit_data.get("generation_method", "unknown") if outfit_data else "unknown"),
                "items_count": len((outfit_data.get("items", []) if outfit_data else [])),
                "items_types": [(item.get("type") if item else None) for item in (outfit_data.get("items", []) if outfit_data else [])],
                "created_at": (outfit_data.get("createdAt") if outfit_data else None),
            }
        }
        
        # Store in enhanced feedback collection
        feedback_ref = db.collection("enhanced_outfit_feedback").document()
        feedback_ref.set(enhanced_feedback_data)
        
        # Update outfit with enhanced feedback summary
        outfit_ref.update({
            "enhanced_feedback_summary": firestore.ArrayUnion([{
                "feedback_type": feedback.feedback_type,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "insights_count": len(all_insights),
                "recommendations_count": len(recommendations)
            }])
        })
        
        # Store in analytics collection for data lake
        analytics_data = {
            "event_type": "enhanced_outfit_feedback",
            "event_data": enhanced_feedback_data,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "outfit_id": feedback.outfit_id,
            "diagnostic_insights": all_insights,
            "recommendations": recommendations,
            "metadata": {
                "source": "enhanced_user_feedback",
                "version": "2.0",
                "processed": False
            }
        }
        
        analytics_ref = db.collection("analytics_events").document()
        analytics_ref.set(analytics_data)
        
        logger.info(f"Enhanced feedback submitted successfully: {feedback_ref.id}")
        
        return EnhancedFeedbackResponse(
            success=True,
            message="Enhanced feedback submitted successfully",
            feedback_id=feedback_ref.id,
            diagnostic_insights=all_insights,
            recommended_fixes=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting enhanced feedback: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/diagnostics/summary")
async def get_diagnostic_summary(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive diagnostic summary for system improvements
    """
    try:
        user_id = (current_user.get("uid") if current_user else None)
        
        # Get all enhanced feedback for this user
        feedback_refs = db.collection("enhanced_outfit_feedback").where("user_id", "==", user_id).stream()
        
        summary = {
            "total_feedback": 0,
            "performance_issues": [],
            "wardrobe_issues": [],
            "generation_issues": [],
            "common_recommendations": {},
            "system_health_score": 0,
            "improvement_priorities": []
        }
        
        all_insights = []
        all_recommendations = []
        
        for feedback_doc in feedback_refs:
            feedback_data = feedback_doc.to_dict()
            summary["total_feedback"] += 1
            
            # Collect all insights and recommendations
            all_insights.extend((feedback_data.get("diagnostic_insights", []) if feedback_data else []))
            all_recommendations.extend((feedback_data.get("recommended_fixes", []) if feedback_data else []))
        
        # Analyze common issues
        insight_counts = {}
        for insight in all_insights:
            insight_counts[insight] = (insight_counts.get(insight, 0) if insight_counts else 0) + 1
        
        # Categorize issues
        for insight, count in insight_counts.items():
            if count > 1:  # Only show recurring issues
                if "performance" in insight.lower() or "response time" in insight.lower():
                    summary["performance_issues"].append({"issue": insight, "count": count})
                elif "wardrobe" in insight.lower() or "items" in insight.lower():
                    summary["wardrobe_issues"].append({"issue": insight, "count": count})
                elif "generation" in insight.lower() or "filtering" in insight.lower():
                    summary["generation_issues"].append({"issue": insight, "count": count})
        
        # Analyze recommendations
        recommendation_counts = {}
        for rec in all_recommendations:
            category = (rec.get("category", "unknown") if rec else "unknown")
            if category not in summary["common_recommendations"]:
                summary["common_recommendations"][category] = []
            summary["common_recommendations"][category].append(rec)
        
        # Calculate system health score (0-100)
        total_issues = len(all_insights)
        if total_issues > 0:
            summary["system_health_score"] = max(0, 100 - (total_issues * 10))
        
        # Generate improvement priorities
        if summary["performance_issues"]:
            summary["improvement_priorities"].append("Performance Optimization")
        if summary["wardrobe_issues"]:
            summary["improvement_priorities"].append("Wardrobe Quality Improvement")
        if summary["generation_issues"]:
            summary["improvement_priorities"].append("Generation Algorithm Enhancement")
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting diagnostic summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 