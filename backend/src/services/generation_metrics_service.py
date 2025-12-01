"""
Generation Metrics Service - Track outfit generation strategy usage and patterns.
Provides counters, rates, and segmented metrics for monitoring system behavior.
"""

import time
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GenerationMetricsService:
    """Service for tracking and analyzing outfit generation metrics."""
    
    # Performance targets
    PERFORMANCE_TARGETS = {
        "outfit_generation": {"target": 5.0, "p95": 10.0},  # seconds
        "wardrobe_page_load": {"target": 2.0, "p95": 4.0},  # seconds
        "upload_processing": {"target": 10.0, "p95": 20.0},  # seconds per item
        "dashboard_load": {"target": 1.0, "p95": 2.0},  # seconds
    }
    
    def __init__(self):
        # Strategy counters
        self.strategy_counts = Counter()
        self.strategy_by_occasion = defaultdict(Counter)
        self.strategy_by_style = defaultdict(Counter)
        self.strategy_by_mood = defaultdict(Counter)
        
        # Validation failure tracking
        self.validation_failures = Counter()
        self.failed_rules_by_strategy = defaultdict(Counter)
        self.fallback_reasons = Counter()
        
        # Time-based tracking
        self.hourly_strategy_counts = defaultdict(Counter)
        self.daily_strategy_counts = defaultdict(Counter)
        
        # Performance metrics
        self.generation_times = defaultdict(list)
        self.validation_times = defaultdict(list)
        
        # Performance target violations
        self.target_violations = defaultdict(list)  # {target_name: [violation_times]}
        
        # Success/failure rates
        self.total_generations = 0
        self.successful_generations = 0
        self.fallback_generations = 0
        
    def record_generation(
        self, 
        strategy: str, 
        occasion: str, 
        style: str, 
        mood: str,
        user_id: str,
        generation_time: float = 0.0,
        validation_time: float = 0.0,
        failed_rules: List[str] = None,
        fallback_reason: str = None,
        success: bool = True
    ):
        """Record a generation event with all relevant metrics."""
        timestamp = datetime.now()
        hour_key = timestamp.strftime("%Y-%m-%d-%H")
        day_key = timestamp.strftime("%Y-%m-%d")
        
        # Basic strategy tracking
        self.strategy_counts[strategy] += 1
        self.strategy_by_occasion[occasion][strategy] += 1
        self.strategy_by_style[style][strategy] += 1
        self.strategy_by_mood[mood][strategy] += 1
        
        # Time-based tracking
        self.hourly_strategy_counts[hour_key][strategy] += 1
        self.daily_strategy_counts[day_key][strategy] += 1
        
        # Performance tracking
        if generation_time > 0:
            self.generation_times[strategy].append(generation_time)
            
            # Check performance target violations
            target = self.PERFORMANCE_TARGETS.get("outfit_generation", {})
            if generation_time > target.get("target", 5.0):
                violation = {
                    "timestamp": timestamp.isoformat(),
                    "duration": generation_time,
                    "target": target.get("target", 5.0),
                    "user_id": user_id,
                    "occasion": occasion,
                    "strategy": strategy
                }
                self.target_violations["outfit_generation"].append(violation)
                
                if generation_time > target.get("p95", 10.0):
                    logger.warning(
                        f"⚠️ PERFORMANCE TARGET VIOLATION (P95): "
                        f"Generation took {generation_time:.2f}s (P95 target: {target.get('p95', 10.0)}s) "
                        f"for user {user_id}, occasion {occasion}"
                    )
                else:
                    logger.info(
                        f"⚠️ PERFORMANCE TARGET VIOLATION: "
                        f"Generation took {generation_time:.2f}s (target: {target.get('target', 5.0)}s) "
                        f"for user {user_id}, occasion {occasion}"
                    )
        
        if validation_time > 0:
            self.validation_times[strategy].append(validation_time)
        
        # Success/failure tracking
        self.total_generations += 1
        if success:
            self.successful_generations += 1
        else:
            self.fallback_generations += 1
            
        # Validation failure tracking
        if failed_rules:
            for rule in failed_rules:
                self.validation_failures[rule] += 1
                self.failed_rules_by_strategy[strategy][rule] += 1
                
        # Fallback reason tracking
        if fallback_reason:
            self.fallback_reasons[fallback_reason] += 1
            
        # Log detailed metrics for complex analysis
        self._log_detailed_metrics(
            strategy, occasion, style, mood, user_id, 
            failed_rules, fallback_reason, success
        )
    
    def _log_detailed_metrics(
        self, 
        strategy: str, 
        occasion: str, 
        style: str, 
        mood: str,
        user_id: str,
        failed_rules: List[str] = None,
        fallback_reason: str = None,
        success: bool = True
    ):
        """Log detailed metrics for analysis."""
        # Enhanced logging with segmentation
        if strategy.startswith("fallback") or not success:
            failed_rules_str = ", ".join(failed_rules) if failed_rules else "none"
            logger.warning(
                f"[GENERATION][FALLBACK] strategy={strategy} user={user_id} "
                f"occasion={occasion} style={style} mood={mood} "
                f"failed_rules=[{failed_rules_str}] reason={fallback_reason or 'unknown'}"
            )
        else:
            logger.info(
                f"[GENERATION][SUCCESS] strategy={strategy} user={user_id} "
                f"occasion={occasion} style={style} mood={mood}"
            )
    
    def get_strategy_metrics(self) -> Dict[str, Any]:
        """Get comprehensive strategy metrics."""
        total = sum(self.strategy_counts.values())
        
        return {
            "total_generations": total,
            "success_rate": (self.successful_generations / total * 100) if total > 0 else 0,
            "fallback_rate": (self.fallback_generations / total * 100) if total > 0 else 0,
            "strategy_counts": dict(self.strategy_counts),
            "strategy_percentages": {
                strategy: (count / total * 100) if total > 0 else 0
                for strategy, count in self.strategy_counts.items()
            },
            "by_occasion": {
                occasion: dict(strategies) 
                for occasion, strategies in self.strategy_by_occasion.items()
            },
            "by_style": {
                style: dict(strategies) 
                for style, strategies in self.strategy_by_style.items()
            },
            "by_mood": {
                mood: dict(strategies) 
                for mood, strategies in self.strategy_by_mood.items()
            },
            "failed_rules": dict(self.validation_failures),
            "fallback_reasons": dict(self.fallback_reasons),
            "avg_generation_times": {
                strategy: sum(times) / len(times) if times else 0
                for strategy, times in self.generation_times.items()
            },
            "avg_validation_times": {
                strategy: sum(times) / len(times) if times else 0
                for strategy, times in self.validation_times.items()
            }
        }
    
    def get_strategy_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown of strategy usage patterns."""
        breakdown = {}
        
        # Strategy vs Occasion analysis
        for occasion, strategies in self.strategy_by_occasion.items():
            total_occasion = sum(strategies.values())
            breakdown[f"occasion_{occasion}"] = {
                "total": total_occasion,
                "strategies": {
                    strategy: {
                        "count": count,
                        "percentage": (count / total_occasion * 100) if total_occasion > 0 else 0
                    }
                    for strategy, count in strategies.items()
                }
            }
        
        # Strategy vs Style analysis
        for style, strategies in self.strategy_by_style.items():
            total_style = sum(strategies.values())
            breakdown[f"style_{style}"] = {
                "total": total_style,
                "strategies": {
                    strategy: {
                        "count": count,
                        "percentage": (count / total_style * 100) if total_style > 0 else 0
                    }
                    for strategy, count in strategies.items()
                }
            }
        
        return breakdown
    
    def get_fallback_analysis(self) -> Dict[str, Any]:
        """Analyze fallback patterns and reasons."""
        fallback_strategies = [s for s in self.strategy_counts.keys() if s.startswith("fallback")]
        fallback_total = sum(self.strategy_counts[s] for s in fallback_strategies)
        
        return {
            "fallback_total": fallback_total,
            "fallback_rate": (fallback_total / self.total_generations * 100) if self.total_generations > 0 else 0,
            "fallback_strategies": {
                strategy: {
                    "count": self.strategy_counts[strategy],
                    "percentage": (self.strategy_counts[strategy] / fallback_total * 100) if fallback_total > 0 else 0
                }
                for strategy in fallback_strategies
            },
            "most_common_failed_rules": dict(self.validation_failures.most_common(10)),
            "fallback_reasons": dict(self.fallback_reasons),
            "failed_rules_by_strategy": {
                strategy: dict(rules) 
                for strategy, rules in self.failed_rules_by_strategy.items()
            }
        }
    
    def get_performance_targets_status(self) -> Dict[str, Any]:
        """Get current performance targets status and violations."""
        status = {}
        
        # Calculate statistics for outfit generation
        all_generation_times = []
        for times in self.generation_times.values():
            all_generation_times.extend(times)
        
        if all_generation_times:
            sorted_times = sorted(all_generation_times)
            avg_time = sum(all_generation_times) / len(all_generation_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
            
            target = self.PERFORMANCE_TARGETS["outfit_generation"]
            status["outfit_generation"] = {
                "target": target["target"],
                "p95_target": target["p95"],
                "current_avg": round(avg_time, 2),
                "current_p95": round(p95_time, 2),
                "meets_target": avg_time <= target["target"],
                "meets_p95": p95_time <= target["p95"],
                "violations_count": len(self.target_violations.get("outfit_generation", [])),
                "recent_violations": self.target_violations.get("outfit_generation", [])[-10:]  # Last 10 violations
            }
        else:
            target = self.PERFORMANCE_TARGETS["outfit_generation"]
            status["outfit_generation"] = {
                "target": target["target"],
                "p95_target": target["p95"],
                "current_avg": 0.0,
                "current_p95": 0.0,
                "meets_target": True,
                "meets_p95": True,
                "violations_count": 0,
                "recent_violations": []
            }
        
        # Add all target definitions
        status["targets"] = self.PERFORMANCE_TARGETS
        
        return status
            "fallback_reasons": dict(self.fallback_reasons),
            "failed_rules_by_strategy": {
                strategy: dict(rules) 
                for strategy, rules in self.failed_rules_by_strategy.items()
            }
        }
    
    def get_hourly_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get hourly metrics for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_hours = {}
        
        for hour_key, strategies in self.hourly_strategy_counts.items():
            hour_time = datetime.strptime(hour_key, "%Y-%m-%d-%H")
            if hour_time >= cutoff:
                recent_hours[hour_key] = dict(strategies)
        
        return recent_hours
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        self.strategy_counts.clear()
        self.strategy_by_occasion.clear()
        self.strategy_by_style.clear()
        self.strategy_by_mood.clear()
        self.validation_failures.clear()
        self.failed_rules_by_strategy.clear()
        self.fallback_reasons.clear()
        self.hourly_strategy_counts.clear()
        self.daily_strategy_counts.clear()
        self.generation_times.clear()
        self.validation_times.clear()
        self.total_generations = 0
        self.successful_generations = 0
        self.fallback_generations = 0

# Global metrics instance
generation_metrics = GenerationMetricsService()
