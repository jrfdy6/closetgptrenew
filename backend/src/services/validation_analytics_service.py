#!/usr/bin/env python3
"""
Validation Analytics Service
===========================

Comprehensive logging and analysis system for validation failures.
Provides detailed insights into validation patterns to improve outfit generation.
"""

import asyncio
import logging
import time
import json
import csv
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ValidationFailureLog:
    """Structured log entry for validation failures"""
    id: str
    timestamp: datetime
    outfit_id: str
    generation_request_id: str
    validator_name: str
    severity: str
    error_message: str
    warning_message: str
    suggestion_message: str
    context: Dict[str, Any]
    outfit_items: List[Dict[str, Any]]
    user_id: str
    validation_duration: float
    retry_attempt: int

@dataclass
class ValidationAnalytics:
    """Aggregated analytics data"""
    total_validations: int
    total_failures: int
    success_rate: float
    validator_failure_counts: Dict[str, int]
    error_message_counts: Dict[str, int]
    problematic_items: Dict[str, int]
    context_failure_patterns: Dict[str, Dict[str, int]]
    severity_distribution: Dict[str, int]
    time_series_data: List[Dict[str, Any]]

class ValidationAnalyticsService:
    """
    Service for logging and analyzing validation failures
    """
    
    def __init__(self):
        self.failure_logs: List[ValidationFailureLog] = []
        self.analytics_cache: Optional[ValidationAnalytics] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        # In-memory storage for now - can be extended to database
        self.storage = {
            "failure_logs": [],
            "analytics": {},
            "last_updated": None
        }
    
    async def log_validation_failure(
        self,
        validator_name: str,
        severity: str,
        error_message: str,
        warning_message: str,
        suggestion_message: str,
        context: Dict[str, Any],
        outfit_items: List[Dict[str, Any]],
        user_id: str,
        validation_duration: float,
        outfit_id: str = None,
        generation_request_id: str = None,
        retry_attempt: int = 0
    ) -> str:
        """
        Log a validation failure with comprehensive metadata
        """
        log_id = str(uuid.uuid4())
        
        failure_log = ValidationFailureLog(
            id=log_id,
            timestamp=datetime.utcnow(),
            outfit_id=outfit_id or f"outfit_{int(time.time())}",
            generation_request_id=generation_request_id or f"req_{int(time.time())}",
            validator_name=validator_name,
            severity=severity,
            error_message=error_message,
            warning_message=warning_message,
            suggestion_message=suggestion_message,
            context=context,
            outfit_items=outfit_items,
            user_id=user_id,
            validation_duration=validation_duration,
            retry_attempt=retry_attempt
        )
        
        # Store in memory
        self.failure_logs.append(failure_log)
        self.storage["failure_logs"].append(asdict(failure_log))
        
        # Log to console for immediate visibility
        logger.warning(f"🚨 VALIDATION FAILURE LOGGED: {validator_name}")
        logger.warning(f"   ID: {log_id}")
        logger.warning(f"   Severity: {severity}")
        logger.warning(f"   Error: {error_message}")
        logger.warning(f"   Context: {((context.get('occasion', 'unknown') if context else 'unknown') if context else 'unknown')} - {context.get('style', 'unknown')}")
        logger.warning(f"   Items: {len(outfit_items)} items")
        logger.warning(f"   User: {user_id}")
        
        # Invalidate cache
        self.analytics_cache = None
        
        return log_id
    
    async def get_analytics(self, force_refresh: bool = False) -> ValidationAnalytics:
        """
        Get comprehensive validation analytics
        """
        # Check cache
        if not force_refresh and self.analytics_cache and self.cache_timestamp:
            if datetime.utcnow() - self.cache_timestamp < self.cache_duration:
                return self.analytics_cache
        
        # Calculate analytics
        analytics = await self._calculate_analytics()
        
        # Update cache
        self.analytics_cache = analytics
        self.cache_timestamp = datetime.utcnow()
        
        return analytics
    
    async def _calculate_analytics(self) -> ValidationAnalytics:
        """
        Calculate comprehensive analytics from failure logs
        """
        total_validations = len(self.failure_logs)
        total_failures = total_validations  # All logged entries are failures
        
        # Calculate success rate (this would need total validation count from pipeline)
        success_rate = 0.0  # Will be updated when we have total validation count
        
        # Validator failure counts
        validator_counts = Counter(log.validator_name for log in self.failure_logs)
        
        # Error message counts
        error_counts = Counter()
        for log in self.failure_logs:
            if log.error_message:
                error_counts[log.error_message] += 1
        
        # Problematic items analysis
        problematic_items = Counter()
        for log in self.failure_logs:
            for item in log.outfit_items:
                item_type = (item.get('type', 'unknown') if item else 'unknown')
                item_name = (item.get('name', 'unknown') if item else 'unknown')
                problematic_items[f"{item_type}:{item_name}"] += 1
        
        # Context failure patterns
        context_patterns = defaultdict(lambda: defaultdict(int))
        for log in self.failure_logs:
            occasion = log.(context.get('occasion', 'unknown') if context else 'unknown')
            style = log.(context.get('style', 'unknown') if context else 'unknown')
            weather_temp = log.(context.get('temperature', 'unknown') if context else 'unknown')
            
            context_patterns['occasion'][occasion] += 1
            context_patterns['style'][style] += 1
            context_patterns['weather_temp'][weather_temp] += 1
        
        # Severity distribution
        severity_counts = Counter(log.severity for log in self.failure_logs)
        
        # Time series data (last 24 hours)
        now = datetime.utcnow()
        time_series = []
        for hour in range(24):
            hour_start = now - timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)
            
            hour_failures = [
                log for log in self.failure_logs
                if hour_start <= log.timestamp <= hour_end
            ]
            
            time_series.append({
                'hour': hour_start.strftime('%Y-%m-%d %H:00'),
                'failures': len(hour_failures),
                'validators': list(set(log.validator_name for log in hour_failures))
            })
        
        return ValidationAnalytics(
            total_validations=total_validations,
            total_failures=total_failures,
            success_rate=success_rate,
            validator_failure_counts=dict(validator_counts),
            error_message_counts=dict(error_counts),
            problematic_items=dict(problematic_items),
            context_failure_patterns=dict(context_patterns),
            severity_distribution=dict(severity_counts),
            time_series_data=time_series
        )
    
    async def export_analytics_csv(self, filepath: str) -> str:
        """
        Export analytics to CSV format for analysis
        """
        analytics = await self.get_analytics()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'validator', 'error_message', 'count', 'example_items', 'example_contexts'
            ])
            
            # Group failures by validator and error message
            failure_groups = defaultdict(lambda: defaultdict(list))
            
            for log in self.failure_logs:
                key = (log.validator_name, log.error_message)
                failure_groups[key]['items'].extend(log.outfit_items)
                failure_groups[key]['contexts'].append(log.context)
            
            # Write data rows
            for (validator, error_message), data in failure_groups.items():
                count = len(data['contexts'])
                
                # Get example items (first 3)
                example_items = [
                    f"{((item.get('type', 'unknown') if item else 'unknown') if item else 'unknown')}:{item.get('name', 'unknown')}"
                    for item in data['items'][:3]
                ]
                
                # Get example contexts (first 3)
                example_contexts = [
                    f"{((ctx.get('occasion', 'unknown') if ctx else 'unknown') if ctx else 'unknown')}:{ctx.get('style', 'unknown')}"
                    for ctx in data['contexts'][:3]
                ]
                
                writer.writerow([
                    validator,
                    error_message,
                    count,
                    json.dumps(example_items),
                    json.dumps(example_contexts)
                ])
        
        logger.info(f"📊 Analytics exported to CSV: {filepath}")
        return filepath
    
    async def generate_analysis_report(self) -> str:
        """
        Generate a comprehensive analysis report
        """
        analytics = await self.get_analytics()
        
        report = []
        report.append("🔍 VALIDATION ANALYTICS REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total validations: {analytics.total_validations}")
        report.append(f"Total failures: {analytics.total_failures}")
        report.append(f"Success rate: {analytics.success_rate:.1f}%")
        report.append("")
        
        # Top validator failures
        report.append("🔝 TOP VALIDATOR FAILURES:")
        for validator, count in sorted(analytics.validator_failure_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / analytics.total_failures * 100) if analytics.total_failures > 0 else 0
            report.append(f"  {validator}: {count} failures ({percentage:.1f}%)")
        report.append("")
        
        # Top error messages
        report.append("🔝 TOP ERROR MESSAGES:")
        for error, count in sorted(analytics.error_message_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / analytics.total_failures * 100) if analytics.total_failures > 0 else 0
            report.append(f"  {error}: {count} times ({percentage:.1f}%)")
        report.append("")
        
        # Problematic items
        report.append("🔝 PROBLEMATIC ITEMS:")
        for item, count in sorted(analytics.problematic_items.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / analytics.total_failures * 100) if analytics.total_failures > 0 else 0
            report.append(f"  {item}: {count} failures ({percentage:.1f}%)")
        report.append("")
        
        # Context patterns
        report.append("🔝 FAILURE PATTERNS BY CONTEXT:")
        for context_type, patterns in analytics.context_failure_patterns.items():
            report.append(f"  {context_type.upper()}:")
            for value, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (count / analytics.total_failures * 100) if analytics.total_failures > 0 else 0
                report.append(f"    {value}: {count} failures ({percentage:.1f}%)")
        report.append("")
        
        # Severity distribution
        report.append("🔝 SEVERITY DISTRIBUTION:")
        for severity, count in sorted(analytics.severity_distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / analytics.total_failures * 100) if analytics.total_failures > 0 else 0
            report.append(f"  {severity}: {count} failures ({percentage:.1f}%)")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        if analytics.validator_failure_counts:
            top_validator = max(analytics.validator_failure_counts.items(), key=lambda x: x[1])
            report.append(f"  Focus on {top_validator[0]} - {top_validator[1]} failures")
        
        if analytics.error_message_counts:
            top_error = max(analytics.error_message_counts.items(), key=lambda x: x[1])
            report.append(f"  Address '{top_error[0]}' - {top_error[1]} occurrences")
        
        if analytics.problematic_items:
            top_item = max(analytics.problematic_items.items(), key=lambda x: x[1])
            report.append(f"  Review item '{top_item[0]}' - {top_item[1]} failures")
        
        report_text = "\n".join(report)
        logger.info(f"📊 Analysis report generated: {len(report_text)} characters")
        
        return report_text
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data formatted for a dashboard display
        """
        analytics = await self.get_analytics()
        
        return {
            "summary": {
                "total_validations": analytics.total_validations,
                "total_failures": analytics.total_failures,
                "success_rate": analytics.success_rate
            },
            "top_validators": list(analytics.validator_failure_counts.items())[:5],
            "top_errors": list(analytics.error_message_counts.items())[:10],
            "problematic_items": list(analytics.problematic_items.items())[:10],
            "context_patterns": analytics.context_failure_patterns,
            "severity_distribution": analytics.severity_distribution,
            "time_series": analytics.time_series_data[-24:],  # Last 24 hours
            "last_updated": self.cache_timestamp.isoformat() if self.cache_timestamp else None
        }

# Global analytics service instance
validation_analytics = ValidationAnalyticsService()
