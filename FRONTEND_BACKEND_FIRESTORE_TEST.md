# Frontend-Backend-Firestore Communication Test

This document explains how to test the complete communication flow between the frontend, backend, and Firestore database.

## Overview

The test verifies that:
1. Frontend can communicate with the backend API
2. Backend can process requests and communicate with Firestore
3. Data can be saved to and retrieved from Firestore through the backend

## Test Components

### 1. Frontend Test Page
**Location**: `frontend/src/app/test-firestore-communication/page.tsx`

This is a comprehensive test page that:
- Allows you to upload a test image
- Sends the image to the backend via API
- Creates a wardrobe item through the backend
- Verifies the item was saved by retrieving the wardrobe
- Shows detailed results for each step

### 2. Backend Test Script
**Location**: `backend/test_frontend_backend_communication.py`

This script tests:
- Backend health and responsiveness
- API endpoint availability
- Firebase configuration
- CORS configuration
- Authentication requirements

## How to Run the Tests

### Prerequisites

1. **Backend Server**: Make sure your backend is running
   ```bash
   cd backend
   python app.py
   # or
   uvicorn app:app --reload --port 3001
   ```

2. **Frontend Server**: Make sure your frontend is running
   ```bash
   cd frontend
   npm run dev
   ```

3. **Environment Variables**: Ensure these are set in your backend:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_PRIVATE_KEY_ID`
   - `FIREBASE_CLIENT_ID`
   - `FIREBASE_CLIENT_X509_CERT_URL`

4. **Frontend Environment**: Ensure these are set in your frontend:
   - `NEXT_PUBLIC_API_URL` (should point to your backend URL)

### Running the Backend Test

```bash
cd backend
python test_frontend_backend_communication.py
```

This will test:
- ✅ Backend health
- ✅ Simple endpoints
- ✅ Image upload endpoint
- ✅ Wardrobe endpoint
- ✅ Firebase connection
- ✅ CORS configuration

### Running the Frontend Test

1. Navigate to the test page in your browser:
   ```
   http://localhost:3000/test-firestore-communication
   ```

2. Upload a test image (any clothing item photo)

3. Configure the test item details:
   - Item Name: "Test Item"
   - Category: "shirt" (or any category)

4. Click "Run Communication Test"

The test will:
- ✅ Check backend health
- ✅ Verify authentication
- ✅ Upload image to backend
- ✅ Create wardrobe item
- ✅ Retrieve wardrobe to verify
- ✅ Show detailed results

## Expected Results

### Successful Test
If everything is working correctly, you should see:
- All steps marked with green checkmarks
- Success rate of 100%
- Detailed data for each step
- Confirmation that the item was saved to Firestore

### Common Issues

1. **Backend Not Running**
   - Error: "Backend is not responding"
   - Solution: Start the backend server

2. **Authentication Issues**
   - Error: "401 Unauthorized"
   - Solution: Ensure you're logged in to the frontend

3. **Firebase Configuration**
   - Error: "Firebase environment variables are missing"
   - Solution: Set up Firebase environment variables in backend

4. **CORS Issues**
   - Error: "CORS policy blocked"
   - Solution: Check CORS configuration in backend

5. **API URL Issues**
   - Error: "Failed to fetch"
   - Solution: Verify `NEXT_PUBLIC_API_URL` is set correctly

## Test Data

The test creates a sample wardrobe item with these properties:
```json
{
  "name": "Test Item",
  "category": "shirt",
  "color": "blue",
  "brand": "Test Brand",
  "description": "Test item created for communication testing",
  "season": "all",
  "occasion": ["casual", "test"],
  "material": "cotton"
}
```

## Troubleshooting

### Backend Issues
1. Check if the backend is running on the correct port
2. Verify Firebase credentials are properly set
3. Check backend logs for any errors

### Frontend Issues
1. Ensure you're logged in (authentication required)
2. Check browser console for any errors
3. Verify environment variables are set correctly

### Firestore Issues
1. Check Firebase project configuration
2. Verify service account has proper permissions
3. Check Firestore rules allow read/write operations

## Next Steps

After running these tests successfully:
1. The frontend can communicate with the backend
2. The backend can communicate with Firestore
3. You can proceed with full application development

If tests fail, address the specific issues before proceeding with development.
