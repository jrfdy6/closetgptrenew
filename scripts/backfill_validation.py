#!/usr/bin/env python3
"""
Backfill Validation Script
Validates the quality and correctness of normalized wardrobe items
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add backend src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

try:
    from config.firebase import db
    from utils.semantic_normalization import normalize_item_metadata
    from utils.semantic_compatibility import style_matches, mood_matches, occasion_matches
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

class BackfillValidator:
    def __init__(self):
        self.validation_results = {
            'total_validated': 0,
            'passed_validation': 0,
            'failed_validation': 0,
            'validation_errors': [],
            'quality_metrics': {}
        }
    
    def validate_normalization_quality(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of normalized fields"""
        try:
            normalized = item.get('normalized', {})
            if not normalized:
                return {'valid': False, 'error': 'No normalized fields found'}
            
            # Check required fields
            required_fields = ['style', 'occasion', 'mood', 'season']
            for field in required_fields:
                if field not in normalized:
                    return {'valid': False, 'error': f'Missing required field: {field}'}
                
                if not isinstance(normalized[field], list):
                    return {'valid': False, 'error': f'Field {field} is not a list'}
            
            # Check data quality
            quality_issues = []
            
            # Check for empty arrays (might be acceptable)
            for field in required_fields:
                if len(normalized[field]) == 0:
                    quality_issues.append(f'Empty {field} array')
            
            # Check for non-string values
            for field in required_fields:
                for value in normalized[field]:
                    if not isinstance(value, str):
                        quality_issues.append(f'Non-string value in {field}: {value}')
                    elif not value.strip():
                        quality_issues.append(f'Empty string in {field}')
            
            # Check for proper lowercase normalization
            for field in required_fields:
                for value in normalized[field]:
                    if value != value.lower():
                        quality_issues.append(f'Non-lowercase value in {field}: {value}')
            
            return {
                'valid': len(quality_issues) == 0,
                'quality_issues': quality_issues,
                'field_counts': {field: len(normalized[field]) for field in required_fields}
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {e}'}
    
    def validate_semantic_compatibility(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Validate semantic compatibility functionality"""
        try:
            normalized = item.get('normalized', {})
            if not normalized:
                return {'valid': False, 'error': 'No normalized fields for compatibility testing'}
            
            # Test style compatibility
            item_styles = normalized.get('style', [])
            if item_styles:
                # Test with first style
                test_style = item_styles[0]
                style_compatible = style_matches(test_style, item_styles)
                if not style_compatible:
                    return {'valid': False, 'error': f'Style compatibility failed for {test_style}'}
            
            # Test mood compatibility
            item_moods = normalized.get('mood', [])
            if item_moods:
                # Test with first mood
                test_mood = item_moods[0]
                mood_compatible = mood_matches(test_mood, item_moods)
                if not mood_compatible:
                    return {'valid': False, 'error': f'Mood compatibility failed for {test_mood}'}
            
            # Test occasion compatibility
            item_occasions = normalized.get('occasion', [])
            if item_occasions:
                # Test with first occasion
                test_occasion = item_occasions[0]
                occasion_compatible = occasion_matches(test_occasion, item_occasions)
                if not occasion_compatible:
                    return {'valid': False, 'error': f'Occasion compatibility failed for {test_occasion}'}
            
            return {
                'valid': True,
                'compatibility_tests': {
                    'style': len(item_styles),
                    'mood': len(item_moods),
                    'occasion': len(item_occasions)
                }
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Compatibility validation error: {e}'}
    
    def validate_consistency(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency between original and normalized fields"""
        try:
            normalized = item.get('normalized', {})
            if not normalized:
                return {'valid': False, 'error': 'No normalized fields for consistency testing'}
            
            # Re-normalize the original item
            renormalized = normalize_item_metadata(item)
            
            # Compare normalized fields
            consistency_issues = []
            
            for field in ['style', 'occasion', 'mood', 'season']:
                original_normalized = set(renormalized.get(field, []))
                stored_normalized = set(normalized.get(field, []))
                
                if original_normalized != stored_normalized:
                    consistency_issues.append(f'{field} mismatch: {original_normalized} vs {stored_normalized}')
            
            return {
                'valid': len(consistency_issues) == 0,
                'consistency_issues': consistency_issues
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Consistency validation error: {e}'}
    
    def validate_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single item"""
        item_id = item.get('id', 'unknown')
        item_name = item.get('name', 'Unknown')
        
        validation_result = {
            'item_id': item_id,
            'item_name': item_name,
            'validations': {},
            'overall_valid': True,
            'errors': []
        }
        
        # Run all validations
        validations = [
            ('normalization_quality', self.validate_normalization_quality),
            ('semantic_compatibility', self.validate_semantic_compatibility),
            ('consistency', self.validate_consistency)
        ]
        
        for validation_name, validation_func in validations:
            try:
                result = validation_func(item)
                validation_result['validations'][validation_name] = result
                
                if not result.get('valid', False):
                    validation_result['overall_valid'] = False
                    validation_result['errors'].append(f"{validation_name}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                validation_result['validations'][validation_name] = {
                    'valid': False,
                    'error': f'Validation crashed: {e}'
                }
                validation_result['overall_valid'] = False
                validation_result['errors'].append(f"{validation_name}: Validation crashed")
        
        return validation_result
    
    def validate_sample_items(self, sample_size: int = 100) -> Dict[str, Any]:
        """Validate a sample of normalized items"""
        try:
            # Get sample of normalized items
            docs = db.collection('wardrobe')\
                .where('normalized', '!=', None)\
                .limit(sample_size)\
                .stream()
            
            sample_items = []
            for doc in docs:
                item_data = doc.to_dict()
                sample_items.append(item_data)
            
            logger.info(f"🔍 Validating {len(sample_items)} sample items...")
            
            validation_results = []
            for item in sample_items:
                result = self.validate_item(item)
                validation_results.append(result)
                
                if not result['overall_valid']:
                    logger.warning(f"❌ Item {result['item_name']} failed validation: {', '.join(result['errors'])}")
                else:
                    logger.debug(f"✅ Item {result['item_name']} passed validation")
            
            # Calculate statistics
            total_validated = len(validation_results)
            passed_validation = sum(1 for r in validation_results if r['overall_valid'])
            failed_validation = total_validated - passed_validation
            
            # Calculate quality metrics
            quality_metrics = self.calculate_quality_metrics(validation_results)
            
            return {
                'total_validated': total_validated,
                'passed_validation': passed_validation,
                'failed_validation': failed_validation,
                'success_rate': (passed_validation / total_validated * 100) if total_validated > 0 else 0,
                'quality_metrics': quality_metrics,
                'validation_results': validation_results,
                'validated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error validating sample items: {e}")
            return {
                'error': str(e),
                'validated_at': datetime.utcnow().isoformat()
            }
    
    def calculate_quality_metrics(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics from validation results"""
        try:
            metrics = {
                'average_field_counts': {'style': 0, 'occasion': 0, 'mood': 0, 'season': 0},
                'validation_failure_reasons': {},
                'quality_issues': {}
            }
            
            total_items = len(validation_results)
            if total_items == 0:
                return metrics
            
            # Calculate average field counts
            for result in validation_results:
                for validation_name, validation_data in result.get('validations', {}).items():
                    if validation_name == 'normalization_quality' and 'field_counts' in validation_data:
                        for field, count in validation_data['field_counts'].items():
                            metrics['average_field_counts'][field] += count
            
            # Normalize averages
            for field in metrics['average_field_counts']:
                metrics['average_field_counts'][field] /= total_items
            
            # Count validation failure reasons
            for result in validation_results:
                if not result['overall_valid']:
                    for error in result['errors']:
                        reason = error.split(':')[0] if ':' in error else error
                        metrics['validation_failure_reasons'][reason] = metrics['validation_failure_reasons'].get(reason, 0) + 1
            
            # Count quality issues
            for result in validation_results:
                for validation_name, validation_data in result.get('validations', {}).items():
                    if 'quality_issues' in validation_data:
                        for issue in validation_data['quality_issues']:
                            metrics['quality_issues'][issue] = metrics['quality_issues'].get(issue, 0) + 1
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating quality metrics: {e}")
            return {}
    
    def generate_validation_report(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive validation report"""
        try:
            report = {
                'report_generated_at': datetime.utcnow().isoformat(),
                'summary': {
                    'total_validated': validation_data.get('total_validated', 0),
                    'passed_validation': validation_data.get('passed_validation', 0),
                    'failed_validation': validation_data.get('failed_validation', 0),
                    'success_rate': validation_data.get('success_rate', 0)
                },
                'quality_metrics': validation_data.get('quality_metrics', {}),
                'recommendations': self.get_validation_recommendations(validation_data),
                'detailed_results': validation_data.get('validation_results', [])
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating validation report: {e}")
            return {
                'error': str(e),
                'report_generated_at': datetime.utcnow().isoformat()
            }
    
    def get_validation_recommendations(self, validation_data: Dict[str, Any]) -> List[str]:
        """Get recommendations based on validation results"""
        recommendations = []
        
        success_rate = validation_data.get('success_rate', 0)
        if success_rate < 90:
            recommendations.append("Success rate below 90% - investigate validation failures")
        
        if success_rate < 95:
            recommendations.append("Success rate below 95% - consider re-running backfill for failed items")
        
        quality_metrics = validation_data.get('quality_metrics', {})
        failure_reasons = quality_metrics.get('validation_failure_reasons', {})
        
        if 'consistency' in failure_reasons:
            recommendations.append("Consistency issues detected - verify normalization logic")
        
        if 'semantic_compatibility' in failure_reasons:
            recommendations.append("Semantic compatibility issues - check compatibility matrix")
        
        if 'normalization_quality' in failure_reasons:
            recommendations.append("Normalization quality issues - review data processing")
        
        if not recommendations:
            recommendations.append("Validation passed successfully - backfill quality is good")
        
        return recommendations
    
    def print_validation_report(self, report: Dict[str, Any]):
        """Print a formatted validation report"""
        print("=" * 80)
        print("🔍 WARDROBE BACKFILL VALIDATION REPORT")
        print("=" * 80)
        
        # Summary
        summary = report.get('summary', {})
        print(f"📦 Total Validated: {summary.get('total_validated', 0)}")
        print(f"✅ Passed Validation: {summary.get('passed_validation', 0)}")
        print(f"❌ Failed Validation: {summary.get('failed_validation', 0)}")
        print(f"📈 Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        # Quality metrics
        quality_metrics = report.get('quality_metrics', {})
        if quality_metrics:
            print(f"\n📊 Quality Metrics:")
            avg_counts = quality_metrics.get('average_field_counts', {})
            for field, count in avg_counts.items():
                print(f"  • Average {field} count: {count:.1f}")
            
            failure_reasons = quality_metrics.get('validation_failure_reasons', {})
            if failure_reasons:
                print(f"\n❌ Validation Failure Reasons:")
                for reason, count in failure_reasons.items():
                    print(f"  • {reason}: {count}")
            
            quality_issues = quality_metrics.get('quality_issues', {})
            if quality_issues:
                print(f"\n⚠️  Quality Issues:")
                for issue, count in quality_issues.items():
                    print(f"  • {issue}: {count}")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        print("=" * 80)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate wardrobe backfill quality')
    parser.add_argument('--sample-size', type=int, default=100, help='Number of items to validate')
    parser.add_argument('--save-report', action='store_true', help='Save validation report to file')
    
    args = parser.parse_args()
    
    validator = BackfillValidator()
    
    # Run validation
    validation_data = validator.validate_sample_items(args.sample_size)
    
    # Generate and print report
    report = validator.generate_validation_report(validation_data)
    validator.print_validation_report(report)
    
    # Save report if requested
    if args.save_report:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"validation_report_{timestamp}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"💾 Validation report saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Error saving validation report: {e}")
    
    # Return exit code based on success rate
    success_rate = report.get('summary', {}).get('success_rate', 0)
    if success_rate >= 95:
        return 0  # Success
    elif success_rate >= 90:
        return 1  # Warning
    else:
        return 2  # Error

if __name__ == "__main__":
    exit(main())
