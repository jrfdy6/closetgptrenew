/**
 * Simple script to get Firebase token from browser console
 * 
 * Copy and paste this entire block into your browser console on https://www.easyoutfitapp.com
 * (Make sure you're logged in first)
 */

(async function() {
  try {
    // Check if Firebase is available
    if (typeof firebase === 'undefined' || !firebase.auth) {
      console.error('❌ Firebase not found. Make sure you\'re on the Easy Outfit App website.');
      return;
    }

    const user = firebase.auth().currentUser;
    
    if (!user) {
      console.error('❌ Not logged in. Please sign in first.');
      return;
    }

    console.log('✅ User found:', user.email);
    console.log('🔄 Getting ID token...');
    
    const token = await user.getIdToken();
    
    console.log('\n✅ TOKEN RETRIEVED:');
    console.log('='.repeat(80));
    console.log(token);
    console.log('='.repeat(80));
    
    // Try to copy to clipboard
    try {
      await navigator.clipboard.writeText(token);
      console.log('\n✅ Token copied to clipboard!');
      console.log('📋 You can now paste it into the test script.');
    } catch (clipboardError) {
      console.log('\n⚠️  Could not copy to clipboard automatically.');
      console.log('📋 Please manually copy the token above.');
    }
    
    console.log('\n💡 To run the test script:');
    console.log(`   node test-outfit-performance.js "${token}"`);
    
  } catch (error) {
    console.error('❌ Error getting token:', error);
  }
})();

