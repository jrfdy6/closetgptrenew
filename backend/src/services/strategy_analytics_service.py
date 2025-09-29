"""
Strategy Analytics Service - Real-time tracking of outfit generation strategy usage
Provides detailed insights into which strategies are actually being used and their performance.
"""

import time
import json
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class StrategyStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    FALLBACK = "fallback"
    SKIPPED = "skipped"

@dataclass
class StrategyExecution:
    """Record of a single strategy execution"""
    strategy: str
    user_id: str
    occasion: str
    style: str
    mood: str
    status: StrategyStatus
    confidence: float
    validation_score: float
    generation_time: float
    validation_time: float
    items_selected: int
    items_available: int
    failed_rules: List[str]
    fallback_reason: Optional[str]
    timestamp: float
    session_id: str

@dataclass
class StrategyMetrics:
    """Aggregated metrics for a strategy"""
    strategy: str
    total_executions: int
    success_count: int
    failure_count: int
    fallback_count: int
    avg_confidence: float
    avg_validation_score: float
    avg_generation_time: float
    avg_validation_time: float
    success_rate: float
    avg_items_selected: float
    common_failure_reasons: Dict[str, int]
    performance_trend: str  # "improving", "declining", "stable"

class StrategyAnalyticsService:
    """Service for tracking and analyzing strategy usage patterns"""
    
    def __init__(self):
        self.executions: List[StrategyExecution] = []
        self.strategy_metrics: Dict[str, StrategyMetrics] = {}
        self.user_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.real_time_stats = {
            'total_generations': 0,
            'active_strategies': set(),
            'current_hour_stats': defaultdict(int),
            'recent_failures': [],
            'top_performing_strategy': None,
            'worst_performing_strategy': None
        }
        
        # Performance thresholds for tuning
        self.performance_thresholds = {
            'min_success_rate': 0.7,
            'max_avg_generation_time': 2.0,
            'min_avg_confidence': 0.6,
            'max_failure_rate': 0.3
        }
        
        logger.info("📊 Strategy Analytics Service initialized")
    
    def record_strategy_execution(
        self,
        strategy: str,
        user_id: str,
        occasion: str,
        style: str,
        mood: str,
        status: StrategyStatus,
        confidence: float = 0.0,
        validation_score: float = 0.0,
        generation_time: float = 0.0,
        validation_time: float = 0.0,
        items_selected: int = 0,
        items_available: int = 0,
        failed_rules: List[str] = None,
        fallback_reason: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """Record a strategy execution with detailed metrics"""
        
        execution = StrategyExecution(
            strategy=strategy,
            user_id=user_id,
            occasion=occasion,
            style=style,
            mood=mood,
            status=status,
            confidence=confidence,
            validation_score=validation_score,
            generation_time=generation_time,
            validation_time=validation_time,
            items_selected=items_selected,
            items_available=items_available,
            failed_rules=failed_rules or [],
            fallback_reason=fallback_reason,
            timestamp=time.time(),
            session_id=session_id or f"session_{int(time.time())}"
        )
        
        # Store execution
        self.executions.append(execution)
        
        # Update real-time stats
        self._update_real_time_stats(execution)
        
        # Update strategy metrics
        self._update_strategy_metrics(strategy)
        
        # Update user patterns
        self._update_user_patterns(user_id, execution)
        
        # Log detailed execution info
        self._log_strategy_execution(execution)
        
        # Clean up old data (keep last 1000 executions)
        if len(self.executions) > 1000:
            self.executions = self.executions[-1000:]
    
    def _update_real_time_stats(self, execution: StrategyExecution) -> None:
        """Update real-time statistics"""
        self.real_time_stats['total_generations'] += 1
        self.real_time_stats['active_strategies'].add(execution.strategy)
        
        # Update hourly stats
        hour_key = datetime.fromtimestamp(execution.timestamp).strftime("%Y-%m-%d-%H")
        self.real_time_stats['current_hour_stats'][f"{execution.strategy}_{execution.status.value}"] += 1
        
        # Track recent failures
        if execution.status in [StrategyStatus.FAILED, StrategyStatus.FALLBACK]:
            self.real_time_stats['recent_failures'].append({
                'strategy': execution.strategy,
                'reason': execution.fallback_reason or 'validation_failed',
                'timestamp': execution.timestamp,
                'user_id': execution.user_id
            })
            
            # Keep only last 50 failures
            if len(self.real_time_stats['recent_failures']) > 50:
                self.real_time_stats['recent_failures'] = self.real_time_stats['recent_failures'][-50:]
    
    def _update_strategy_metrics(self, strategy: str) -> None:
        """Update metrics for a specific strategy"""
        strategy_executions = [e for e in self.executions if e.strategy == strategy]
        
        if not strategy_executions:
            return
        
        success_count = sum(1 for e in strategy_executions if e.status == StrategyStatus.SUCCESS)
        failure_count = sum(1 for e in strategy_executions if e.status == StrategyStatus.FAILED)
        fallback_count = sum(1 for e in strategy_executions if e.status == StrategyStatus.FALLBACK)
        
        avg_confidence = sum(e.confidence for e in strategy_executions) / len(strategy_executions)
        avg_validation_score = sum(e.validation_score for e in strategy_executions) / len(strategy_executions)
        avg_generation_time = sum(e.generation_time for e in strategy_executions) / len(strategy_executions)
        avg_validation_time = sum(e.validation_time for e in strategy_executions) / len(strategy_executions)
        avg_items_selected = sum(e.items_selected for e in strategy_executions) / len(strategy_executions)
        
        # Calculate common failure reasons
        failure_reasons = Counter()
        for e in strategy_executions:
            if e.failed_rules:
                failure_reasons.update(e.failed_rules)
            if e.fallback_reason:
                failure_reasons[e.fallback_reason] += 1
        
        # Determine performance trend (simplified)
        recent_executions = strategy_executions[-10:] if len(strategy_executions) >= 10 else strategy_executions
        recent_success_rate = sum(1 for e in recent_executions if e.status == StrategyStatus.SUCCESS) / len(recent_executions)
        overall_success_rate = success_count / len(strategy_executions)
        
        if recent_success_rate > overall_success_rate + 0.1:
            trend = "improving"
        elif recent_success_rate < overall_success_rate - 0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        self.strategy_metrics[strategy] = StrategyMetrics(
            strategy=strategy,
            total_executions=len(strategy_executions),
            success_count=success_count,
            failure_count=failure_count,
            fallback_count=fallback_count,
            avg_confidence=avg_confidence,
            avg_validation_score=avg_validation_score,
            avg_generation_time=avg_generation_time,
            avg_validation_time=avg_validation_time,
            success_rate=success_count / len(strategy_executions),
            avg_items_selected=avg_items_selected,
            common_failure_reasons=dict(failure_reasons),
            performance_trend=trend
        )
        
        # Update top/worst performing strategies
        self._update_performance_rankings()
    
    def _update_user_patterns(self, user_id: str, execution: StrategyExecution) -> None:
        """Update user-specific patterns"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                'total_generations': 0,
                'preferred_strategies': Counter(),
                'successful_combinations': Counter(),
                'failed_combinations': Counter(),
                'avg_confidence': 0.0,
                'last_activity': execution.timestamp
            }
        
        user_data = self.user_patterns[user_id]
        user_data['total_generations'] += 1
        user_data['preferred_strategies'][execution.strategy] += 1
        user_data['last_activity'] = execution.timestamp
        
        # Track successful combinations
        combination_key = f"{execution.occasion}_{execution.style}_{execution.mood}"
        if execution.status == StrategyStatus.SUCCESS:
            user_data['successful_combinations'][combination_key] += 1
        else:
            user_data['failed_combinations'][combination_key] += 1
        
        # Update average confidence
        all_user_executions = [e for e in self.executions if e.user_id == user_id]
        if all_user_executions:
            user_data['avg_confidence'] = sum(e.confidence for e in all_user_executions) / len(all_user_executions)
    
    def _update_performance_rankings(self) -> None:
        """Update top and worst performing strategies"""
        if not self.strategy_metrics:
            return
        
        # Sort by success rate
        sorted_strategies = sorted(
            self.strategy_metrics.items(),
            key=lambda x: x[1].success_rate,
            reverse=True
        )
        
        if sorted_strategies:
            self.real_time_stats['top_performing_strategy'] = sorted_strategies[0][0]
            self.real_time_stats['worst_performing_strategy'] = sorted_strategies[-1][0]
    
    def _log_strategy_execution(self, execution: StrategyExecution) -> None:
        """Log detailed strategy execution information"""
        status_emoji = {
            StrategyStatus.SUCCESS: "✅",
            StrategyStatus.FAILED: "❌",
            StrategyStatus.FALLBACK: "🔄",
            StrategyStatus.SKIPPED: "⏭️"
        }
        
        logger.info(f"📊 STRATEGY EXECUTION: {status_emoji[execution.status]} {execution.strategy}")
        logger.info(f"   👤 User: {execution.user_id}")
        logger.info(f"   🎯 Context: {execution.occasion} | {execution.style} | {execution.mood}")
        logger.info(f"   📈 Performance: {execution.confidence:.2f} confidence | {execution.validation_score:.2f} validation")
        logger.info(f"   ⏱️ Timing: {execution.generation_time:.3f}s generation | {execution.validation_time:.3f}s validation")
        logger.info(f"   📦 Items: {execution.items_selected}/{execution.items_available} selected")
        
        if execution.failed_rules:
            logger.info(f"   🚫 Failed rules: {', '.join(execution.failed_rules)}")
        
        if execution.fallback_reason:
            logger.info(f"   🔄 Fallback reason: {execution.fallback_reason}")
    
    def get_strategy_analytics(self, strategy: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive strategy analytics"""
        if strategy:
            if strategy not in self.strategy_metrics:
                return {"error": f"Strategy '{strategy}' not found"}
            return asdict(self.strategy_metrics[strategy])
        
        return {
            "real_time_stats": self.real_time_stats,
            "strategy_metrics": {k: asdict(v) for k, v in self.strategy_metrics.items()},
            "total_executions": len(self.executions),
            "active_strategies": list(self.real_time_stats['active_strategies']),
            "performance_thresholds": self.performance_thresholds
        }
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific analytics"""
        if user_id not in self.user_patterns:
            return {"error": f"User '{user_id}' not found"}
        
        user_data = self.user_patterns[user_id]
        user_executions = [e for e in self.executions if e.user_id == user_id]
        
        return {
            "user_id": user_id,
            "total_generations": user_data['total_generations'],
            "preferred_strategies": dict(user_data['preferred_strategies']),
            "successful_combinations": dict(user_data['successful_combinations']),
            "failed_combinations": dict(user_data['failed_combinations']),
            "avg_confidence": user_data['avg_confidence'],
            "last_activity": user_data['last_activity'],
            "recent_executions": [
                {
                    "strategy": e.strategy,
                    "status": e.status.value,
                    "confidence": e.confidence,
                    "timestamp": e.timestamp,
                    "occasion": e.occasion,
                    "style": e.style,
                    "mood": e.mood
                }
                for e in user_executions[-10:]  # Last 10 executions
            ]
        }
    
    def get_performance_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for improving strategy performance"""
        recommendations = []
        
        for strategy, metrics in self.strategy_metrics.items():
            strategy_recs = []
            
            # Check success rate
            if metrics.success_rate < self.performance_thresholds['min_success_rate']:
                strategy_recs.append({
                    "type": "success_rate",
                    "message": f"Strategy '{strategy}' has low success rate ({metrics.success_rate:.2f})",
                    "recommendation": "Consider adjusting filtering rules or confidence thresholds",
                    "priority": "high"
                })
            
            # Check generation time
            if metrics.avg_generation_time > self.performance_thresholds['max_avg_generation_time']:
                strategy_recs.append({
                    "type": "performance",
                    "message": f"Strategy '{strategy}' is slow ({metrics.avg_generation_time:.2f}s)",
                    "recommendation": "Optimize algorithm or reduce complexity",
                    "priority": "medium"
                })
            
            # Check confidence
            if metrics.avg_confidence < self.performance_thresholds['min_avg_confidence']:
                strategy_recs.append({
                    "type": "quality",
                    "message": f"Strategy '{strategy}' produces low confidence outfits ({metrics.avg_confidence:.2f})",
                    "recommendation": "Improve item selection logic or validation rules",
                    "priority": "high"
                })
            
            # Check common failure reasons
            if metrics.common_failure_reasons:
                top_failure = max(metrics.common_failure_reasons.items(), key=lambda x: x[1])
                strategy_recs.append({
                    "type": "failure_pattern",
                    "message": f"Strategy '{strategy}' commonly fails due to: {top_failure[0]}",
                    "recommendation": f"Address the '{top_failure[0]}' validation rule",
                    "priority": "medium"
                })
            
            if strategy_recs:
                recommendations.append({
                    "strategy": strategy,
                    "recommendations": strategy_recs
                })
        
        return recommendations
    
    def export_analytics_data(self) -> Dict[str, Any]:
        """Export all analytics data for external analysis"""
        return {
            "export_timestamp": time.time(),
            "total_executions": len(self.executions),
            "strategy_metrics": {k: asdict(v) for k, v in self.strategy_metrics.items()},
            "user_patterns": dict(self.user_patterns),
            "real_time_stats": self.real_time_stats,
            "performance_recommendations": self.get_performance_recommendations()
        }

# Global instance
strategy_analytics = StrategyAnalyticsService()
