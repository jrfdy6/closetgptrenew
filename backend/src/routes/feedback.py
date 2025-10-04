from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import firebase_admin
from firebase_admin import firestore, auth
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Initialize Firestore
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}")
    db = None

class FeedbackType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    ISSUE = "issue"

class IssueCategory(str, Enum):
    OUTFIT_DOESNT_MAKE_SENSE = "outfit_doesnt_make_sense"
    INAPPROPRIATE_ITEMS = "inappropriate_items"
    WRONG_STYLE = "wrong_style"
    WRONG_OCCASION = "wrong_occasion"
    WRONG_WEATHER = "wrong_weather"
    DUPLICATE_ITEMS = "duplicate_items"
    MISSING_ITEMS = "missing_items"
    COLOR_MISMATCH = "color_mismatch"
    SIZING_ISSUES = "sizing_issues"
    OTHER = "other"

class OutfitFeedbackRequest(BaseModel):
    outfit_id: str = Field(..., description="ID of the outfit being rated")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    issue_category: Optional[IssueCategory] = Field(None, description="Category of issue if feedback_type is 'issue'")
    issue_description: Optional[str] = Field(None, description="Detailed description of the issue")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5 for likes")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")

class OutfitFeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: Optional[str] = None

async def get_current_user(request: Request):
    """Extract user from Firebase token"""
    try:
        auth_header = request.(headers.get("Authorization") if headers else None)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = auth_header.split(" ")[1]
        try:
            # Try with default settings first
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            if "Token used too early" in str(e) or "clock" in str(e).lower():
                # If it's a clock issue, try with more lenient settings
                logger.warning(f"Clock skew detected, trying with lenient settings: {e}")
                try:
                    # Try with a more lenient clock skew tolerance
                    decoded_token = auth.verify_id_token(token, check_revoked=False)
                    return decoded_token
                except Exception as e2:
                    logger.error(f"Still failed with lenient settings: {e2}")
                    raise HTTPException(status_code=401, detail="Token validation failed")
            else:
                raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/outfit", response_model=OutfitFeedbackResponse)
