"""
Production Monitoring Service for Easy Outfit App
Comprehensive monitoring for first real users launch.

Tracks:
- Errors with full context
- Performance metrics for critical operations
- Success rates
- User journey funnels
- Service-level metrics
- Usage patterns
"""

import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict
from enum import Enum
import traceback
import os

logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    """Types of operations to monitor."""
    OUTFIT_GENERATION = "outfit_generation"
    IMAGE_UPLOAD = "image_upload"
    IMAGE_ANALYSIS = "image_analysis"
    WARDROBE_FETCH = "wardrobe_fetch"
    WARDROBE_ADD = "wardrobe_add"
    DASHBOARD_LOAD = "dashboard_load"
    AUTH = "authentication"
    PROFILE_UPDATE = "profile_update"
    OUTFIT_SAVE = "outfit_save"
    OUTFIT_FETCH = "outfit_fetch"


class UserJourneyStep(str, Enum):
    """User journey milestones."""
    SIGNUP = "signup"
    ONBOARDING_START = "onboarding_start"
    ONBOARDING_COMPLETE = "onboarding_complete"
    FIRST_ITEM_ADDED = "first_item_added"
    FIRST_OUTFIT_GENERATED = "first_outfit_generated"
    FIRST_OUTFIT_SAVED = "first_outfit_saved"
    FIRST_FAVORITE = "first_favorite"
    RETURN_VISIT = "return_visit"
    SUBSCRIPTION_VIEW = "subscription_view"
    SUBSCRIPTION_PURCHASE = "subscription_purchase"


class ServiceLayer(str, Enum):
    """Service layers in outfit generation."""
    ROBUST_GENERATION = "robust_generation"
    PERSONALIZATION = "personalization"
    RULE_BASED = "rule_based"
    SIMPLE_FALLBACK = "simple_fallback"
    EMERGENCY_MOCK = "emergency_mock"


