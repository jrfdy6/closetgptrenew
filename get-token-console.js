/**
 * Copy and paste this into your browser console on https://www.easyoutfitapp.com
 * Make sure you're logged in first!
 */

(async function() {
  try {
    // Method 1: Try to access Firebase from the page's context
    // Check if window has Firebase initialized
    if (window.__NEXT_DATA__) {
      console.log('✅ Next.js detected');
    }

    // Try to get auth from the page's Firebase instance
    // Since the page uses Firebase v9 modular, we need to access it differently
    
    // Check localStorage for auth state
    const authState = localStorage.getItem('firebase:authUser:' + process.env.NEXT_PUBLIC_FIREBASE_API_KEY?.split(':')[0] + ':[DEFAULT]');
    
    if (authState) {
      console.log('✅ Found auth state in localStorage');
      const authData = JSON.parse(authState);
      console.log('User:', authData.email);
    }

    // Alternative: Use the browser's fetch to call an API that returns the token
    // But we need the user to be authenticated first
    
    console.log('\n📋 INSTRUCTIONS:');
    console.log('1. Make sure you\'re logged in');
    console.log('2. Open DevTools → Application → Local Storage');
    console.log('3. Look for Firebase auth keys');
    console.log('4. OR use the debug token page: https://www.easyoutfitapp.com/debug-token');
    console.log('\n💡 EASIEST: Just visit /debug-token page and click the button!');
    
    // Try to redirect to debug page
    if (confirm('Would you like to go to the debug token page?')) {
      window.location.href = '/debug-token';
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
    console.log('\n💡 Just visit: https://www.easyoutfitapp.com/debug-token');
  }
})();

