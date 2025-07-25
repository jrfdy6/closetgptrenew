#!/usr/bin/env python3
"""
Data Quality & Metadata Integrity Testing

This script specifically tests:
- Clothing metadata completeness
- Tag consistency
- Descriptions quality
- Image quality
- Outfit quiz data integrity
"""

import asyncio
import time
import random
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class DataQualityResult:
    """Represents a data quality test result."""
    test_name: str
    success: bool
    score: float
    issues: List[str]
    recommendations: List[str]

class DataQualityValidator:
    """Validator for data quality and metadata integrity."""
    
    def __init__(self):
        self.test_results = []
    
    async def run_data_quality_tests(self):
        """Run all data quality tests."""
        print("🧩 Starting Data Quality & Metadata Integrity Testing")
        print("=" * 60)
        
        # Test 1: Clothing Metadata Completeness
        print("\n📋 1. Testing Clothing Metadata Completeness")
        result = await self.test_clothing_metadata_completeness()
        self.test_results.append(result)
        
        # Test 2: Tag Consistency
        print("\n🏷️  2. Testing Tag Consistency")
        result = await self.test_tag_consistency()
        self.test_results.append(result)
        
        # Test 3: Descriptions Quality
        print("\n📝 3. Testing Descriptions Quality")
        result = await self.test_descriptions_quality()
        self.test_results.append(result)
        
        # Test 4: Image Quality
        print("\n🖼️  4. Testing Image Quality")
        result = await self.test_image_quality()
        self.test_results.append(result)
        
        # Test 5: Outfit Quiz Data
        print("\n🎯 5. Testing Outfit Quiz Data")
        result = await self.test_outfit_quiz_data()
        self.test_results.append(result)
        
        # Print final results
        self.print_data_quality_summary()
    
    async def test_clothing_metadata_completeness(self) -> DataQualityResult:
        """Test that all items have required metadata fields."""
        print("  Checking required fields...")
        
        # Define required fields for outfit generation
        required_fields = [
            'type', 'styleWeights', 'colorPalette', 'fit', 'material', 
            'tags', 'dominantColors', 'matchingColors', 'occasion', 'season'
        ]
        
        # Simulate checking a sample of items
        sample_items = self.create_sample_wardrobe_items(50)
        
        completeness_scores = []
        missing_fields_by_item = {}
        
        for item in sample_items:
            missing_fields = []
            for field in required_fields:
                if not self.has_field(item, field):
                    missing_fields.append(field)
            
            completeness_score = (len(required_fields) - len(missing_fields)) / len(required_fields)
            completeness_scores.append(completeness_score)
            
            if missing_fields:
                missing_fields_by_item[item.get('name', 'Unknown')] = missing_fields
        
        overall_score = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        
        # Generate issues and recommendations
        issues = []
        recommendations = []
        
        if overall_score < 0.9:
            issues.append(f"Overall completeness score is {overall_score:.1%}, below 90% threshold")
            recommendations.append("Implement automated metadata enrichment for missing fields")
        
        if missing_fields_by_item:
            issues.append(f"{len(missing_fields_by_item)} items have missing required fields")
            recommendations.append("Add validation checks during item upload")
        
        # Check specific field completeness
        field_completeness = {}
        for field in required_fields:
            field_score = sum(1 for item in sample_items if self.has_field(item, field)) / len(sample_items)
            field_completeness[field] = field_score
            
            if field_score < 0.8:
                issues.append(f"Field '{field}' is only {field_score:.1%} complete")
                recommendations.append(f"Prioritize enrichment for '{field}' field")
        
        success = overall_score >= 0.9
        
        print(f"    ✅ Overall completeness: {overall_score:.1%}")
        print(f"    📊 Items with missing fields: {len(missing_fields_by_item)}")
        
        return DataQualityResult(
            test_name="Clothing Metadata Completeness",
            success=success,
            score=overall_score,
            issues=issues,
            recommendations=recommendations
        )
    
    async def test_tag_consistency(self) -> DataQualityResult:
        """Test consistency of tags across items."""
        print("  Checking tag consistency...")
        
        sample_items = self.create_sample_wardrobe_items(100)
        
        # Check for consistent tag formats
        tag_issues = []
        inconsistent_items = 0
        
        # Define expected tag categories
        expected_categories = {
            'style': ['casual', 'formal', 'business', 'athletic', 'elegant', 'streetwear'],
            'occasion': ['daily', 'work', 'party', 'formal', 'casual', 'athletic'],
            'season': ['spring', 'summer', 'fall', 'winter', 'all-season'],
            'color': ['black', 'white', 'navy', 'gray', 'brown', 'blue', 'red', 'green']
        }
        
        for item in sample_items:
            item_issues = []
            
            # Check style tags
            if 'style' in item:
                style_tags = item['style']
                if not isinstance(style_tags, list):
                    item_issues.append("Style tags should be a list")
                else:
                    for tag in style_tags:
                        if tag not in expected_categories['style']:
                            item_issues.append(f"Unexpected style tag: {tag}")
            
            # Check occasion tags
            if 'occasion' in item:
                occasion_tags = item['occasion']
                if not isinstance(occasion_tags, list):
                    item_issues.append("Occasion tags should be a list")
                else:
                    for tag in occasion_tags:
                        if tag not in expected_categories['occasion']:
                            item_issues.append(f"Unexpected occasion tag: {tag}")
            
            if item_issues:
                inconsistent_items += 1
                tag_issues.extend(item_issues)
        
        consistency_score = (len(sample_items) - inconsistent_items) / len(sample_items) if sample_items else 0
        
        issues = []
        recommendations = []
        
        if consistency_score < 0.95:
            issues.append(f"Tag consistency score is {consistency_score:.1%}, below 95% threshold")
            recommendations.append("Implement tag validation and normalization")
        
        if tag_issues:
            issues.append(f"Found {len(set(tag_issues))} unique tag consistency issues")
            recommendations.append("Create tag standardization process")
        
        success = consistency_score >= 0.95
        
        print(f"    ✅ Tag consistency: {consistency_score:.1%}")
        print(f"    📊 Inconsistent items: {inconsistent_items}")
        
        return DataQualityResult(
            test_name="Tag Consistency",
            success=success,
            score=consistency_score,
            issues=issues,
            recommendations=recommendations
        )
    
    async def test_descriptions_quality(self) -> DataQualityResult:
        """Test quality of item descriptions."""
        print("  Checking description quality...")
        
        sample_items = self.create_sample_wardrobe_items(50)
        
        quality_scores = []
        description_issues = []
        
        for item in sample_items:
            description = item.get('description', '')
            score = self.assess_description_quality(description)
            quality_scores.append(score)
            
            if score < 0.7:
                description_issues.append(f"Low quality description: {description[:50]}...")
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        issues = []
        recommendations = []
        
        if avg_quality < 0.8:
            issues.append(f"Average description quality is {avg_quality:.1%}, below 80% threshold")
            recommendations.append("Implement AI-powered description generation")
        
        if description_issues:
            issues.append(f"Found {len(description_issues)} low-quality descriptions")
            recommendations.append("Add description quality validation")
        
        success = avg_quality >= 0.8
        
        print(f"    ✅ Average description quality: {avg_quality:.1%}")
        print(f"    📊 Low-quality descriptions: {len(description_issues)}")
        
        return DataQualityResult(
            test_name="Descriptions Quality",
            success=success,
            score=avg_quality,
            issues=issues,
            recommendations=recommendations
        )
    
    async def test_image_quality(self) -> DataQualityResult:
        """Test image quality and consistency."""
        print("  Checking image quality...")
        
        sample_items = self.create_sample_wardrobe_items(30)
        
        image_issues = []
        quality_scores = []
        
        for item in sample_items:
            image_url = item.get('imageUrl', '')
            score = self.assess_image_quality(image_url)
            quality_scores.append(score)
            
            if score < 0.7:
                image_issues.append(f"Low quality image: {image_url}")
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        issues = []
        recommendations = []
        
        if avg_quality < 0.85:
            issues.append(f"Average image quality is {avg_quality:.1%}, below 85% threshold")
            recommendations.append("Implement image quality validation during upload")
        
        if image_issues:
            issues.append(f"Found {len(image_issues)} low-quality images")
            recommendations.append("Add image enhancement processing")
        
        success = avg_quality >= 0.85
        
        print(f"    ✅ Average image quality: {avg_quality:.1%}")
        print(f"    📊 Low-quality images: {len(image_issues)}")
        
        return DataQualityResult(
            test_name="Image Quality",
            success=success,
            score=avg_quality,
            issues=issues,
            recommendations=recommendations
        )
    
    async def test_outfit_quiz_data(self) -> DataQualityResult:
        """Test outfit quiz data integrity."""
        print("  Checking outfit quiz data...")
        
        # Simulate outfit quiz data
        quiz_data = self.create_sample_quiz_data(20)
        
        data_issues = []
        integrity_scores = []
        
        for quiz_item in quiz_data:
            score = self.assess_quiz_data_integrity(quiz_item)
            integrity_scores.append(score)
            
            if score < 0.9:
                data_issues.append(f"Quiz item {quiz_item.get('id', 'Unknown')} has integrity issues")
        
        avg_integrity = sum(integrity_scores) / len(integrity_scores) if integrity_scores else 0
        
        issues = []
        recommendations = []
        
        if avg_integrity < 0.95:
            issues.append(f"Quiz data integrity is {avg_integrity:.1%}, below 95% threshold")
            recommendations.append("Implement quiz data validation")
        
        if data_issues:
            issues.append(f"Found {len(data_issues)} quiz items with integrity issues")
            recommendations.append("Add quiz data quality checks")
        
        success = avg_integrity >= 0.95
        
        print(f"    ✅ Quiz data integrity: {avg_integrity:.1%}")
        print(f"    📊 Items with issues: {len(data_issues)}")
        
        return DataQualityResult(
            test_name="Outfit Quiz Data",
            success=success,
            score=avg_integrity,
            issues=issues,
            recommendations=recommendations
        )
    
    # Helper methods
    
    def create_sample_wardrobe_items(self, count: int) -> List[Dict]:
        """Create sample wardrobe items for testing."""
        items = []
        
        item_types = ['shirt', 'pants', 'shoes', 'dress', 'jacket']
        colors = ['black', 'white', 'navy', 'gray', 'brown', 'blue']
        styles = ['casual', 'formal', 'business', 'athletic', 'elegant']
        occasions = ['daily', 'work', 'party', 'formal', 'casual']
        
        for i in range(count):
            # Randomly create items with varying completeness
            completeness = random.random()
            
            item = {
                'id': f'item-{i}',
                'name': f'Test Item {i}',
                'type': random.choice(item_types),
                'color': random.choice(colors),
                'imageUrl': f'https://example.com/image-{i}.jpg'
            }
            
            # Add fields based on completeness
            if completeness > 0.8:
                item.update({
                    'style': random.sample(styles, random.randint(1, 2)),
                    'occasion': random.sample(occasions, random.randint(1, 2)),
                    'season': random.sample(['spring', 'summer', 'fall', 'winter'], random.randint(1, 3)),
                    'dominantColors': [{'name': random.choice(colors), 'hex': '#000000'}],
                    'matchingColors': [{'name': random.choice(colors), 'hex': '#FFFFFF'}],
                    'description': f'A {item["color"]} {item["type"]} suitable for {random.choice(occasions)} occasions.',
                    'material': random.choice(['cotton', 'wool', 'silk', 'polyester']),
                    'fit': random.choice(['slim', 'regular', 'loose']),
                    'tags': [item['type'], item['color'], random.choice(styles)]
                })
            elif completeness > 0.6:
                item.update({
                    'style': [random.choice(styles)],
                    'occasion': [random.choice(occasions)],
                    'season': ['all-season'],
                    'dominantColors': [{'name': item['color'], 'hex': '#000000'}],
                    'description': f'A {item["color"]} {item["type"]}.'
                })
            elif completeness > 0.4:
                item.update({
                    'style': [random.choice(styles)],
                    'occasion': [random.choice(occasions)]
                })
            
            items.append(item)
        
        return items
    
    def create_sample_quiz_data(self, count: int) -> List[Dict]:
        """Create sample outfit quiz data for testing."""
        quiz_items = []
        
        for i in range(count):
            quiz_item = {
                'id': f'quiz-{i}',
                'outfit_id': f'outfit-{i}',
                'style_tags': ['casual', 'classic'],
                'occasion_tags': ['daily', 'work'],
                'color_harmony': 'neutral',
                'user_rating': random.randint(1, 5),
                'metadata': {
                    'generation_method': 'ai',
                    'confidence_score': random.uniform(0.7, 1.0),
                    'style_cluster': 'classic_casual'
                }
            }
            
            # Randomly introduce some data quality issues
            if random.random() < 0.1:  # 10% chance of issues
                quiz_item['style_tags'] = []  # Missing style tags
            elif random.random() < 0.05:  # 5% chance of other issues
                quiz_item['metadata']['confidence_score'] = None  # Missing confidence
            
            quiz_items.append(quiz_item)
        
        return quiz_items
    
    def has_field(self, item: Dict, field: str) -> bool:
        """Check if item has a specific field with a valid value."""
        if field not in item:
            return False
        
        value = item[field]
        if value is None:
            return False
        
        if isinstance(value, (list, dict)):
            return len(value) > 0
        
        if isinstance(value, str):
            return len(value.strip()) > 0
        
        return True
    
    def assess_description_quality(self, description: str) -> float:
        """Assess the quality of an item description."""
        if not description:
            return 0.0
        
        score = 0.5  # Base score
        
        # Length check
        if len(description) > 20:
            score += 0.2
        
        # Completeness check
        if any(word in description.lower() for word in ['color', 'style', 'occasion']):
            score += 0.2
        
        # Grammar check (simplified)
        if description[0].isupper() and description.endswith(('.', '!', '?')):
            score += 0.1
        
        return min(score, 1.0)
    
    def assess_image_quality(self, image_url: str) -> float:
        """Assess image quality (simplified)."""
        if not image_url:
            return 0.0
        
        score = 0.8  # Base score for valid URL
        
        # Check for common image quality indicators
        if any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png']):
            score += 0.1
        
        if 'high-res' in image_url.lower() or 'hd' in image_url.lower():
            score += 0.1
        
        return min(score, 1.0)
    
    def assess_quiz_data_integrity(self, quiz_item: Dict) -> float:
        """Assess the integrity of quiz data."""
        score = 1.0  # Start with perfect score
        
        # Check required fields
        required_fields = ['id', 'outfit_id', 'style_tags', 'occasion_tags']
        for field in required_fields:
            if not self.has_field(quiz_item, field):
                score -= 0.2
        
        # Check metadata
        if 'metadata' in quiz_item:
            metadata = quiz_item['metadata']
            if not self.has_field(metadata, 'confidence_score'):
                score -= 0.1
            if not self.has_field(metadata, 'style_cluster'):
                score -= 0.1
        
        return max(score, 0.0)
    
    def print_data_quality_summary(self):
        """Print data quality test summary."""
        print("\n" + "=" * 60)
        print("🧩 DATA QUALITY TESTING RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"   {status} {result.test_name}: {result.score:.1%}")
            
            if result.issues:
                print(f"      Issues: {len(result.issues)}")
                for issue in result.issues[:2]:  # Show first 2 issues
                    print(f"        • {issue}")
                if len(result.issues) > 2:
                    print(f"        • ... and {len(result.issues) - 2} more")
        
        # Collect all recommendations
        all_recommendations = []
        for result in self.test_results:
            all_recommendations.extend(result.recommendations)
        
        if all_recommendations:
            print(f"\n💡 Recommendations:")
            unique_recommendations = list(set(all_recommendations))
            for rec in unique_recommendations[:5]:  # Show top 5 recommendations
                print(f"   • {rec}")
        
        print("\n✅ Data quality testing completed!")

# Main execution
async def main():
    """Main function to run data quality testing."""
    validator = DataQualityValidator()
    await validator.run_data_quality_tests()

if __name__ == "__main__":
    asyncio.run(main()) 