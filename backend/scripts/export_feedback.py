#!/usr/bin/env python3
"""
Simple script to export feedback data for analytics and data lake.
"""

import firebase_admin
from firebase_admin import firestore
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

def export_feedback_data():
    """Export all feedback data to JSON file"""
    logger.info("Exporting feedback data...")
    
    # Get all feedback documents
    feedback_refs = db.collection("outfit_feedback").stream()
    
    feedback_data = []
    for doc in feedback_refs:
        data = doc.to_dict()
        data['feedback_id'] = doc.id
        feedback_data.append(data)
    
    # Export to JSON file
    filename = f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(feedback_data, f, indent=2, default=str)
    
    logger.info(f"Exported {len(feedback_data)} feedback records to {filename}")
    
    # Print summary
    likes = sum(1 for f in feedback_data if f.get('feedback_type') == 'like')
    dislikes = sum(1 for f in feedback_data if f.get('feedback_type') == 'dislike')
    issues = sum(1 for f in feedback_data if f.get('feedback_type') == 'issue')
    
    print(f"\nFeedback Summary:")
    print(f"Total: {len(feedback_data)}")
    print(f"Likes: {likes}")
    print(f"Dislikes: {dislikes}")
    print(f"Issues: {issues}")
    
    return feedback_data

if __name__ == "__main__":
    export_feedback_data() 