async def submit_outfit_feedback(
    feedback: OutfitFeedbackRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Submit feedback for an outfit
    """
    logger.info(f"=== FEEDBACK SUBMISSION START ===")
    logger.info(f"Received feedback request: outfit_id={feedback.outfit_id}, rating={feedback.rating}, comment_length={len(feedback.comment) if feedback.comment else 0}")
    logger.info(f"Current user: {current_user}")
    
    try:
        user_id = (current_user.get("uid") if current_user else None)
        logger.info(f"Extracted user_id: {user_id}")
        
        if not user_id:
            logger.error("User ID not found in token")
            raise HTTPException(status_code=401, detail="User ID not found in token")

        # Get the outfit details for context
        logger.info(f"Fetching outfit with ID: {feedback.outfit_id}")
        outfit_ref = db.collection("outfits").document(feedback.outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None
        
        if not outfit_doc.exists:
            logger.error(f"Outfit not found: {feedback.outfit_id}")
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        logger.info(f"Outfit data retrieved: {((outfit_data.get('occasion', 'Unknown') if outfit_data else 'Unknown') if outfit_data else 'Unknown')} outfit with {len(outfit_data.get('items', []))} items")
        
        # Create comprehensive feedback document
        logger.info("Creating feedback data structure...")
        feedback_data = {
            "user_id": user_id,
            "outfit_id": feedback.outfit_id,
            "feedback_type": feedback.feedback_type.value,
            "issue_category": feedback.issue_category.value if feedback.issue_category else None,
            "issue_description": feedback.issue_description,
            "rating": feedback.rating,
            "context_data": feedback.context_data or {},
            "outfit_context": {
                "occasion": (outfit_data.get("occasion") if outfit_data else None),
                "mood": (outfit_data.get("mood") if outfit_data else None),
                "style": (outfit_data.get("style") if outfit_data else None),
                "items_count": len((outfit_data.get("items", []) if outfit_data else [])),
                "items_types": [],  # We can't get item types from IDs without fetching the items
                "created_at": (outfit_data.get("createdAt") if outfit_data else None),
                "generation_method": (outfit_data.get("generation_method", "unknown") if outfit_data else "unknown")
            },
            "user_context": {
                "user_id": user_id,
                "user_email": (current_user.get("email") if current_user else None),
                "user_preferences": (current_user.get("preferences", {}) if current_user else {}),
                "feedback_timestamp": datetime.utcnow().isoformat(),
                "session_data": feedback.(context_data.get("session_data", {}) if context_data else {}) if feedback.context_data else {}
            },
            "analytics_data": {
                "feedback_timestamp": datetime.utcnow().isoformat(),
                "feedback_category": "outfit_rating",
                "data_source": "user_feedback",
                "metadata": {
                    "user_agent": feedback.(context_data.get("user_agent") if context_data else None) if feedback.context_data else None,
                    "platform": feedback.(context_data.get("platform") if context_data else None) if feedback.context_data else None,
                    "location": feedback.(context_data.get("location") if context_data else None) if feedback.context_data else None
                }
            }
        }
        
        logger.info(f"Feedback data created: user_id={(((feedback_data.get('user_id') if feedback_data else None) if feedback_data else None) if feedback_data else None)}, outfit_id={feedback_data.get('outfit_id')}, rating={feedback_data.get('rating')}")
        
        # Store in feedback collection
        logger.info("Attempting to save to outfit_feedback collection...")
        feedback_ref = db.collection("outfit_feedback").document()
        logger.info(f"Created feedback document reference: {feedback_ref.id}")
        
        feedback_ref.set(feedback_data)
        logger.info(f"Successfully saved feedback to outfit_feedback collection with ID: {feedback_ref.id}")
        
        # Update outfit with feedback summary
        logger.info("Updating outfit with feedback summary...")
        outfit_ref.update({
            "feedback_summary": firestore.ArrayUnion([{
                "feedback_type": feedback.feedback_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }])
        })
        logger.info("Successfully updated outfit with feedback summary")
        
        # Store in analytics collection for data lake
        logger.info("Saving to analytics_events collection...")
        analytics_data = {
            "event_type": "outfit_feedback",
            "event_data": feedback_data,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "outfit_id": feedback.outfit_id,
            "feedback_type": feedback.feedback_type.value,
            "rating": feedback.rating,
            "issue_category": feedback.issue_category.value if feedback.issue_category else None,
            "metadata": {
                "source": "user_feedback",
                "version": "1.0",
                "processed": False
            }
        }
        
        analytics_ref = db.collection("analytics_events").document()
        analytics_ref.set(analytics_data)
        logger.info(f"Successfully saved to analytics_events collection with ID: {analytics_ref.id}")
        
        logger.info(f"=== FEEDBACK SUBMISSION SUCCESS ===")
        logger.info(f"Feedback submitted successfully: {feedback_ref.id}")
        
        return OutfitFeedbackResponse(
            success=True,
            message="Feedback submitted successfully",
            feedback_id=feedback_ref.id
        )
        
    except HTTPException as he:
        logger.error(f"=== FEEDBACK SUBMISSION HTTP ERROR ===")
        logger.error(f"HTTP Exception: {he}")
        raise
    except Exception as e:
        logger.error(f"=== FEEDBACK SUBMISSION EXCEPTION ===")
        logger.error(f"Error submitting feedback: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@(router.get("/outfit/{outfit_id}/summary") if router else None)
async def get_outfit_feedback_summary(
    outfit_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get feedback summary for an outfit
    """
    try:
        user_id = (current_user.get("uid") if current_user else None)
        
        # Get feedback for this outfit
        feedback_refs = db.collection("outfit_feedback").where("outfit_id", "==", outfit_id).stream()
        
        feedback_summary = {
            "total_feedback": 0,
            "likes": 0,
            "dislikes": 0,
            "issues": 0,
            "average_rating": 0,
            "issue_categories": {},
            "recent_feedback": []
        }
        
        total_rating = 0
        rating_count = 0
        
        for feedback_doc in feedback_refs:
            feedback_data = feedback_doc.to_dict()
            feedback_summary["total_feedback"] += 1
            
            if feedback_data.get("feedback_type") == "like":
                feedback_summary["likes"] += 1
                if feedback_data.get("rating"):
                    total_rating += feedback_data["rating"]
                    rating_count += 1
            elif feedback_data.get("feedback_type") == "dislike":
                feedback_summary["dislikes"] += 1
            elif feedback_data.get("feedback_type") == "issue":
                feedback_summary["issues"] += 1
                category = feedback_data.get("issue_category")
                if category:
                    feedback_summary["issue_categories"][category] = feedback_summary["issue_categories"].get(category, 0) + 1
            
            # Add to recent feedback (last 5)
            if len(feedback_summary["recent_feedback"]) < 5:
                feedback_summary["recent_feedback"].append({
                    "feedback_type": (feedback_data.get("feedback_type") if feedback_data else None),
                    "timestamp": (feedback_data.get("user_context", {}) if feedback_data else {}).get("feedback_timestamp"),
                    "rating": (feedback_data.get("rating") if feedback_data else None),
                    "issue_category": (feedback_data.get("issue_category") if feedback_data else None)
                })
        
        if rating_count > 0:
            feedback_summary["average_rating"] = round(total_rating / rating_count, 2)
        
        return {
            "success": True,
            "data": feedback_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting feedback summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@(router.get("/analytics/summary") if router else None)
async def get_feedback_analytics_summary(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get overall feedback analytics summary
    """
    try:
        user_id = (current_user.get("uid") if current_user else None)
        
        # Get all feedback for this user
        feedback_refs = db.collection("outfit_feedback").where("user_id", "==", user_id).stream()
        
        analytics_summary = {
            "total_outfits_rated": 0,
            "total_feedback": 0,
            "likes": 0,
            "dislikes": 0,
            "issues": 0,
            "average_rating": 0,
            "top_issue_categories": {},
            "feedback_trend": {},
            "preferred_occasions": {},
            "preferred_styles": {}
        }
        
        total_rating = 0
        rating_count = 0
        rated_outfits = set()
        
        for feedback_doc in feedback_refs:
            feedback_data = feedback_doc.to_dict()
            analytics_summary["total_feedback"] += 1
            rated_outfits.add((feedback_data.get("outfit_id") if feedback_data else None))
            
            if feedback_data.get("feedback_type") == "like":
                analytics_summary["likes"] += 1
                if feedback_data.get("rating"):
                    total_rating += feedback_data["rating"]
                    rating_count += 1
                    
                # Track preferred occasions and styles for likes
                outfit_context = (feedback_data.get("outfit_context", {}) if feedback_data else {})
                occasion = (outfit_context.get("occasion") if outfit_context else None)
                style = (outfit_context.get("style") if outfit_context else None)
                
                if occasion:
                    analytics_summary["preferred_occasions"][occasion] = analytics_summary["preferred_occasions"].get(occasion, 0) + 1
                if style:
                    analytics_summary["preferred_styles"][style] = analytics_summary["preferred_styles"].get(style, 0) + 1
                    
            elif feedback_data.get("feedback_type") == "dislike":
                analytics_summary["dislikes"] += 1
            elif feedback_data.get("feedback_type") == "issue":
                analytics_summary["issues"] += 1
                category = feedback_data.get("issue_category")
                if category:
                    analytics_summary["top_issue_categories"][category] = analytics_summary["top_issue_categories"].get(category, 0) + 1
        
        analytics_summary["total_outfits_rated"] = len(rated_outfits)
        
        if rating_count > 0:
            analytics_summary["average_rating"] = round(total_rating / rating_count, 2)
        
        return {
            "success": True,
            "data": analytics_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@(router.get("/user/summary") if router else None)
async def get_user_feedback_summary(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive feedback summary for the current user
    """
    try:
        user_id = (current_user.get("uid") if current_user else None)
        
        # Get all feedback for this user
        feedback_refs = db.collection("outfit_feedback").where("user_id", "==", user_id).stream()
        
        feedback_summary = {
            "total_feedback": 0,
            "likes": 0,
            "dislikes": 0,
            "issues": 0,
            "average_rating": 0,
            "top_rated_styles": [],
            "improvement_areas": [],
            "feedback_by_style": {},
            "feedback_by_occasion": {},
            "recent_feedback": [],
            "item_feedback": {}
        }
        
        total_rating = 0
        rating_count = 0
        style_ratings: Dict[str, List[float]] = {}
        occasion_ratings: Dict[str, List[float]] = {}
        item_ratings: Dict[str, List[float]] = {}
        
        for feedback_doc in feedback_refs:
            feedback_data = feedback_doc.to_dict()
            feedback_summary["total_feedback"] += 1
            
            # Track feedback types
            if feedback_data.get("feedback_type") == "like":
                feedback_summary["likes"] += 1
                if feedback_data.get("rating"):
                    total_rating += feedback_data["rating"]
                    rating_count += 1
            elif feedback_data.get("feedback_type") == "dislike":
                feedback_summary["dislikes"] += 1
            elif feedback_data.get("feedback_type") == "issue":
                feedback_summary["issues"] += 1
            
            # Track ratings by style and occasion
            outfit_context = (feedback_data.get("outfit_context", {}) if feedback_data else {})
            if outfit_context.get("style") and (feedback_data.get("rating") if feedback_data else None):
                style = outfit_context["style"].lower()
                if style not in style_ratings:
                    style_ratings[style] = []
                style_ratings[style].append(feedback_data["rating"])
            
            if outfit_context.get("occasion") and (feedback_data.get("rating") if feedback_data else None):
                occasion = outfit_context["occasion"].lower()
                if occasion not in occasion_ratings:
                    occasion_ratings[occasion] = []
                occasion_ratings[occasion].append(feedback_data["rating"])
            
            # Track item-specific feedback
            outfit_id = (feedback_data.get("outfit_id") if feedback_data else None)
            if outfit_id and (feedback_data.get("rating") if feedback_data else None):
                if outfit_id not in item_ratings:
                    item_ratings[outfit_id] = []
                item_ratings[outfit_id].append(feedback_data["rating"])
            
            # Add to recent feedback
            feedback_summary["recent_feedback"].append({
                "outfit_id": (feedback_data.get("outfit_id") if feedback_data else None),
                "feedback_type": (feedback_data.get("feedback_type") if feedback_data else None),
                "rating": (feedback_data.get("rating") if feedback_data else None),
                "timestamp": (feedback_data.get("timestamp") if feedback_data else None),
                "outfit_context": outfit_context
            })
        
        # Calculate average rating
        if rating_count > 0:
            feedback_summary["average_rating"] = total_rating / rating_count
        
        # Calculate top rated styles
        for style, ratings in style_ratings.items():
            avg_rating = sum(ratings) / len(ratings)
            feedback_summary["feedback_by_style"][style] = {
                "average_rating": avg_rating,
                "total_feedback": len(ratings),
                "ratings": ratings
            }
        
        # Get top 3 rated styles
        top_styles = sorted(
            feedback_summary["feedback_by_style"].items(),
            key=lambda x: x[1]["average_rating"],
            reverse=True
        )[:3]
        feedback_summary["top_rated_styles"] = [style for style, _ in top_styles]
        
        # Calculate occasion ratings
        for occasion, ratings in occasion_ratings.items():
            avg_rating = sum(ratings) / len(ratings)
            feedback_summary["feedback_by_occasion"][occasion] = {
                "average_rating": avg_rating,
                "total_feedback": len(ratings),
                "ratings": ratings
            }
        
        # Identify improvement areas (styles/occasions with low ratings)
        improvement_areas = []
        for style, data in feedback_summary["feedback_by_style"].items():
            if data["average_rating"] < 3.0 and data["total_feedback"] >= 2:
                improvement_areas.append(f"{style} style (avg: {data['average_rating']:.1f})")
        
        for occasion, data in feedback_summary["feedback_by_occasion"].items():
            if data["average_rating"] < 3.0 and data["total_feedback"] >= 2:
                improvement_areas.append(f"{occasion} occasions (avg: {data['average_rating']:.1f})")
        
        feedback_summary["improvement_areas"] = improvement_areas
        
        # Calculate item-specific feedback
        for outfit_id, ratings in item_ratings.items():
            feedback_summary["item_feedback"][outfit_id] = {
                "average_rating": sum(ratings) / len(ratings),
                "total_ratings": len(ratings),
                "ratings": ratings
            }
        
        # Sort recent feedback by timestamp
        feedback_summary["recent_feedback"].sort(
            key=lambda x: (x.get("timestamp") if x else None) or 0,
            reverse=True
        )
        feedback_summary["recent_feedback"] = feedback_summary["recent_feedback"][:10]
        
        logger.info(f"Generated feedback summary for user {user_id}")
        
        return {
            "success": True,
            "data": feedback_summary
        }
        
    except Exception as e:
        logger.error(f"Error generating user feedback summary: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 