"""
Adaptive Tuning Service - Dynamic optimization of confidence thresholds and filtering rules
Uses performance data to automatically adjust parameters for better outfit generation.
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import statistics

logger = logging.getLogger(__name__)

class TuningParameter(Enum):
    """Parameters that can be tuned"""
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    VALIDATION_STRICTNESS = "validation_strictness"
    DIVERSITY_BOOST_FACTOR = "diversity_boost_factor"
    SIMILARITY_THRESHOLD = "similarity_threshold"
    MAX_ITEMS_PER_OUTFIT = "max_items_per_outfit"
    MIN_ITEMS_PER_OUTFIT = "min_items_per_outfit"

class TuningStrategy(Enum):
    """Tuning strategies"""
    CONSERVATIVE = "conservative"  # Slow, safe adjustments
    AGGRESSIVE = "aggressive"      # Fast, bold adjustments
    ADAPTIVE = "adaptive"          # Dynamic based on performance

@dataclass
class ParameterRange:
    """Defines valid range for a tuning parameter"""
    min_value: float
    max_value: float
    step_size: float
    current_value: float
    default_value: float

@dataclass
class PerformanceMetrics:
    """Performance metrics for tuning decisions"""
    success_rate: float
    avg_confidence: float
    avg_generation_time: float
    avg_validation_time: float
    diversity_score: float
    user_satisfaction: float
    fallback_rate: float
    sample_size: int
    time_window_hours: int

@dataclass
class TuningRecommendation:
    """Recommendation for parameter adjustment"""
    parameter: TuningParameter
    current_value: float
    recommended_value: float
    adjustment_reason: str
    confidence: float
    expected_improvement: float
    risk_level: str  # "low", "medium", "high"

class AdaptiveTuningService:
    """Service for adaptive tuning of outfit generation parameters"""
    
    def __init__(self):
        # Parameter ranges and current values
        self.parameters = {
            TuningParameter.CONFIDENCE_THRESHOLD: ParameterRange(
                min_value=0.3, max_value=0.9, step_size=0.05, 
                current_value=0.6, default_value=0.7
            ),
            TuningParameter.VALIDATION_STRICTNESS: ParameterRange(
                min_value=0.1, max_value=1.0, step_size=0.1,
                current_value=0.8, default_value=0.8
            ),
            TuningParameter.DIVERSITY_BOOST_FACTOR: ParameterRange(
                min_value=0.5, max_value=3.0, step_size=0.1,
                current_value=1.5, default_value=1.5
            ),
            TuningParameter.SIMILARITY_THRESHOLD: ParameterRange(
                min_value=0.3, max_value=0.9, step_size=0.05,
                current_value=0.7, default_value=0.7
            ),
            TuningParameter.MAX_ITEMS_PER_OUTFIT: ParameterRange(
                min_value=3, max_value=8, step_size=1,
                current_value=6, default_value=6
            ),
            TuningParameter.MIN_ITEMS_PER_OUTFIT: ParameterRange(
                min_value=2, max_value=5, step_size=1,
                current_value=3, default_value=3
            )
        }
        
        # Performance tracking
        self.performance_history: List[PerformanceMetrics] = []
        self.parameter_history: List[Dict[TuningParameter, float]] = []
        self.tuning_recommendations: List[TuningRecommendation] = []
        
        # Tuning configuration
        self.tuning_strategy = TuningStrategy.ADAPTIVE
        self.min_sample_size = 50  # Minimum samples before tuning
        self.tuning_frequency_hours = 24  # How often to run tuning
        self.last_tuning_time = 0
        
        # Performance targets
        self.targets = {
            'success_rate': 0.85,
            'avg_confidence': 0.75,
            'avg_generation_time': 2.0,
            'diversity_score': 0.7,
            'fallback_rate': 0.15
        }
        
        logger.info("🎛️ Adaptive Tuning Service initialized")
    
    def record_performance(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics for tuning analysis"""
        self.performance_history.append(metrics)
        
        # Keep only recent history (last 7 days)
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        self.performance_history = [
            m for m in self.performance_history 
            if m.time_window_hours < cutoff_time
        ]
        
        logger.debug(f"📊 Recorded performance: success_rate={metrics.success_rate:.2f}, confidence={metrics.avg_confidence:.2f}")
    
    def should_tune(self) -> bool:
        """Check if it's time to run tuning"""
        current_time = time.time()
        time_since_last_tuning = current_time - self.last_tuning_time
        hours_since_tuning = time_since_last_tuning / (60 * 60)
        
        # Check if enough time has passed
        if hours_since_tuning < self.tuning_frequency_hours:
            return False
        
        # Check if we have enough recent data
        recent_metrics = [m for m in self.performance_history 
                         if m.time_window_hours > current_time - (24 * 60 * 60)]
        
        if len(recent_metrics) < self.min_sample_size:
            return False
        
        return True
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance and identify tuning opportunities"""
        
        if not self.performance_history:
            return {"error": "No performance data available"}
        
        # Get recent performance (last 24 hours)
        current_time = time.time()
        recent_metrics = [m for m in self.performance_history 
                         if m.time_window_hours > current_time - (24 * 60 * 60)]
        
        if not recent_metrics:
            return {"error": "No recent performance data"}
        
        # Calculate aggregated metrics
        avg_success_rate = statistics.mean([m.success_rate for m in recent_metrics])
        avg_confidence = statistics.mean([m.avg_confidence for m in recent_metrics])
        avg_generation_time = statistics.mean([m.avg_generation_time for m in recent_metrics])
        avg_diversity_score = statistics.mean([m.diversity_score for m in recent_metrics])
        avg_fallback_rate = statistics.mean([m.fallback_rate for m in recent_metrics])
        
        # Identify performance gaps
        gaps = {
            'success_rate': self.targets['success_rate'] - avg_success_rate,
            'confidence': self.targets['avg_confidence'] - avg_confidence,
            'generation_time': avg_generation_time - self.targets['avg_generation_time'],
            'diversity': self.targets['diversity_score'] - avg_diversity_score,
            'fallback_rate': avg_fallback_rate - self.targets['fallback_rate']
        }
        
        # Determine tuning priorities
        priorities = []
        for metric, gap in gaps.items():
            if gap > 0.05:  # Significant gap
                priorities.append({
                    'metric': metric,
                    'gap': gap,
                    'priority': 'high' if gap > 0.1 else 'medium'
                })
        
        return {
            'current_performance': {
                'success_rate': avg_success_rate,
                'confidence': avg_confidence,
                'generation_time': avg_generation_time,
                'diversity_score': avg_diversity_score,
                'fallback_rate': avg_fallback_rate
            },
            'targets': self.targets,
            'gaps': gaps,
            'priorities': priorities,
            'sample_size': len(recent_metrics)
        }
    
    def generate_tuning_recommendations(self) -> List[TuningRecommendation]:
        """Generate recommendations for parameter adjustments"""
        
        analysis = self.analyze_performance()
        if "error" in analysis:
            return []
        
        recommendations = []
        current_performance = analysis['current_performance']
        gaps = analysis['gaps']
        
        # Tune confidence threshold based on success rate and confidence
        if gaps['success_rate'] > 0.05 or gaps['confidence'] > 0.05:
            current_conf = self.parameters[TuningParameter.CONFIDENCE_THRESHOLD].current_value
            
            if gaps['success_rate'] > 0.1:  # Low success rate
                # Lower confidence threshold to allow more outfits through
                new_conf = max(current_conf - 0.1, 
                              self.parameters[TuningParameter.CONFIDENCE_THRESHOLD].min_value)
                recommendations.append(TuningRecommendation(
                    parameter=TuningParameter.CONFIDENCE_THRESHOLD,
                    current_value=current_conf,
                    recommended_value=new_conf,
                    adjustment_reason=f"Low success rate ({current_performance['success_rate']:.2f}), lowering threshold",
                    confidence=0.8,
                    expected_improvement=0.1,
                    risk_level="low"
                ))
            elif gaps['confidence'] > 0.1:  # Low confidence
                # Raise confidence threshold to improve quality
                new_conf = min(current_conf + 0.05,
                              self.parameters[TuningParameter.CONFIDENCE_THRESHOLD].max_value)
                recommendations.append(TuningRecommendation(
                    parameter=TuningParameter.CONFIDENCE_THRESHOLD,
                    current_value=current_conf,
                    recommended_value=new_conf,
                    adjustment_reason=f"Low confidence ({current_performance['confidence']:.2f}), raising threshold",
                    confidence=0.7,
                    expected_improvement=0.05,
                    risk_level="medium"
                ))
        
        # Tune diversity boost factor based on diversity score
        if gaps['diversity'] > 0.05:
            current_boost = self.parameters[TuningParameter.DIVERSITY_BOOST_FACTOR].current_value
            new_boost = min(current_boost + 0.2,
                           self.parameters[TuningParameter.DIVERSITY_BOOST_FACTOR].max_value)
            recommendations.append(TuningRecommendation(
                parameter=TuningParameter.DIVERSITY_BOOST_FACTOR,
                current_value=current_boost,
                recommended_value=new_boost,
                adjustment_reason=f"Low diversity score ({current_performance['diversity_score']:.2f}), increasing boost",
                confidence=0.6,
                expected_improvement=0.1,
                risk_level="low"
            ))
        
        # Tune similarity threshold based on diversity
        if gaps['diversity'] > 0.1:
            current_sim = self.parameters[TuningParameter.SIMILARITY_THRESHOLD].current_value
            new_sim = max(current_sim - 0.05,
                         self.parameters[TuningParameter.SIMILARITY_THRESHOLD].min_value)
            recommendations.append(TuningRecommendation(
                parameter=TuningParameter.SIMILARITY_THRESHOLD,
                current_value=current_sim,
                recommended_value=new_sim,
                adjustment_reason=f"Very low diversity ({current_performance['diversity_score']:.2f}), lowering similarity threshold",
                confidence=0.7,
                expected_improvement=0.15,
                risk_level="medium"
            ))
        
        # Tune validation strictness based on fallback rate
        if gaps['fallback_rate'] > 0.05:
            current_strict = self.parameters[TuningParameter.VALIDATION_STRICTNESS].current_value
            new_strict = max(current_strict - 0.1,
                            self.parameters[TuningParameter.VALIDATION_STRICTNESS].min_value)
            recommendations.append(TuningRecommendation(
                parameter=TuningParameter.VALIDATION_STRICTNESS,
                current_value=current_strict,
                recommended_value=new_strict,
                adjustment_reason=f"High fallback rate ({current_performance['fallback_rate']:.2f}), relaxing validation",
                confidence=0.6,
                expected_improvement=0.1,
                risk_level="medium"
            ))
        
        return recommendations
    
    def apply_tuning_recommendations(self, recommendations: List[TuningRecommendation]) -> Dict[str, Any]:
        """Apply tuning recommendations to parameters"""
        
        applied_changes = []
        rejected_changes = []
        
        for rec in recommendations:
            # Check if recommendation is safe to apply
            if rec.risk_level == "high" and rec.confidence < 0.8:
                rejected_changes.append({
                    'parameter': rec.parameter.value,
                    'reason': 'High risk, low confidence',
                    'recommendation': rec
                })
                continue
            
            # Apply the change
            old_value = self.parameters[rec.parameter].current_value
            self.parameters[rec.parameter].current_value = rec.recommended_value
            
            # Record the change
            applied_changes.append({
                'parameter': rec.parameter.value,
                'old_value': old_value,
                'new_value': rec.recommended_value,
                'reason': rec.adjustment_reason,
                'confidence': rec.confidence
            })
            
            logger.info(f"🎛️ Applied tuning: {rec.parameter.value} {old_value:.3f} → {rec.recommended_value:.3f}")
        
        # Update tuning time
        self.last_tuning_time = time.time()
        
        # Record parameter history
        current_params = {param: self.parameters[param].current_value 
                         for param in self.parameters}
        self.parameter_history.append(current_params)
        
        return {
            'applied_changes': applied_changes,
            'rejected_changes': rejected_changes,
            'total_applied': len(applied_changes),
            'total_rejected': len(rejected_changes)
        }
    
    def get_current_parameters(self) -> Dict[str, float]:
        """Get current parameter values"""
        return {param.value: self.parameters[param].current_value 
                for param in self.parameters}
    
    def get_parameter_history(self, hours: int = 24) -> List[Dict[str, float]]:
        """Get parameter history for the last N hours"""
        cutoff_time = time.time() - (hours * 60 * 60)
        return [params for params in self.parameter_history 
                if params.get('timestamp', 0) > cutoff_time]
    
    def reset_parameters_to_default(self) -> Dict[str, Any]:
        """Reset all parameters to their default values"""
        reset_count = 0
        for param in self.parameters:
            if self.parameters[param].current_value != self.parameters[param].default_value:
                self.parameters[param].current_value = self.parameters[param].default_value
                reset_count += 1
        
        logger.info(f"🔄 Reset {reset_count} parameters to default values")
        return {
            'reset_count': reset_count,
            'parameters': self.get_current_parameters()
        }
    
    def run_adaptive_tuning(self) -> Dict[str, Any]:
        """Run the complete adaptive tuning process"""
        
        if not self.should_tune():
            return {
                'tuning_performed': False,
                'reason': 'Not time for tuning or insufficient data'
            }
        
        logger.info("🎛️ Starting adaptive tuning process")
        
        # Generate recommendations
        recommendations = self.generate_tuning_recommendations()
        
        if not recommendations:
            return {
                'tuning_performed': False,
                'reason': 'No tuning recommendations generated'
            }
        
        # Apply recommendations
        result = self.apply_tuning_recommendations(recommendations)
        
        logger.info(f"🎛️ Adaptive tuning completed: {result['total_applied']} changes applied")
        
        return {
            'tuning_performed': True,
            'recommendations_generated': len(recommendations),
            'changes_applied': result['total_applied'],
            'changes_rejected': result['total_rejected'],
            'applied_changes': result['applied_changes'],
            'rejected_changes': result['rejected_changes']
        }
    
    def get_tuning_status(self) -> Dict[str, Any]:
        """Get current tuning status and recommendations"""
        
        analysis = self.analyze_performance()
        recommendations = self.generate_tuning_recommendations()
        
        return {
            'current_parameters': self.get_current_parameters(),
            'performance_analysis': analysis,
            'pending_recommendations': [asdict(rec) for rec in recommendations],
            'tuning_strategy': self.tuning_strategy.value,
            'last_tuning_time': self.last_tuning_time,
            'next_tuning_due': self.last_tuning_time + (self.tuning_frequency_hours * 60 * 60),
            'can_tune_now': self.should_tune()
        }

# Global instance
adaptive_tuning = AdaptiveTuningService()
