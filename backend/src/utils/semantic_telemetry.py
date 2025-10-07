"""
Semantic Filtering Telemetry and Guardrails
Monitors semantic filtering performance and provides safety alerts
"""

import time
import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class FilteringMetrics:
    """Metrics for a single filtering operation"""
    timestamp: datetime
    user_id: str
    total_items: int
    passed_items: int
    hard_rejected: int
    weather_rejected: int
    semantic_mode: bool
    filtering_mode: str
    request_occasion: str
    request_style: str
    request_mood: str
    composition_success: bool
    outfits_generated: int
    processing_time_ms: float

@dataclass
class DebugReasonCount:
    """Count of debug rejection reasons"""
    reason: str
    count: int
    percentage: float

class SemanticTelemetry:
    """Telemetry system for semantic filtering monitoring"""
    
    def __init__(self, max_history: int = 1000, alert_threshold: float = 0.8):
        self.max_history = max_history
        self.alert_threshold = alert_threshold
        self.metrics_history: deque = deque(maxlen=max_history)
        self.debug_reasons: Dict[str, int] = defaultdict(int)
        self.baseline_metrics: Optional[Dict[str, float]] = None
        self.alerts: List[str] = []
        
    def record_filtering_metrics(self, metrics: FilteringMetrics):
        """Record filtering metrics for analysis"""
        try:
            self.metrics_history.append(metrics)
            
            # Update debug reasons count
            if hasattr(metrics, 'debug_reasons'):
                for reason in metrics.debug_reasons:
                    self.debug_reasons[reason] += 1
            
            # Check for alerts
            self._check_alerts()
            
            logger.info(f"📊 Telemetry: Recorded metrics for user {metrics.user_id}, "
                       f"filter_pass_rate: {self._calculate_filter_pass_rate(metrics):.2f}, "
                       f"composition_success: {metrics.composition_success}")
            
        except Exception as e:
            logger.error(f"❌ Error recording telemetry metrics: {e}")
    
    def _calculate_filter_pass_rate(self, metrics: FilteringMetrics) -> float:
        """Calculate filter pass rate for a single request"""
        if metrics.total_items == 0:
            return 0.0
        return metrics.passed_items / metrics.total_items
    
    def _check_alerts(self):
        """Check for alert conditions"""
        if len(self.metrics_history) < 10:  # Need minimum data for alerts
            return
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 requests
        
        # Calculate recent averages
        recent_filter_pass_rate = sum(
            self._calculate_filter_pass_rate(m) for m in recent_metrics
        ) / len(recent_metrics)
        
        recent_composition_success_rate = sum(
            1 for m in recent_metrics if m.composition_success
        ) / len(recent_metrics)
        
        recent_avg_outfits = sum(
            m.outfits_generated for m in recent_metrics
        ) / len(recent_metrics)
        
        # Check for alerts
        alerts = []
        
        # Alert 1: Composition success rate drops below baseline
        if self.baseline_metrics:
            baseline_composition = self.baseline_metrics.get('composition_success_rate', 0.8)
            if recent_composition_success_rate < baseline_composition * self.alert_threshold:
                alerts.append(f"🚨 ALERT: Composition success rate dropped to {recent_composition_success_rate:.2f} "
                            f"(baseline: {baseline_composition:.2f})")
        
        # Alert 2: Filter pass rate increases drastically (too-loose matching)
        if self.baseline_metrics:
            baseline_filter_pass = self.baseline_metrics.get('filter_pass_rate', 0.3)
            if recent_filter_pass_rate > baseline_filter_pass * 2.0:  # 2x increase
                alerts.append(f"🚨 ALERT: Filter pass rate increased to {recent_filter_pass_rate:.2f} "
                            f"(baseline: {baseline_filter_pass:.2f}) - possible too-loose matching")
        
        # Alert 3: Average outfits per request drops significantly
        if self.baseline_metrics:
            baseline_outfits = self.baseline_metrics.get('avg_outfits_per_request', 3.0)
            if recent_avg_outfits < baseline_outfits * 0.5:  # 50% drop
                alerts.append(f"🚨 ALERT: Average outfits per request dropped to {recent_avg_outfits:.2f} "
                            f"(baseline: {baseline_outfits:.2f})")
        
        # Store alerts
        for alert in alerts:
            if alert not in self.alerts:
                self.alerts.append(alert)
                logger.warning(alert)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        recent_metrics = list(self.metrics_history)[-50:]  # Last 50 requests
        
        # Calculate current metrics
        current_filter_pass_rate = sum(
            self._calculate_filter_pass_rate(m) for m in recent_metrics
        ) / len(recent_metrics)
        
        current_composition_success_rate = sum(
            1 for m in recent_metrics if m.composition_success
        ) / len(recent_metrics)
        
        current_avg_outfits = sum(
            m.outfits_generated for m in recent_metrics
        ) / len(recent_metrics)
        
        # Semantic vs traditional breakdown
        semantic_metrics = [m for m in recent_metrics if m.semantic_mode]
        traditional_metrics = [m for m in recent_metrics if not m.semantic_mode]
        
        semantic_pass_rate = 0.0
        traditional_pass_rate = 0.0
        
        if semantic_metrics:
            semantic_pass_rate = sum(
                self._calculate_filter_pass_rate(m) for m in semantic_metrics
            ) / len(semantic_metrics)
        
        if traditional_metrics:
            traditional_pass_rate = sum(
                self._calculate_filter_pass_rate(m) for m in traditional_metrics
            ) / len(traditional_metrics)
        
        return {
            "status": "active",
            "total_requests": len(self.metrics_history),
            "recent_requests": len(recent_metrics),
            "current_filter_pass_rate": current_filter_pass_rate,
            "current_composition_success_rate": current_composition_success_rate,
            "current_avg_outfits_per_request": current_avg_outfits,
            "semantic_mode_requests": len(semantic_metrics),
            "traditional_mode_requests": len(traditional_metrics),
            "semantic_filter_pass_rate": semantic_pass_rate,
            "traditional_filter_pass_rate": traditional_pass_rate,
            "active_alerts": len(self.alerts),
            "baseline_established": self.baseline_metrics is not None
        }
    
    def get_debug_reason_counts(self, limit: int = 10) -> List[DebugReasonCount]:
        """Get top debug rejection reasons"""
        total_reasons = sum(self.debug_reasons.values())
        if total_reasons == 0:
            return []
        
        sorted_reasons = sorted(
            self.debug_reasons.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            DebugReasonCount(
                reason=reason,
                count=count,
                percentage=(count / total_reasons) * 100
            )
            for reason, count in sorted_reasons[:limit]
        ]
    
    def establish_baseline(self, days: int = 7):
        """Establish baseline metrics from historical data"""
        if len(self.metrics_history) < 50:
            logger.warning("⚠️ Not enough data to establish baseline (need at least 50 requests)")
            return
        
        # Use all available data for baseline
        all_metrics = list(self.metrics_history)
        
        baseline_filter_pass_rate = sum(
            self._calculate_filter_pass_rate(m) for m in all_metrics
        ) / len(all_metrics)
        
        baseline_composition_success_rate = sum(
            1 for m in all_metrics if m.composition_success
        ) / len(all_metrics)
        
        baseline_avg_outfits = sum(
            m.outfits_generated for m in all_metrics
        ) / len(all_metrics)
        
        self.baseline_metrics = {
            "filter_pass_rate": baseline_filter_pass_rate,
            "composition_success_rate": baseline_composition_success_rate,
            "avg_outfits_per_request": baseline_avg_outfits,
            "established_at": datetime.utcnow().isoformat(),
            "sample_size": len(all_metrics)
        }
        
        logger.info(f"📊 Baseline established: filter_pass_rate={baseline_filter_pass_rate:.2f}, "
                   f"composition_success_rate={baseline_composition_success_rate:.2f}, "
                   f"avg_outfits={baseline_avg_outfits:.2f}")
    
    def get_alerts(self) -> List[str]:
        """Get current alerts"""
        return self.alerts.copy()
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        logger.info("📊 Alerts cleared")

