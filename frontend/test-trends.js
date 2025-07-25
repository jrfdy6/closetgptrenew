// Simple test to verify real trends are being fetched
async function testTrendsAPI() {
  try {
    console.log('🧪 Testing Trends API...');
    
    // Test the frontend API route
    const response = await fetch('/api/wardrobe/trending-styles');
    const data = await response.json();
    
    console.log('📊 API Response:', data);
    
    if (data.success && data.data?.trending_styles) {
      console.log('✅ Real trends found!');
      console.log('📈 Number of trends:', data.data.trending_styles.length);
      console.log('🏆 Most popular trend:', data.data.most_popular?.name);
      
      // Show first few trends
      console.log('\n🎨 Top 5 Trending Styles:');
      data.data.trending_styles.slice(0, 5).forEach((trend, index) => {
        console.log(`${index + 1}. ${trend.name} (${trend.popularity}%)`);
        console.log(`   ${trend.description}`);
        console.log(`   Trend: ${trend.trend_direction}`);
        console.log('');
      });
    } else {
      console.log('❌ No real trends found or API error');
    }
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Run the test
testTrendsAPI(); 