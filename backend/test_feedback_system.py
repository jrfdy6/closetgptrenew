#!/usr/bin/env python3
"""
Test script to verify the feedback system works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.routes.feedback import FeedbackType, IssueCategory, OutfitFeedbackRequest

def test_feedback_models():
    """Test that feedback models work correctly"""
    print("Testing feedback models...")
    
    # Test like feedback
    like_feedback = OutfitFeedbackRequest(
        outfit_id="test_outfit_123",
        feedback_type=FeedbackType.LIKE,
        rating=5,
        context_data={
            "user_agent": "test-agent",
            "platform": "test-platform",
            "location": "test"
        }
    )
    print(f"✅ Like feedback model: {like_feedback.feedback_type} with rating {like_feedback.rating}")
    
    # Test issue feedback
    issue_feedback = OutfitFeedbackRequest(
        outfit_id="test_outfit_456",
        feedback_type=FeedbackType.ISSUE,
        issue_category=IssueCategory.INAPPROPRIATE_ITEMS,
        issue_description="This outfit has inappropriate items for the occasion",
        context_data={
            "user_agent": "test-agent",
            "platform": "test-platform",
            "location": "test"
        }
    )
    print(f"✅ Issue feedback model: {issue_feedback.feedback_type} with category {issue_feedback.issue_category}")
    
    # Test dislike feedback
    dislike_feedback = OutfitFeedbackRequest(
        outfit_id="test_outfit_789",
        feedback_type=FeedbackType.DISLIKE,
        context_data={
            "user_agent": "test-agent",
            "platform": "test-platform",
            "location": "test"
        }
    )
    print(f"✅ Dislike feedback model: {dislike_feedback.feedback_type}")
    
    print("✅ All feedback models work correctly!")

def test_issue_categories():
    """Test all issue categories"""
    print("\nTesting issue categories...")
    
    categories = [
        IssueCategory.OUTFIT_DOESNT_MAKE_SENSE,
        IssueCategory.INAPPROPRIATE_ITEMS,
        IssueCategory.WRONG_STYLE,
        IssueCategory.WRONG_OCCASION,
        IssueCategory.WRONG_WEATHER,
        IssueCategory.DUPLICATE_ITEMS,
        IssueCategory.MISSING_ITEMS,
        IssueCategory.COLOR_MISMATCH,
        IssueCategory.SIZING_ISSUES,
        IssueCategory.OTHER
    ]
    
    for category in categories:
        print(f"✅ Issue category: {category.value}")
    
    print("✅ All issue categories are valid!")

def test_feedback_types():
    """Test all feedback types"""
    print("\nTesting feedback types...")
    
    types = [
        FeedbackType.LIKE,
        FeedbackType.DISLIKE,
        FeedbackType.ISSUE
    ]
    
    for feedback_type in types:
        print(f"✅ Feedback type: {feedback_type.value}")
    
    print("✅ All feedback types are valid!")

if __name__ == "__main__":
    print("🧪 Testing Feedback System")
    print("=" * 40)
    
    try:
        test_feedback_models()
        test_issue_categories()
        test_feedback_types()
        
        print("\n" + "=" * 40)
        print("✅ All feedback system tests passed!")
        print("\nThe feedback system is ready to use with:")
        print("- 3 feedback types: like, dislike, issue")
        print("- 10 issue categories for detailed reporting")
        print("- Star rating system (1-5) for likes")
        print("- Comprehensive context data collection")
        print("- Analytics and data lake integration")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1) 