# Global telemetry instance
semantic_telemetry = SemanticTelemetry()

def record_semantic_filtering_metrics(
    user_id: str,
    total_items: int,
    passed_items: int,
    hard_rejected: int,
    weather_rejected: int,
    semantic_mode: bool,
    filtering_mode: str,
    request_occasion: str,
    request_style: str,
    request_mood: str,
    composition_success: bool,
    outfits_generated: int,
    processing_time_ms: float,
    debug_reasons: Optional[List[str]] = None
):
    """Record semantic filtering metrics"""
    metrics = FilteringMetrics(
        timestamp=datetime.utcnow(),
        user_id=user_id,
        total_items=total_items,
        passed_items=passed_items,
        hard_rejected=hard_rejected,
        weather_rejected=weather_rejected,
        semantic_mode=semantic_mode,
        filtering_mode=filtering_mode,
        request_occasion=request_occasion,
        request_style=request_style,
        request_mood=request_mood,
        composition_success=composition_success,
        outfits_generated=outfits_generated,
        processing_time_ms=processing_time_ms
    )
    
    if debug_reasons:
        metrics.debug_reasons = debug_reasons
    
    semantic_telemetry.record_filtering_metrics(metrics)

def get_semantic_telemetry_status() -> Dict[str, Any]:
    """Get current telemetry status"""
    return semantic_telemetry.get_current_metrics()

def get_debug_reason_analytics() -> List[Dict[str, Any]]:
    """Get debug reason analytics"""
    reason_counts = semantic_telemetry.get_debug_reason_counts()
    return [
        {
            "reason": rc.reason,
            "count": rc.count,
            "percentage": rc.percentage
        }
        for rc in reason_counts
    ]

def establish_telemetry_baseline():
    """Establish telemetry baseline"""
    semantic_telemetry.establish_baseline()

def get_active_alerts() -> List[str]:
    """Get active alerts"""
    return semantic_telemetry.get_alerts()
