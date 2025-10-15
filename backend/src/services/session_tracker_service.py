"""
Session Tracker Service - Prevents item repetition within the same outfit generation session.

This is session-level tracking (resets per generation batch), separate from global diversity
tracking (based on past outfits). Works alongside the existing diversity system.
"""

import time
import logging
from typing import Dict, Set, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# In-memory session-level cache
# Structure: {session_id: {'items': set(item_ids), 'created_at': timestamp}}
SESSION_CACHE: Dict[str, Dict[str, any]] = {}

# Session TTL: 30 minutes (auto-cleanup)
SESSION_TTL_SECONDS = 30 * 60


class SessionTrackerService:
    """Lightweight session tracker to prevent item repetition within outfit generation batches."""
    
    def __init__(self, use_firestore: bool = False):
        """
        Initialize session tracker.
        
        Args:
            use_firestore: If True, persist sessions to Firestore for multi-instance environments
        """
        self.use_firestore = use_firestore
        self._cleanup_expired_sessions()
    
    def get_session_seen_items(self, session_id: str) -> Set[str]:
        """
        Get set of item IDs already seen in this session.
        
        Args:
            session_id: Unique session identifier (user_id + timestamp or request_id)
            
        Returns:
            Set of item IDs seen in this session
        """
        # Clean up old sessions first
        self._cleanup_expired_sessions()
        
        # Check in-memory cache
        if session_id in SESSION_CACHE:
            session_data = SESSION_CACHE[session_id]
            
            # Verify session hasn't expired
            if time.time() - session_data['created_at'] < SESSION_TTL_SECONDS:
                logger.debug(f"📍 Session {session_id[:8]}... found with {len(session_data['items'])} seen items")
                return session_data['items']
            else:
                # Session expired, remove it
                del SESSION_CACHE[session_id]
                logger.debug(f"🕐 Session {session_id[:8]}... expired, creating new")
        
        # Create new session if not found or expired
        SESSION_CACHE[session_id] = {
            'items': set(),
            'created_at': time.time()
        }
        logger.debug(f"✨ New session created: {session_id[:8]}...")
        
        return SESSION_CACHE[session_id]['items']
    
    def mark_item_as_seen(self, session_id: str, item_id: str) -> None:
        """
        Mark an item as seen in this session.
        
        Args:
            session_id: Session identifier
            item_id: ID of the item to mark as seen
        """
        seen_items = self.get_session_seen_items(session_id)
        seen_items.add(item_id)
        
        logger.debug(f"✅ Item {item_id} marked as seen in session {session_id[:8]}...")
    
    def is_item_seen(self, session_id: str, item_id: str) -> bool:
        """
        Check if an item has been seen in this session.
        
        Args:
            session_id: Session identifier
            item_id: ID of the item to check
            
        Returns:
            True if item was seen in this session, False otherwise
        """
        seen_items = self.get_session_seen_items(session_id)
        return item_id in seen_items
    
    def get_diversity_penalty(self, session_id: str, item_id: str) -> float:
        """
        Calculate diversity penalty for an item based on session history.
        
        Args:
            session_id: Session identifier
            item_id: ID of the item to check
            
        Returns:
            Penalty value (negative) if item was seen, 0.0 otherwise
        """
        if self.is_item_seen(session_id, item_id):
            logger.debug(f"⚠️ Session penalty applied to item {item_id} (already seen)")
            return -1.5  # Strong penalty for session repetition
        return 0.0
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear a specific session from cache.
        
        Args:
            session_id: Session identifier to clear
        """
        if session_id in SESSION_CACHE:
            del SESSION_CACHE[session_id]
            logger.debug(f"🗑️ Session {session_id[:8]}... cleared")
    
    def get_session_stats(self, session_id: str) -> Dict[str, any]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with session stats (item count, age, etc.)
        """
        if session_id not in SESSION_CACHE:
            return {
                'exists': False,
                'item_count': 0,
                'age_seconds': 0
            }
        
        session_data = SESSION_CACHE[session_id]
        age_seconds = time.time() - session_data['created_at']
        
        return {
            'exists': True,
            'item_count': len(session_data['items']),
            'age_seconds': age_seconds,
            'created_at': datetime.fromtimestamp(session_data['created_at']).isoformat(),
            'expires_in_seconds': max(0, SESSION_TTL_SECONDS - age_seconds)
        }
    
    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions from cache."""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, data in SESSION_CACHE.items()
            if current_time - data['created_at'] > SESSION_TTL_SECONDS
        ]
        
        for session_id in expired_sessions:
            del SESSION_CACHE[session_id]
        
        if expired_sessions:
            logger.debug(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_active_session_count(self) -> int:
        """Get count of active sessions."""
        self._cleanup_expired_sessions()
        return len(SESSION_CACHE)
    
    # ═══════════════════════════════════════════════════════════════
    # FIRESTORE PERSISTENCE (Optional - for multi-instance environments)
    # ═══════════════════════════════════════════════════════════════
    
    def _persist_to_firestore(self, session_id: str) -> None:
        """
        Persist session to Firestore (optional, for multi-instance environments).
        
        This would allow session tracking across multiple backend instances.
        Currently a placeholder for future implementation.
        """
        if not self.use_firestore:
            return
        
        try:
            from src.config.firebase import db
            
            if session_id not in SESSION_CACHE:
                return
            
            session_data = SESSION_CACHE[session_id]
            
            # Store in Firestore with TTL
            db.collection('sessions').document(session_id).set({
                'items': list(session_data['items']),
                'created_at': session_data['created_at'],
                'expires_at': session_data['created_at'] + SESSION_TTL_SECONDS
            })
            
            logger.debug(f"💾 Session {session_id[:8]}... persisted to Firestore")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to persist session to Firestore: {e}")
    
    def _load_from_firestore(self, session_id: str) -> Optional[Dict[str, any]]:
        """
        Load session from Firestore (optional).
        
        Returns:
            Session data if found and not expired, None otherwise
        """
        if not self.use_firestore:
            return None
        
        try:
            from src.config.firebase import db
            
            doc = db.collection('sessions').document(session_id).get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            
            # Check if expired
            if time.time() > data.get('expires_at', 0):
                # Clean up expired session
                db.collection('sessions').document(session_id).delete()
                return None
            
            # Convert items list back to set
            return {
                'items': set(data.get('items', [])),
                'created_at': data.get('created_at', time.time())
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load session from Firestore: {e}")
            return None


# Convenience function for quick access
def get_session_tracker(use_firestore: bool = False) -> SessionTrackerService:
    """Get a session tracker instance."""
    return SessionTrackerService(use_firestore=use_firestore)