class ProductionMonitoringService:
    """
    Comprehensive monitoring service for production launch.
    Thread-safe, low-overhead, with Firebase persistence.
    """
    
    def __init__(self):
        self.enabled = True
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # In-memory metrics (for fast aggregation)
        self.metrics = {
            'errors': [],
            'performance': [],
            'success_rates': defaultdict(lambda: {'success': 0, 'failure': 0}),
            'user_journeys': defaultdict(dict),
            'service_layers': defaultdict(int),
            'cache_stats': {'hits': 0, 'misses': 0},
            'api_calls': defaultdict(int),
        }
        
        # Alerting thresholds
        self.thresholds = {
            'outfit_generation_time_ms': 10000,  # 10s max
            'image_analysis_time_ms': 15000,  # 15s max
            'error_rate_percent': 10,  # 10% error rate triggers alert
            'success_rate_minimum': 90,  # 90% minimum success rate
        }
        
        # Firebase (lazy load)
        self._db = None
        self._firebase_available = None
    
    @property
    def db(self):
        """Lazy load Firebase to prevent startup crashes."""
        if self._firebase_available is False:
            return None
            
        if self._db is None:
            try:
                from firebase_admin import firestore
                self._db = firestore.client()
                self._firebase_available = True
                logger.info("✅ Production monitoring connected to Firebase")
            except Exception as e:
                logger.warning(f"⚠️ Firebase not available for monitoring: {e}")
                self._firebase_available = False
                self._db = None
        
        return self._db
    
    async def track_operation(
        self,
        operation: OperationType,
        user_id: str,
        status: str,  # "success" or "failure"
        duration_ms: float,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        error_type: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> None:
        """
        Track a user operation with full context.
        
        Args:
            operation: Type of operation
            user_id: User ID
            status: "success" or "failure"
            duration_ms: Duration in milliseconds
            context: Additional context (wardrobe_size, occasion, etc.)
            error: Error message if failed
            error_type: Type of error
            stack_trace: Full stack trace if available
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        # Update success rates
        self.metrics['success_rates'][operation][status] += 1
        
        # Track performance
        perf_data = {
            'operation': operation,
            'user_id': user_id,
            'status': status,
            'duration_ms': duration_ms,
            'timestamp': timestamp.isoformat(),
            'context': context or {},
        }
        
        if error:
            perf_data['error'] = error
            perf_data['error_type'] = error_type
            
            # Track errors separately for alerting
            error_data = {
                'operation': operation,
                'user_id': user_id,
                'error': error,
                'error_type': error_type,
                'stack_trace': stack_trace,
                'context': context or {},
                'timestamp': timestamp.isoformat(),
            }
            self.metrics['errors'].append(error_data)
            
            # Check if we need to alert
            await self._check_alert_thresholds(operation, error_data)
        
        # Add to performance log
        self.metrics['performance'].append(perf_data)
        
        # Persist to Firebase (async, non-blocking)
        if self.db and self.environment == "production":
            try:
                await self._persist_to_firebase(operation, perf_data, error_data if error else None)
            except Exception as e:
                logger.warning(f"Failed to persist metrics to Firebase: {e}")
        
        # Log important events
        if status == "failure" or duration_ms > self.thresholds.get(f'{operation}_time_ms', float('inf')):
            logger.warning(
                f"🚨 {operation} - {status} - {duration_ms:.0f}ms - User: {user_id}",
                extra={
                    'extra_fields': {
                        'operation': operation,
                        'status': status,
                        'duration_ms': duration_ms,
                        'user_id': user_id,
                        'error': error,
                        'context': context
                    }
                }
            )
    
    async def track_user_journey(
        self,
        user_id: str,
        step: UserJourneyStep,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track user journey milestones.
        
        Args:
            user_id: User ID
            step: Journey step
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        # Update in-memory tracking
        if user_id not in self.metrics['user_journeys']:
            self.metrics['user_journeys'][user_id] = {}
        
        self.metrics['user_journeys'][user_id][step] = {
            'timestamp': timestamp.isoformat(),
            'metadata': metadata or {}
        }
        
        # Persist to Firebase
        if self.db:
            try:
                doc_ref = self.db.collection('user_journeys').document(user_id)
                doc_ref.set({
                    step: {
                        'timestamp': timestamp,
                        'metadata': metadata or {},
                        'completed': True
                    }
                }, merge=True)
                
                logger.info(f"📍 User journey: {user_id} - {step}")
            except Exception as e:
                logger.warning(f"Failed to track user journey: {e}")
    
    async def track_service_layer(
        self,
        layer: ServiceLayer,
        user_id: str,
        success: bool,
        duration_ms: float,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track which service layer was used for outfit generation.
        
        Args:
            layer: Service layer used
            user_id: User ID
            success: Whether generation succeeded
            duration_ms: Duration
            context: Additional context
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        # Track layer usage
        self.metrics['service_layers'][layer] += 1
        
        # Log fallback usage (important!)
        if layer in [ServiceLayer.RULE_BASED, ServiceLayer.SIMPLE_FALLBACK, ServiceLayer.EMERGENCY_MOCK]:
            logger.warning(
                f"⚠️ Fallback layer used: {layer} - User: {user_id}",
                extra={'extra_fields': {'layer': layer, 'user_id': user_id, 'context': context}}
            )
        
        # Persist to Firebase
        if self.db:
            try:
                self.db.collection('service_layer_usage').add({
                    'layer': layer,
                    'user_id': user_id,
                    'success': success,
                    'duration_ms': duration_ms,
                    'context': context or {},
                    'timestamp': timestamp
                })
            except Exception as e:
                logger.warning(f"Failed to track service layer: {e}")
    
    async def track_cache_operation(
        self,
        cache_key: str,
        hit: bool,
        operation: str = "outfit_generation"
    ) -> None:
        """Track cache hit/miss rates."""
        if not self.enabled:
            return
        
        if hit:
            self.metrics['cache_stats']['hits'] += 1
        else:
            self.metrics['cache_stats']['misses'] += 1
    
    async def track_external_api_call(
        self,
        api_name: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Track external API calls (OpenAI, Firebase, etc.)
        
        Args:
            api_name: API name (e.g., "openai_gpt4", "firebase_query")
            duration_ms: Call duration
            success: Whether call succeeded
            error: Error message if failed
        """
        if not self.enabled:
            return
        
        self.metrics['api_calls'][api_name] += 1
        
        # Log slow API calls
        if duration_ms > 5000:
            logger.warning(
                f"🐌 Slow API call: {api_name} - {duration_ms:.0f}ms",
                extra={'extra_fields': {'api': api_name, 'duration_ms': duration_ms}}
            )
        
        # Log failures
        if not success:
            logger.error(
                f"❌ API call failed: {api_name} - {error}",
                extra={'extra_fields': {'api': api_name, 'error': error}}
            )
    
    def get_success_rate(self, operation: OperationType) -> float:
        """Calculate success rate for an operation."""
        stats = self.metrics['success_rates'][operation]
        total = stats['success'] + stats['failure']
        if total == 0:
            return 100.0
        return (stats['success'] / total) * 100
    
    def get_performance_percentile(
        self,
        operation: OperationType,
        percentile: float = 95,
        time_window_minutes: int = 60
    ) -> Optional[float]:
        """
        Get performance percentile for an operation.
        
        Args:
            operation: Operation type
            percentile: Percentile to calculate (e.g., 95 for p95)
            time_window_minutes: Time window to consider
            
        Returns:
            Duration in ms at the specified percentile
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        
        # Filter to operation and time window
        relevant_metrics = [
            m for m in self.metrics['performance']
            if m['operation'] == operation and
            datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not relevant_metrics:
            return None
        
        # Calculate percentile
        durations = sorted([m['duration_ms'] for m in relevant_metrics])
        index = int(len(durations) * (percentile / 100))
        return durations[index] if index < len(durations) else durations[-1]
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        stats = self.metrics['cache_stats']
        total = stats['hits'] + stats['misses']
        if total == 0:
            return 0.0
        return (stats['hits'] / total) * 100
    
    def get_user_funnel_stats(self) -> Dict[str, Any]:
        """
        Calculate user funnel conversion rates.
        
        Returns:
            Dictionary with conversion rates for each step
        """
        total_users = len(self.metrics['user_journeys'])
        if total_users == 0:
            return {}
        
        funnel = {}
        for step in UserJourneyStep:
            completed = sum(
                1 for journey in self.metrics['user_journeys'].values()
                if step in journey
            )
            funnel[step] = {
                'completed': completed,
                'conversion_rate': (completed / total_users) * 100
            }
        
        return funnel
    
    def get_service_layer_distribution(self) -> Dict[str, Any]:
        """Get distribution of service layer usage."""
        total = sum(self.metrics['service_layers'].values())
        if total == 0:
            return {}
        
        return {
            layer: {
                'count': count,
                'percentage': (count / total) * 100
            }
            for layer, count in self.metrics['service_layers'].items()
        }
    
    async def get_summary_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics.
        
        Args:
            time_window_minutes: Time window to analyze
            
        Returns:
            Complete stats summary
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        
        # Filter recent errors
        recent_errors = [
            e for e in self.metrics['errors']
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]
        
        # Success rates
        success_rates = {
            op: self.get_success_rate(op)
            for op in OperationType
        }
        
        # Performance percentiles
        performance = {
            op: {
                'p50': self.get_performance_percentile(op, 50, time_window_minutes),
                'p95': self.get_performance_percentile(op, 95, time_window_minutes),
                'p99': self.get_performance_percentile(op, 99, time_window_minutes),
            }
            for op in OperationType
        }
        
        return {
            'time_window_minutes': time_window_minutes,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'success_rates': success_rates,
            'performance': performance,
            'cache_hit_rate': self.get_cache_hit_rate(),
            'recent_errors_count': len(recent_errors),
            'recent_errors': recent_errors[-10:],  # Last 10 errors
            'user_funnel': self.get_user_funnel_stats(),
            'service_layers': self.get_service_layer_distribution(),
            'total_operations': sum(
                stats['success'] + stats['failure']
                for stats in self.metrics['success_rates'].values()
            ),
        }
    
    async def _check_alert_thresholds(
        self,
        operation: OperationType,
        error_data: Dict[str, Any]
    ) -> None:
        """Check if we need to send alerts."""
        # Check error rate
        success_rate = self.get_success_rate(operation)
        if success_rate < self.thresholds['success_rate_minimum']:
            logger.critical(
                f"🚨🚨 CRITICAL: {operation} success rate dropped to {success_rate:.1f}%",
                extra={'extra_fields': {'operation': operation, 'success_rate': success_rate}}
            )
            
            # In production, you'd send email/Slack/PagerDuty alert here
            if self.environment == "production":
                await self._send_alert(
                    title=f"Low Success Rate Alert: {operation}",
                    message=f"Success rate: {success_rate:.1f}% (threshold: {self.thresholds['success_rate_minimum']}%)",
                    severity="critical",
                    data=error_data
                )
    
    async def _send_alert(
        self,
        title: str,
        message: str,
        severity: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Send alert (placeholder for external alerting).
        
        In production, integrate with:
        - Email (SendGrid)
        - Slack webhook
        - PagerDuty
        - Discord
        """
        logger.critical(f"🚨 ALERT: {title} - {message}")
        
        # Save to Firebase alerts collection
        if self.db:
            try:
                self.db.collection('alerts').add({
                    'title': title,
                    'message': message,
                    'severity': severity,
                    'data': data,
                    'timestamp': datetime.now(timezone.utc),
                    'acknowledged': False
                })
            except Exception as e:
                logger.error(f"Failed to save alert: {e}")
    
    async def _persist_to_firebase(
        self,
        operation: OperationType,
        perf_data: Dict[str, Any],
        error_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Persist metrics to Firebase for long-term storage."""
        if not self.db:
            return
        
        try:
            # Save performance data
            self.db.collection('performance_metrics').add(perf_data)
            
            # Save error data separately
            if error_data:
                self.db.collection('errors').add(error_data)
        
        except Exception as e:
            logger.warning(f"Failed to persist to Firebase: {e}")


# Global singleton instance
monitoring_service = ProductionMonitoringService()


# Convenience decorator for monitoring functions
def monitor_operation(operation: OperationType):
    """
    Decorator to automatically monitor function execution.
    
    Usage:
        @monitor_operation(OperationType.OUTFIT_GENERATION)
        async def generate_outfit(user_id: str, ...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or (args[0] if args else 'unknown')
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                await monitoring_service.track_operation(
                    operation=operation,
                    user_id=user_id,
                    status="success",
                    duration_ms=duration_ms,
                    context={'function': func.__name__}
                )
                
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                await monitoring_service.track_operation(
                    operation=operation,
                    user_id=user_id,
                    status="failure",
                    duration_ms=duration_ms,
                    error=str(e),
                    error_type=type(e).__name__,
                    stack_trace=traceback.format_exc(),
                    context={'function': func.__name__}
                )
                
                raise
        
        return wrapper
    return decorator

