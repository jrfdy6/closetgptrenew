# How to Get Your Firebase Token for Testing

## Method 1: Browser Console Script (Easiest)

1. **Go to your production site:** https://www.easyoutfitapp.com
2. **Make sure you're logged in**
3. **Open DevTools** (F12 or Right-click → Inspect)
4. **Go to Console tab**
5. **Copy and paste this entire code block:**

```javascript
(async function() {
  try {
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
    
    try {
      await navigator.clipboard.writeText(token);
      console.log('\n✅ Token copied to clipboard!');
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
```

6. **Press Enter** - The token will be displayed and copied to clipboard
7. **Run the test script** with the token

## Method 2: One-Liner (Simpler)

If the above doesn't work, try this simpler version:

```javascript
firebase.auth().currentUser?.getIdToken().then(token => console.log('TOKEN:', token))
```

Then manually copy the token from the console output.

## Method 3: Using the Helper Script

1. **Open the file:** `get-firebase-token.js`
2. **Copy its contents**
3. **Paste into browser console**
4. **Follow the instructions**

## Running the Test

Once you have the token:

```bash
# Option 1: Pass as argument
node test-outfit-performance.js "YOUR_TOKEN_HERE"

# Option 2: Set as environment variable
export FIREBASE_TOKEN="YOUR_TOKEN_HERE"
node test-outfit-performance.js
```

## Troubleshooting

### "Firebase not found"
- Make sure you're on https://www.easyoutfitapp.com
- Make sure the page is fully loaded
- Try refreshing the page

### "Not logged in"
- Sign in to your account first
- Check that you're authenticated

### Token expires
- Firebase tokens expire after 1 hour
- If tests fail with 401 errors, get a new token

### Syntax errors
- Make sure you copy the entire code block
- Don't break it across multiple lines
- Use the helper script file if needed

