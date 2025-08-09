# Live Route Testing Suite

This testing suite validates the three main API endpoints post-deployment to ensure your ClosetGPT application is working correctly.

## 🎯 Test Coverage

### 1. `/api/process-image` - Image Upload & Analysis
- ✅ Uploads an image file
- ✅ Processes and analyzes clothing metadata
- ✅ Generates CLIP embeddings
- ✅ Saves to Firestore with clean metadata
- ✅ Returns structured clothing item data

### 2. `/api/generate-outfit` - Outfit Generation
- ✅ Generates outfits from wardrobe items
- ✅ Handles user preferences and weather
- ✅ Validates outfit combinations
- ✅ Returns complete outfit with reasoning

### 3. `/api/delete-photo` - Photo Deletion & Sync
- ✅ Deletes photos from Firebase Storage
- ✅ Syncs deletion with Firestore
- ✅ Verifies cleanup across services

## 🚀 Quick Start

### Prerequisites
1. **Node.js** (v16 or higher)
2. **Firebase Admin SDK** credentials
3. **Test image** (included: `frontend/test-images/test-shirt.jpg`)

### Installation

```bash
# Install testing dependencies
npm install form-data node-fetch firebase-admin

# Or use the test package.json
cp test-package.json package.json
npm install
```

### Environment Setup

1. **Set up Firebase Admin credentials:**
   ```bash
   # Option 1: Use service account key
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/serviceAccountKey.json"
   
   # Option 2: Use Firebase CLI
   firebase login
   firebase projects:list
   ```

2. **Configure URLs:**
   ```bash
   export FRONTEND_URL="http://localhost:3000"  # or your deployed frontend URL
   export NEXT_PUBLIC_BACKEND_URL="https://closetgptrenew-backend-production.up.railway.app"
   ```

### Authentication Setup

The tests require authentication tokens. You have several options:

#### Option 1: Use Auth Helper (Recommended)
```bash
# Create a test user
node auth_helper.js create-user test@closetgpt.com

# Generate a test token
node auth_helper.js generate-token test-user-123
```

#### Option 2: Manual Token Generation
1. Sign in to your app manually
2. Get the Firebase ID token from browser dev tools
3. Use that token in the tests

#### Option 3: Use Existing User
If you have an existing user, you can use their token directly.

## 🧪 Running Tests

### Run All Tests
```bash
npm test
# or
node test_live_routes.js
```

### Run Individual Tests
```bash
# Test image processing only
npm run test:process-image

# Test outfit generation only
npm run test:generate-outfit

# Test photo deletion only
npm run test:delete-photo
```

### Test Output Example
```
============================================================
  LIVE ROUTE TESTING SUITE
============================================================
Testing deployed API endpoints...

============================================================
  TEST 1: /api/process-image - Upload and Analyze Image
============================================================
✅ Image File Check: PASS
   Test image found
📤 Uploading image for processing...
✅ API Response Status: PASS
   Status: 200
✅ Response Structure: PASS
   All required fields present
✅ Clothing Item Data: PASS
   All item fields present
📋 Generated Metadata:
   ID: abc123
   Name: Blue T-Shirt
   Type: shirt
   Colors: 3 colors detected
   Styles: 2 styles identified
   Occasions: 3 occasions identified
✅ CLIP Embedding: PASS
   Embedding vector length: 512

============================================================
  TEST 2: /api/generate-outfit - Generate Outfit from Wardrobe
============================================================
🎨 Generating outfit...
✅ API Response Status: PASS
   Status: 200
✅ Response Structure: PASS
   All required fields present
✅ Outfit Items: PASS
   2 items generated
👕 Generated Outfit:
   ID: outfit-456
   Name: Casual Blue Outfit
   Occasion: casual
   Style: casual
   Items: 2
   1. Blue T-Shirt (shirt)
   2. Black Jeans (pants)
✅ Generation Success: PASS
   Outfit generated successfully

============================================================
  TEST 3: /api/delete-photo - Delete Photo and Sync Storage
============================================================
📤 Uploading test photo for deletion...
✅ Photo Upload for Deletion: PASS
   Photo uploaded successfully
   Photo URL: https://storage.googleapis.com/...
🗑️  Deleting uploaded photo...
✅ Delete API Response: PASS
   Status: 204
🔍 Verifying photo deletion...
✅ Photo Deletion Verification: PASS
   Photo successfully deleted from storage
📊 Checking Firestore sync...
✅ Firestore Sync: PASS
   Photo deletion completed successfully

============================================================
  TEST RESULTS SUMMARY
============================================================
✅ Process Image API: PASS
✅ Generate Outfit API: PASS
✅ Delete Photo API: PASS

📊 Overall Results: 3/3 tests passed
🎉 All tests passed! Your deployment is working correctly.
```

