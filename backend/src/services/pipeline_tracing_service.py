"""
Pipeline Tracing Service for Outfit Generation Diagnostics

This service provides comprehensive tracing capabilities for the outfit generation pipeline,
enabling full explainability, debugging, and self-healing capabilities.
"""

import time
import uuid
import json
import subprocess
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..config.firebase import db
from ..core.validation_rules import validation_rules

class PipelineTracingService:
    """Service for managing comprehensive pipeline traces during outfit generation."""
    
    def __init__(self):
        self.db = db
        self.trace_collection = self.db.collection('generation_traces')
        self.session_id = str(uuid.uuid4())
        self.current_trace = []
        self.start_time = time.time()
    
    def add_trace_step(self, step: str, method: str, params: Dict[str, Any], 
                      result: Optional[Dict[str, Any]] = None, 
                      errors: Optional[List[str]] = None,
                      duration: Optional[float] = None) -> None:
        """Add a step to the current trace."""
        trace_entry = {
            "timestamp": time.time(),
            "step": step,
            "method": method,
            "params": params,
            "result": result,
            "errors": errors or [],
            "duration": duration,
            "session_id": self.session_id
        }
        self.current_trace.append(trace_entry)
    
    def add_validation_error(self, error_type: str, item_id: Optional[str] = None, 
                           reason: str = "", details: Optional[Dict[str, Any]] = None) -> None:
        """Add a validation error to the trace with fixable suggestions."""
        # Generate fixable suggestion if possible
        fixable_suggestion = None
        if details:
            fixable_suggestion = validation_rules.generate_fixable_suggestion(error_type, details)
        
        error_entry = {
            "timestamp": time.time(),
            "type": error_type,
            "item_id": item_id,
            "reason": reason,
            "details": details or {},
            "fixable": fixable_suggestion is not None,
            "suggested_fix": fixable_suggestion,
            "session_id": self.session_id
        }
        
        # Add to current trace
        if not any((entry.get("step") if entry else None) == "validation_error" for entry in self.current_trace):
            self.current_trace.append({"step": "validation_error", "errors": []})
        
        validation_entry = next(entry for entry in self.current_trace if entry.get("step") == "validation_error")
        validation_entry["errors"].append(error_entry)
    
    def add_fix_attempt(self, method: str, item_id: Optional[str] = None, 
                       original_error: str = "", fix_details: Optional[Dict[str, Any]] = None) -> None:
        """Add a fix attempt to the trace."""
        fix_entry = {
            "timestamp": time.time(),
            "method": method,
            "item_id": item_id,
            "original_error": original_error,
            "fix_details": fix_details or {},
            "session_id": self.session_id
        }
        
        # Add to current trace
        if not any((entry.get("step") if entry else None) == "fix_attempt" for entry in self.current_trace):
            self.current_trace.append({"step": "fix_attempt", "fixes": []})
        
        fix_entry_list = next(entry for entry in self.current_trace if entry.get("step") == "fix_attempt")
        fix_entry_list["fixes"].append(fix_entry)
    
    def capture_wardrobe_snapshot(self, wardrobe: List[Any], user_id: str) -> Dict[str, Any]:
        """Capture a snapshot of the wardrobe state at generation time."""
        wardrobe_summary = {
            "total_items": len(wardrobe),
            "user_id": user_id,
            "captured_at": time.time(),
            "categories": {},
            "gaps": []
        }
        
        # Count items by category
        category_counts = {}
        for item in wardrobe:
            item_type = getattr(item, 'type', 'unknown')
            category_counts[item_type] = (category_counts.get(item_type, 0) if category_counts else 0) + 1
        
        wardrobe_summary["categories"] = category_counts
        
        # Identify potential gaps (categories with very few items)
        for category, count in category_counts.items():
            if count <= 2:  # Consider it a gap if 2 or fewer items
                wardrobe_summary["gaps"].append({
                    "category": category,
                    "count": count,
                    "severity": "high" if count == 0 else "medium"
                })
        
        return wardrobe_summary
    
    def capture_system_context(self) -> Dict[str, Any]:
        """Capture system version, configuration, and context."""
        try:
            # Get git commit hash if available
            git_hash = "unknown"
            try:
                result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                      capture_output=True, text=True, cwd=os.getcwd())
                if result.returncode == 0:
                    git_hash = result.stdout.strip()
            except:
                pass
            
            # Get environment info
            env_info = {
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "platform": os.sys.platform,
                "git_hash": git_hash,
                "timestamp": time.time()
            }
            
            # Add configuration snapshot
            config_snapshot = {
                "max_attempts": 2,  # Default from outfit service
                "style_strictness": "high",
                "weather_tolerance": "medium",
                "fallback_enabled": True
            }
            
            return {
                "environment": env_info,
                "config": config_snapshot,
                "session_id": self.session_id
            }
        except Exception as e:
            return {
                "error": f"Failed to capture system context: {str(e)}",
                "session_id": self.session_id
            }
    
    def capture_user_session_context(self, user_id: str, 
                                   recent_feedback: Optional[List[Dict[str, Any]]] = None,
                                   outfit_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Capture user session context and feedback history."""
        session_context = {
            "user_id": user_id,
            "session_id": self.session_id,
            "session_start": self.start_time,
            "recent_feedback": recent_feedback or [],
            "outfit_history_count": len(outfit_history) if outfit_history else 0,
            "feedback_patterns": {}
        }
        
        # Analyze feedback patterns if available
        if recent_feedback:
            feedback_patterns = {
                "avg_rating": 0,
                "common_issues": [],
                "preferred_styles": [],
                "temperature_preferences": {}
            }
            
            ratings = [f.get("rating", 0) for f in recent_feedback if f.get("rating")]
            if ratings:
                feedback_patterns["avg_rating"] = sum(ratings) / len(ratings)
            
            # Extract common issues
            issues = [f.get("comment", "") for f in recent_feedback if f.get("comment")]
            # Simple issue extraction (could be enhanced with NLP)
            common_words = {}
            for issue in issues:
                words = issue.lower().split()
                for word in words:
                    if len(word) > 3:  # Skip short words
                        common_words[word] = (common_words.get(word, 0) if common_words else 0) + 1
            
            feedback_patterns["common_issues"] = [word for word, count in common_words.items() if count > 1]
            session_context["feedback_patterns"] = feedback_patterns
        
        return session_context
    
    def get_complete_trace(self, outfit_id: str, user_id: str, 
                          wardrobe: List[Any], 
                          recent_feedback: Optional[List[Dict[str, Any]]] = None,
                          outfit_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Get the complete trace with all context information."""
        return {
            "outfit_id": outfit_id,
            "user_id": user_id,
            "session_id": self.session_id,
            "generation_trace": self.current_trace,
            "wardrobe_snapshot": self.capture_wardrobe_snapshot(wardrobe, user_id),
            "system_context": self.capture_system_context(),
            "user_session_context": self.capture_user_session_context(
                user_id, recent_feedback, outfit_history
            ),
            "total_duration": time.time() - self.start_time,
            "timestamp": time.time()
        }
    
    async def save_trace(self, outfit_id: str, trace_data: Dict[str, Any]) -> bool:
        """Save the trace to Firestore for later analysis."""
        try:
            trace_doc = {
                "outfit_id": outfit_id,
                "trace_data": trace_data,
                "created_at": time.time()
            }
            
            # Save to generation_traces collection
            self.trace_collection.document(str(uuid.uuid4())).set(trace_doc)
            
            # Also save a reference in the outfit document
            outfit_ref = self.db.collection('outfits').document(outfit_id)
            outfit_ref.update({
                "generation_trace": trace_data["generation_trace"],
                "validation_details": {
                    "errors": [entry for entry in trace_data["generation_trace"] 
                             if entry.get("step") == "validation_error"],
                    "fixes": [entry for entry in trace_data["generation_trace"] 
                             if entry.get("step") == "fix_attempt"]
                },
                "wardrobe_snapshot": trace_data["wardrobe_snapshot"],
                "system_context": trace_data["system_context"],
                "user_session_context": trace_data["user_session_context"]
            })
            
            return True
        except Exception as e:
#             print(f"Error saving trace: {e}")
            return False
    
    def reset_trace(self) -> None:
        """Reset the current trace for a new generation."""
        self.current_trace = []
        self.session_id = str(uuid.uuid4())
        self.start_time = time.time()
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get a summary of the current trace."""
        if not self.current_trace:
            return {"status": "no_trace", "steps": 0}
        
        steps = len(self.current_trace)
        errors = sum(1 for entry in self.current_trace if entry.get("errors"))
        fixes = sum(1 for entry in self.current_trace if entry.get("step") == "fix_attempt")
        
        return {
            "status": "complete" if steps > 0 else "empty",
            "steps": steps,
            "errors": errors,
            "fixes": fixes,
            "duration": time.time() - self.start_time,
            "session_id": self.session_id
        } 