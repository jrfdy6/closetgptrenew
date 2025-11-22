/**
 * Production Payment System Test Script
 * Tests payment and subscription endpoints in production
 * 
 * Usage:
 *   1. Open browser console on your app (https://easyoutfitapp.com)
 *   2. Get your Firebase token: await firebase.auth().currentUser.getIdToken()
 *   3. Copy the token
 *   4. Run: node test_payment_system.js YOUR_TOKEN
 */

const PROD_URL = 'https://closetgptrenew-production.up.railway.app';
const API_URL = `${PROD_URL}/api`;

const token = process.argv[2] || 'test';

console.log('🧪 Testing Payment System in Production');
console.log('========================================');
console.log(`Production URL: ${PROD_URL}\n`);

if (token === 'test') {
  console.log('⚠️  Using test token. For real tests, pass your Firebase token:');
  console.log('   node test_payment_system.js YOUR_FIREBASE_TOKEN\n');
}

// Test 1: Health Check
async function testHealthCheck() {
  console.log('1️⃣  Testing Health Check...');
  console.log('------------------------');
  try {
    const response = await fetch(`${PROD_URL}/health`);
    const data = await response.json();
    console.log('✅ Health check:', JSON.stringify(data, null, 2));
  } catch (error) {
    console.log('❌ Health check failed:', error.message);
  }
  console.log('\n');
}

// Test 2: Current Subscription
async function testCurrentSubscription() {
  console.log('2️⃣  Testing Current Subscription Endpoint...');
  console.log('--------------------------------------------');
  try {
    const response = await fetch(`${API_URL}/payments/subscription/current`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    console.log(`HTTP Status: ${response.status}`);
    console.log('Response:', JSON.stringify(data, null, 2));
    
    if (response.ok) {
      console.log('✅ Subscription endpoint working!');
      console.log(`   Current role: ${data.role || 'unknown'}`);
      console.log(`   Status: ${data.status || 'unknown'}`);
      console.log(`   Flatlays remaining: ${data.flatlays_remaining || 0}`);
    } else {
      console.log('❌ Subscription endpoint failed');
    }
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
  console.log('\n');
}

// Test 3: Style Persona Analysis (Should Require Pro/Premium)
async function testStylePersonaPaywall() {
  console.log('3️⃣  Testing Style Persona Analysis (Should Require Pro/Premium)...');
  console.log('-------------------------------------------------------------------');
  
  // Create a minimal test image (1x1 pixel PNG in base64)
  const testImageBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
  const imageBlob = await fetch(`data:image/png;base64,${testImageBase64}`).then(r => r.blob());
  
  try {
    const formData = new FormData();
    formData.append('file', imageBlob, 'test.png');
    
    const response = await fetch(`${API_URL}/style-analysis/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const data = await response.json();
    console.log(`HTTP Status: ${response.status}`);
    console.log('Response:', JSON.stringify(data, null, 2));
    
    if (response.status === 403) {
      console.log('✅ Paywall working! Style analysis correctly requires Pro/Premium');
    } else if (response.ok) {
      console.log('⚠️  Style analysis accessible - user might already have Pro/Premium');
    } else {
      console.log('❌ Unexpected response');
    }
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
  console.log('\n');
}

// Test 4: Check Feature Access
async function testFeatureAccess() {
  console.log('4️⃣  Testing Feature Access...');
  console.log('------------------------------');
  try {
    const response = await fetch(`${API_URL}/payments/subscription/current`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      const role = data.role || 'tier1';
      console.log(`   User role: ${role}`);
      
      if (role === 'tier2' || role === 'tier3') {
        console.log('✅ User has Pro/Premium - should have access to premium features');
      } else {
        console.log('⚠️  User has Free tier - premium features should be blocked');
      }
    }
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
  console.log('\n');
}

// Test 5: Payment Routes Registration
async function testPaymentRoutes() {
  console.log('5️⃣  Testing Payment Routes Registration...');
  console.log('------------------------------------------');
  try {
    const response = await fetch(`${API_URL}/payments/subscription/current`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status !== 404) {
      console.log('✅ Payment routes are registered and accessible');
    } else {
      console.log('❌ Payment routes not found - check if deployed');
    }
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
  console.log('\n');
}

// Test 6: Stripe Configuration
async function testStripeConfig() {
  console.log('6️⃣  Testing Stripe Configuration...');
  console.log('-----------------------------------');
  try {
    const response = await fetch(`${API_URL}/payments/checkout/create-session`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ role: 'tier2' })
    });
    
    const data = await response.json();
    console.log(`HTTP Status: ${response.status}`);
    console.log('Response:', JSON.stringify(data, null, 2));
    
    if (response.status === 503) {
      console.log('⚠️  Stripe not configured yet - this is expected');
      console.log('   Need to set STRIPE_SECRET_KEY environment variable');
    } else if (response.ok) {
      console.log('✅ Stripe is configured and working!');
    } else {
      console.log('⚠️  Unexpected response - check configuration');
    }
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
  console.log('\n');
}

// Run all tests
async function runAllTests() {
  await testHealthCheck();
  await testCurrentSubscription();
  await testStylePersonaPaywall();
  await testFeatureAccess();
  await testPaymentRoutes();
  await testStripeConfig();
  
  console.log('========================================');
  console.log('✅ Test Summary Complete\n');
  console.log('Next Steps:');
  console.log('1. Set up Stripe (see STRIPE_SETUP.md)');
  console.log('2. Configure environment variables in Railway');
  console.log('3. Test with real Stripe checkout');
}

runAllTests().catch(console.error);