## 🔧 Configuration

### Test Configuration
Edit `test_live_routes.js` to customize:

```javascript
// URLs
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';

// Test data
const TEST_IMAGE_PATH = path.join(__dirname, 'frontend/test-images/test-shirt.jpg');
const TEST_USER_ID = 'test-user-123';
```

### Mock Data
The tests use mock data for wardrobe items and user profiles. You can modify these in the test functions:

```javascript
const mockWardrobe = [
  {
    id: 'item-1',
    name: 'Blue T-Shirt',
    type: 'shirt',
    // ... more properties
  }
];
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
❌ Authentication: FAIL
   Valid auth token required
```
**Solution:** Set up Firebase Admin credentials and generate a valid token.

#### 2. Image File Not Found
```
❌ Image File Check: FAIL
   Test image not found
```
**Solution:** Ensure `frontend/test-images/test-shirt.jpg` exists.

#### 3. API Endpoint Not Found
```
❌ API Response Status: FAIL
   Status: 404
```
**Solution:** Check that your frontend is running and the API routes are deployed.

#### 4. CORS Errors
```
❌ Process Image Test: FAIL
   CORS policy error
```
**Solution:** Ensure CORS is properly configured in your backend.

### Debug Mode
Enable detailed logging by setting:
```bash
export DEBUG=true
```

### Manual Testing
If automated tests fail, you can test manually:

1. **Process Image:**
   ```bash
   curl -X POST http://localhost:3000/api/process-image \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@frontend/test-images/test-shirt.jpg" \
     -F "userId=test-user-123"
   ```

2. **Generate Outfit:**
   ```bash
   curl -X POST http://localhost:3000/api/outfit/generate \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"occasion":"casual","wardrobe":[...]}'
   ```

3. **Delete Photo:**
   ```bash
   curl -X DELETE "http://localhost:3000/api/delete-photo?url=PHOTO_URL&type=outfit" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## 📊 Test Results Interpretation

### Pass Criteria
- ✅ **API Response Status:** 200/201/204
- ✅ **Response Structure:** All required fields present
- ✅ **Data Validation:** Valid data format and content
- ✅ **Error Handling:** Proper error responses

### Warning Indicators
- ⚠️ **CLIP Embedding:** Missing but not critical
- ⚠️ **Validation Errors:** Minor issues in outfit generation
- ⚠️ **Performance:** Slow response times

### Failure Indicators
- ❌ **Authentication:** Invalid or missing tokens
- ❌ **File Operations:** Missing files or upload failures
- ❌ **Database Sync:** Firestore/Storage sync issues
- ❌ **API Errors:** 4xx/5xx status codes

## 🔄 Continuous Testing

### GitHub Actions Integration
Add this to your `.github/workflows/test.yml`:

```yaml
name: Live Route Testing
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '16'
      - run: npm install
      - run: npm test
        env:
          FRONTEND_URL: ${{ secrets.FRONTEND_URL }}
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}
```

### Pre-deployment Testing
Run tests before deploying:
```bash
# In your deployment pipeline
npm test
if [ $? -eq 0 ]; then
  echo "✅ All tests passed, proceeding with deployment"
  # deploy
else
  echo "❌ Tests failed, aborting deployment"
  exit 1
fi
```

## 📝 Customization

### Adding New Tests
1. Create a new test function in `test_live_routes.js`
2. Add it to the `runAllTests()` function
3. Update the results object

### Testing Different Scenarios
- **Empty Wardrobe:** Test with no items
- **Large Wardrobe:** Test with many items
- **Invalid Data:** Test error handling
- **Performance:** Test response times

### Environment-Specific Tests
Create environment-specific test files:
- `test_production.js` - Production-specific tests
- `test_staging.js` - Staging-specific tests
- `test_local.js` - Local development tests

## 🤝 Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Include proper error handling
3. Add detailed logging
4. Update this README
5. Test across different environments

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the error logs
3. Test manually to isolate the issue
4. Check your deployment configuration
5. Verify Firebase credentials and permissions 