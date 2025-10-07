#!/usr/bin/env python3
"""
Backfill Monitoring Script
Monitors the progress and health of the wardrobe backfill process
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add backend src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

try:
    from config.firebase import db
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and Firebase is configured")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackfillMonitor:
    def __init__(self):
        self.stats = {
            'total_items': 0,
            'normalized_items': 0,
            'pending_items': 0,
            'error_items': 0,
            'last_check': None
        }
    
    def get_wardrobe_stats(self) -> Dict[str, Any]:
        """Get current wardrobe statistics"""
        try:
            # Get total count
            total_docs = db.collection('wardrobe').count().get()
            total_items = total_docs[0][0].value
            
            # Get normalized count
            normalized_docs = db.collection('wardrobe').where('normalized', '!=', None).count().get()
            normalized_items = normalized_docs[0][0].value
            
            # Get error count (items with normalization errors)
            error_docs = db.collection('wardrobe').where('normalization_error', '!=', None).count().get()
            error_items = error_docs[0][0].value
            
            pending_items = total_items - normalized_items - error_items
            
            return {
                'total_items': total_items,
                'normalized_items': normalized_items,
                'pending_items': pending_items,
                'error_items': error_items,
                'completion_percentage': (normalized_items / total_items * 100) if total_items > 0 else 0,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting wardrobe stats: {e}")
            return {}
    
    def get_recent_normalizations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently normalized items"""
        try:
            docs = db.collection('wardrobe')\
                .where('normalized.normalized_at', '!=', None)\
                .order_by('normalized.normalized_at', direction='DESCENDING')\
                .limit(limit)\
                .stream()
            
            recent_items = []
            for doc in docs:
                item_data = doc.to_dict()
                recent_items.append({
                    'id': item_data.get('id', 'unknown'),
                    'name': item_data.get('name', 'Unknown'),
                    'normalized_at': item_data.get('normalized', {}).get('normalized_at'),
                    'style_count': len(item_data.get('normalized', {}).get('style', [])),
                    'occasion_count': len(item_data.get('normalized', {}).get('occasion', [])),
                    'mood_count': len(item_data.get('normalized', {}).get('mood', []))
                })
            
            return recent_items
            
        except Exception as e:
            logger.error(f"❌ Error getting recent normalizations: {e}")
            return []
    
    def get_normalization_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get items with normalization errors"""
        try:
            docs = db.collection('wardrobe')\
                .where('normalization_error', '!=', None)\
                .limit(limit)\
                .stream()
            
            error_items = []
            for doc in docs:
                item_data = doc.to_dict()
                error_items.append({
                    'id': item_data.get('id', 'unknown'),
                    'name': item_data.get('name', 'Unknown'),
                    'error': item_data.get('normalization_error'),
                    'error_at': item_data.get('error_at')
                })
            
            return error_items
            
        except Exception as e:
            logger.error(f"❌ Error getting normalization errors: {e}")
            return []
    
    def get_sample_normalized_items(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample of normalized items for verification"""
        try:
            docs = db.collection('wardrobe')\
                .where('normalized', '!=', None)\
                .limit(limit)\
                .stream()
            
            sample_items = []
            for doc in docs:
                item_data = doc.to_dict()
                normalized = item_data.get('normalized', {})
                sample_items.append({
                    'id': item_data.get('id', 'unknown'),
                    'name': item_data.get('name', 'Unknown'),
                    'original_style': item_data.get('style', []),
                    'normalized_style': normalized.get('style', []),
                    'original_occasion': item_data.get('occasion', []),
                    'normalized_occasion': normalized.get('occasion', []),
                    'original_mood': item_data.get('mood', []),
                    'normalized_mood': normalized.get('mood', []),
                    'normalized_at': normalized.get('normalized_at')
                })
            
            return sample_items
            
        except Exception as e:
            logger.error(f"❌ Error getting sample normalized items: {e}")
            return []
    
    def check_backfill_health(self) -> Dict[str, Any]:
        """Check the health of the backfill process"""
        try:
            stats = self.get_wardrobe_stats()
            
            # Calculate health metrics
            health_status = "healthy"
            issues = []
            
            if stats.get('error_items', 0) > 0:
                error_rate = (stats['error_items'] / stats['total_items']) * 100
                if error_rate > 5:  # More than 5% errors
                    health_status = "unhealthy"
                    issues.append(f"High error rate: {error_rate:.1f}%")
                elif error_rate > 1:  # More than 1% errors
                    health_status = "warning"
                    issues.append(f"Elevated error rate: {error_rate:.1f}%")
            
            if stats.get('completion_percentage', 0) < 50:
                issues.append("Low completion percentage")
            
            return {
                'status': health_status,
                'issues': issues,
                'stats': stats,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking backfill health: {e}")
            return {
                'status': 'error',
                'issues': [f"Health check failed: {e}"],
                'stats': {},
                'checked_at': datetime.utcnow().isoformat()
            }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive backfill report"""
        try:
            stats = self.get_wardrobe_stats()
            recent_items = self.get_recent_normalizations(10)
            error_items = self.get_normalization_errors(10)
            sample_items = self.get_sample_normalized_items(5)
            health = self.check_backfill_health()
            
            report = {
                'report_generated_at': datetime.utcnow().isoformat(),
                'summary': {
                    'total_items': stats.get('total_items', 0),
                    'normalized_items': stats.get('normalized_items', 0),
                    'pending_items': stats.get('pending_items', 0),
                    'error_items': stats.get('error_items', 0),
                    'completion_percentage': stats.get('completion_percentage', 0),
                    'health_status': health.get('status', 'unknown')
                },
                'health_check': health,
                'recent_normalizations': recent_items,
                'normalization_errors': error_items,
                'sample_normalized_items': sample_items,
                'recommendations': self.get_recommendations(stats, health)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return {
                'error': str(e),
                'report_generated_at': datetime.utcnow().isoformat()
            }
    
    def get_recommendations(self, stats: Dict[str, Any], health: Dict[str, Any]) -> List[str]:
        """Get recommendations based on current status"""
        recommendations = []
        
        if stats.get('completion_percentage', 0) < 50:
            recommendations.append("Consider increasing batch size or running multiple backfill processes")
        
        if stats.get('error_items', 0) > 0:
            recommendations.append("Review and fix normalization errors before continuing")
        
        if health.get('status') == 'unhealthy':
            recommendations.append("Stop backfill process and investigate issues")
        
        if stats.get('pending_items', 0) > 1000:
            recommendations.append("Large number of pending items - consider running backfill during off-peak hours")
        
        if not recommendations:
            recommendations.append("Backfill process is running smoothly")
        
        return recommendations
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted report"""
        print("=" * 80)
        print("📊 WARDROBE BACKFILL MONITORING REPORT")
        print("=" * 80)
        
        # Summary
        summary = report.get('summary', {})
        print(f"📦 Total Items: {summary.get('total_items', 0)}")
        print(f"✅ Normalized Items: {summary.get('normalized_items', 0)}")
        print(f"⏳ Pending Items: {summary.get('pending_items', 0)}")
        print(f"❌ Error Items: {summary.get('error_items', 0)}")
        print(f"📈 Completion: {summary.get('completion_percentage', 0):.1f}%")
        print(f"🏥 Health Status: {summary.get('health_status', 'unknown').upper()}")
        
        # Health check
        health = report.get('health_check', {})
        if health.get('issues'):
            print(f"\n⚠️  Issues: {', '.join(health['issues'])}")
        
        # Recent normalizations
        recent = report.get('recent_normalizations', [])
        if recent:
            print(f"\n🕒 Recent Normalizations ({len(recent)} items):")
            for item in recent[:5]:
                print(f"  • {item['name']} - {item['normalized_at']}")
        
        # Errors
        errors = report.get('normalization_errors', [])
        if errors:
            print(f"\n❌ Normalization Errors ({len(errors)} items):")
            for item in errors[:5]:
                print(f"  • {item['name']} - {item['error']}")
        
        # Sample items
        samples = report.get('sample_normalized_items', [])
        if samples:
            print(f"\n🔍 Sample Normalized Items:")
            for item in samples[:3]:
                print(f"  • {item['name']}")
                print(f"    Style: {item['original_style']} → {item['normalized_style']}")
                print(f"    Occasion: {item['original_occasion']} → {item['normalized_occasion']}")
                print(f"    Mood: {item['original_mood']} → {item['normalized_mood']}")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        print("=" * 80)
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save report to file"""
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"backfill_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"💾 Report saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor wardrobe backfill process')
    parser.add_argument('--watch', action='store_true', help='Watch mode - continuously monitor')
    parser.add_argument('--interval', type=int, default=30, help='Watch interval in seconds')
    parser.add_argument('--save-report', action='store_true', help='Save report to file')
    
    args = parser.parse_args()
    
    monitor = BackfillMonitor()
    
    if args.watch:
        logger.info(f"👀 Starting watch mode (interval: {args.interval}s)")
        try:
            while True:
                report = monitor.generate_report()
                monitor.print_report(report)
                
                if args.save_report:
                    monitor.save_report(report)
                
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Watch mode stopped")
    else:
        # Single report
        report = monitor.generate_report()
        monitor.print_report(report)
        
        if args.save_report:
            monitor.save_report(report)

if __name__ == "__main__":
    main()
