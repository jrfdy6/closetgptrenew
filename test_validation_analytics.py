#!/usr/bin/env python3
"""
Test script for Validation Analytics System
==========================================

This script demonstrates the validation analytics system by generating
sample validation failures and analyzing them.
"""

import asyncio
import sys
import os
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.validation_analytics_service import validation_analytics, ValidationFailureLog
from services.outfit_validation_pipeline import validation_pipeline, ValidationContext
from datetime import datetime, timedelta

async def generate_sample_validation_failures():
    """Generate sample validation failures for testing analytics"""
    
    print("🧪 Generating Sample Validation Failures")
    print("=" * 50)
    
    # Sample failure scenarios
    scenarios = [
        {
            "validator": "OccasionValidator",
            "severity": "critical",
            "error": "Inappropriate shoes for business formal: ['Nike Sneakers']",
            "warning": "Too casual for business formal",
            "suggestion": "Consider dress shoes, oxfords, or loafers",
            "context": {
                "occasion": "Business Formal",
                "style": "Classic",
                "mood": "Professional",
                "temperature": 72
            },
            "items": [
                {"name": "Nike Sneakers", "type": "shoes", "color": "white"},
                {"name": "Dress Shirt", "type": "shirt", "color": "white"},
                {"name": "Dress Pants", "type": "pants", "color": "black"}
            ]
        },
        {
            "validator": "WeatherValidator",
            "severity": "high",
            "error": "Too warm (85.0°F) for heavy items: ['Winter Parka']",
            "warning": "",
            "suggestion": "Consider lighter fabrics like cotton or linen",
            "context": {
                "occasion": "Casual",
                "style": "Casual",
                "mood": "Relaxed",
                "temperature": 85
            },
            "items": [
                {"name": "Winter Parka", "type": "coat", "material": "down", "color": "black"},
                {"name": "T-Shirt", "type": "shirt", "color": "blue"},
                {"name": "Shorts", "type": "bottoms", "color": "khaki"}
            ]
        },
        {
            "validator": "OccasionValidator",
            "severity": "critical",
            "error": "Inappropriate shoes for business formal: ['Converse Sneakers']",
            "warning": "Too casual for business formal",
            "suggestion": "Consider dress shoes, oxfords, or loafers",
            "context": {
                "occasion": "Business Formal",
                "style": "Classic",
                "mood": "Professional",
                "temperature": 70
            },
            "items": [
                {"name": "Converse Sneakers", "type": "shoes", "color": "black"},
                {"name": "Dress Shirt", "type": "shirt", "color": "white"},
                {"name": "Dress Pants", "type": "pants", "color": "navy"}
            ]
        },
        {
            "validator": "WeatherValidator",
            "severity": "high",
            "error": "Too cold (35.0°F) for shorts: ['Shorts']",
            "warning": "May need more layers for cold weather",
            "suggestion": "Consider pants or long bottoms for cold weather",
            "context": {
                "occasion": "Casual",
                "style": "Casual",
                "mood": "Relaxed",
                "temperature": 35
            },
            "items": [
                {"name": "Shorts", "type": "bottoms", "color": "blue"},
                {"name": "T-Shirt", "type": "shirt", "color": "white"},
                {"name": "Sneakers", "type": "shoes", "color": "black"}
            ]
        },
        {
            "validator": "StyleValidator",
            "severity": "medium",
            "error": "",
            "warning": "Minimalist style typically uses fewer items (current: 7)",
            "suggestion": "Consider removing one or two items for a cleaner look",
            "context": {
                "occasion": "Casual",
                "style": "Minimalist",
                "mood": "Serene",
                "temperature": 75
            },
            "items": [
                {"name": "T-Shirt", "type": "shirt", "color": "white"},
                {"name": "Jeans", "type": "pants", "color": "blue"},
                {"name": "Sneakers", "type": "shoes", "color": "white"},
                {"name": "Watch", "type": "accessory", "color": "silver"},
                {"name": "Bracelet", "type": "accessory", "color": "gold"},
                {"name": "Necklace", "type": "accessory", "color": "silver"},
                {"name": "Hat", "type": "accessory", "color": "black"}
            ]
        }
    ]
    
    # Generate multiple instances of each scenario
    for scenario in scenarios:
        for i in range(3):  # Generate 3 instances of each scenario
            await validation_analytics.log_validation_failure(
                validator_name=scenario["validator"],
                severity=scenario["severity"],
                error_message=scenario["error"],
                warning_message=scenario["warning"],
                suggestion_message=scenario["suggestion"],
                context=scenario["context"],
                outfit_items=scenario["items"],
                user_id=f"test_user_{i}",
                validation_duration=0.1,
                outfit_id=f"outfit_{int(datetime.now().timestamp())}_{i}",
                generation_request_id=f"req_{int(datetime.now().timestamp())}_{i}",
                retry_attempt=0
            )
    
    print(f"✅ Generated {len(scenarios) * 3} sample validation failures")

async def test_analytics_system():
    """Test the analytics system with sample data"""
    
    print("\n🔍 Testing Validation Analytics System")
    print("=" * 50)
    
    # Generate sample data
    await generate_sample_validation_failures()
    
    # Test analytics retrieval
    print("\n📊 Retrieving Analytics...")
    analytics = await validation_analytics.get_analytics()
    
    print(f"Total validations: {analytics.total_validations}")
    print(f"Total failures: {analytics.total_failures}")
    print(f"Success rate: {analytics.success_rate:.1f}%")
    
    # Test dashboard data
    print("\n📊 Dashboard Data:")
    dashboard_data = await validation_analytics.get_dashboard_data()
    print(f"Summary: {dashboard_data['summary']}")
    print(f"Top validators: {dashboard_data['top_validators']}")
    print(f"Top errors: {dashboard_data['top_errors']}")
    
    # Test report generation
    print("\n📊 Analysis Report:")
    report = await validation_analytics.generate_analysis_report()
    print(report)
    
    # Test CSV export
    print("\n📊 CSV Export:")
    csv_path = await validation_analytics.export_analytics_csv("test_validation_analytics.csv")
    print(f"CSV exported to: {csv_path}")
    
    # Read and display CSV content
    try:
        with open(csv_path, 'r') as f:
            csv_content = f.read()
            print("\nCSV Content Preview:")
            print(csv_content[:500] + "..." if len(csv_content) > 500 else csv_content)
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    # Clean up
    try:
        os.remove(csv_path)
        print(f"\n✅ Cleaned up test file: {csv_path}")
    except Exception as e:
        print(f"Error cleaning up: {e}")

if __name__ == "__main__":
    asyncio.run(test_analytics_system())
