# Wardrobe Item Upload Testing Guide

This guide will help you test the complete wardrobe item upload process, from frontend upload through AI analysis to Firestore storage.

## Testing Overview

We will test:
1. ✅ Frontend image upload process
2. ✅ AI analysis metadata generation
3. ✅ Wardrobe item page displays correct metadata
4. ✅ Firestore storage contains all required fields

---

## Step 1: Frontend Upload Testing

### Access the Upload Interface

1. **Start your development server** (if not already running):
   ```bash
   cd /Users/johnniefields/Desktop/Cursor/closetgptrenew
   cd frontend && npm run dev
   ```

2. **Navigate to the Wardrobe page**:
   - Go to: https://my-app.vercel.app/wardrobe
   - Or locally: http://localhost:3000/wardrobe

3. **Open the Batch Upload Modal**:
   - Click the **"Upload"** button or **"Batch Upload with AI"** button

### Upload a Test Image

1. **Select an image**:
   - Drag and drop a clothing item image
   - Or click to browse and select an image
   - Supported formats: JPG, PNG, GIF, WebP (max 10MB)

2. **Verify duplicate detection** (if applicable):
   - The system will check if the item already exists
   - Duplicates will be marked with an orange "Already exists" badge
   - Non-duplicates will show as "pending"

3. **Start the upload**:
   - Click **"Upload All with AI"** button
   - Watch the progress:
     - 🔄 "Uploading" - Uploading to Firebase Storage
     - 🧠 "Analyzing" - AI analyzing the image
     - ✅ "Success" - Item saved successfully

4. **Check for success message**:
   - You should see a toast notification: **"Batch upload completed! ✨"**
   - The message will show how many items were uploaded

---

## Step 2: Verify Metadata on Wardrobe Item Page

### View the Uploaded Item

1. **Navigate back to the wardrobe**:
   - The page should automatically refresh
   - Or click the wardrobe tab if still on the page

2. **Find your uploaded item**:
   - It should appear in the wardrobe grid
   - Look for the item you just uploaded

3. **Click on the item** to open details modal

### Check Displayed Metadata

The **WardrobeItemDetails** modal should display the following metadata:

#### Basic Information:
- ✅ **Name**: AI-generated name (e.g., "Navy Blue T-Shirt")
- ✅ **Type**: Clothing type (e.g., shirt, pants, dress, jacket)
- ✅ **Color**: Primary color detected by AI
- ✅ **Brand**: If detected (may be empty)
- ✅ **Description**: AI-generated description

#### Style Attributes:
- ✅ **Styles**: Tags like casual, formal, sporty, elegant, etc.
- ✅ **Seasons**: Spring, summer, fall, winter, all-season
- ✅ **Occasions**: Everyday, work, party, athletic, formal, etc.

#### Visual Attributes (if detected):
- ✅ **Materials**: Cotton, denim, leather, polyester, etc.
- ✅ **Sleeve Length**: Short, long, sleeveless, three-quarter
- ✅ **Fit**: Slim, regular, loose, oversized
- ✅ **Neckline**: Crew-neck, v-neck, button-down, etc.
- ✅ **Length**: Regular, crop, long, short

#### Advanced Metadata (visible in data structure):
- ✅ **Dominant Colors**: Array of colors with hex codes
- ✅ **Matching Colors**: Recommended color combinations
- ✅ **Sub Type**: Specific category (e.g., "polo" for shirts)

#### Usage Tracking:
- ✅ **Wear Count**: Starts at 0
- ✅ **Last Worn**: Initially null
- ✅ **Favorite**: Default false

### Test Editing

1. **Click "Edit" button** in the modal
2. **Verify all fields are editable**:
   - Text fields (name, brand, description)
   - Dropdowns (type, color, fit, neckline, etc.)
   - Multi-select badges (styles, seasons, occasions, materials)
3. **Make a change** and click **"Save"**
4. **Verify the change persists** after closing and reopening

---

## Step 3: Verify Firestore Storage

### Option A: Use the Backend Debug Endpoint

1. **Get your Firebase Auth token**:
   - Open browser DevTools (F12)
   - Go to Application/Storage → Local Storage
   - Copy your Firebase auth token

2. **Call the debug endpoint**:
   ```bash
   curl -X GET \
     https://closetgptrenew-backend-production.up.railway.app/api/wardrobe/ \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN_HERE"
   ```

3. **Check the response** for your uploaded item
   - Look for the item by name or timestamp
   - Verify all metadata fields are present

### Option B: Use Firebase Console

1. **Open Firebase Console**:
   - Go to: https://console.firebase.google.com
   - Select your project

2. **Navigate to Firestore Database**:
   - Click "Firestore Database" in the left sidebar
   - Find the `wardrobe` collection
   - Look for your user ID (starts with `dANq...` or similar)

3. **Find your uploaded item**:
   - Sort by `createdAt` (newest first)
   - Or search by item name

4. **Verify the following fields exist**:

#### Required Fields:
```json
{
  "id": "item-1234567890",
  "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
  "name": "Navy Blue T-Shirt",
  "type": "t-shirt",
  "color": "blue",
  "imageUrl": "https://firebasestorage.googleapis.com/...",
  "createdAt": "2025-10-09T12:00:00.000Z",
  
  // AI Analysis Data
  "analysis": {
    "name": "Navy Blue T-Shirt",
    "type": "t-shirt",
    "subType": "casual-tee",
    "dominantColors": [
      { "name": "navy", "hex": "#001f3f", "percentage": 85 }
    ],
    "matchingColors": [
      { "name": "white", "hex": "#FFFFFF" },
      { "name": "khaki", "hex": "#C3B091" }
    ],
    "style": ["casual", "everyday"],
    "season": ["spring", "summer", "fall"],
    "occasion": ["everyday", "casual"],
    "metadata": {
      "visualAttributes": {
        "material": "cotton",
        "pattern": "solid",
        "fit": "regular",
        "sleeveLength": "short"
      }
    }
  },
  
  // Additional Metadata
  "brand": "",
  "style": ["casual", "everyday"],
  "material": "cotton",
  "season": ["spring", "summer", "fall"],
  "occasion": ["everyday", "casual"],
  "subType": "casual-tee",
  "gender": "unisex",
  
  // Duplicate Detection Fields
  "imageHash": "abc123...def456",
  "metadata": {
    "width": 800,
    "height": 1200,
    "aspectRatio": 0.6667,
    "fileSize": 524288,
    "type": "image/jpeg"
  },
  "fileSize": 524288,
  
  // Usage Tracking
  "backgroundRemoved": false,
  "favorite": false,
  "wearCount": 0,
  "lastWorn": null
}
```

### Option C: Create a Test Script

Run the provided test script to check Firestore data:

```bash
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew
node test_check_firebase_metadata.js
```

This will:
- ✅ Connect to Firestore
- ✅ Fetch recent wardrobe items
- ✅ Check for required metadata fields
- ✅ Report any missing fields
- ✅ Show sample data structure

---

## Expected Results

### ✅ Success Criteria

1. **Upload completes without errors**
   - No error toasts or console errors
   - Item appears in wardrobe grid

2. **AI Analysis generates comprehensive metadata**:
   - Name is descriptive and accurate
   - Type is correctly identified
   - Colors are accurate
   - Styles, seasons, and occasions are relevant
   - Visual attributes (material, fit, etc.) are detected

3. **Wardrobe item page displays all metadata**:
   - All fields are populated (or show as empty if not detected)
   - Images load correctly
   - Edit functionality works

4. **Firestore contains complete data**:
   - All required fields are present
   - Nested structures (analysis, metadata) are intact
   - No null/undefined values where not expected
   - Duplicate detection fields are populated

---

## Troubleshooting

### Upload Fails
- **Check browser console** for errors
- **Verify Firebase Storage** is configured
- **Check backend logs** for API errors
- **Ensure image file** is valid and under 10MB

### Metadata Missing
- **Check AI analysis response** in browser DevTools → Network tab
- **Look for `/analyze-image` request** and response
- **Verify OpenAI API** is working (check backend logs)
- **Check if analysis field** exists in the response

### Item Not Saved to Firestore
- **Check browser console** for POST errors
- **Verify authentication** token is valid
- **Check backend logs** for `/api/wardrobe/add` errors
- **Ensure user permissions** are correct in Firestore

### Metadata Not Displayed
- **Verify WardrobeItemDetails component** is receiving the item
- **Check browser console** for render errors
- **Inspect item data structure** in React DevTools
- **Ensure normalization** is not removing fields

---

## Quick Verification Checklist

- [ ] Image uploads successfully
- [ ] AI analysis completes (no errors in console)
- [ ] Item appears in wardrobe grid
- [ ] Item details modal opens when clicked
- [ ] Name, type, and color are displayed
- [ ] Style tags are visible
- [ ] Season tags are visible
- [ ] Occasion tags are visible
- [ ] Material is shown (if detected)
- [ ] Visual attributes present (fit, sleeve length, etc.)
- [ ] Image loads in detail view
- [ ] Edit button works
- [ ] Changes save successfully
- [ ] Firestore contains all required fields
- [ ] Duplicate detection fields present
- [ ] Analysis metadata is nested correctly

---

## Next Steps After Testing

If all tests pass:
1. ✅ **Mark the feature as working**
2. ✅ **Test with multiple item types** (shirts, pants, dresses, shoes, etc.)
3. ✅ **Test edge cases** (unusual colors, patterns, materials)
4. ✅ **Test duplicate detection** with same image
5. ✅ **Test batch upload** with multiple items

If any tests fail:
1. 🔍 **Document the specific failure**
2. 🔍 **Check logs** (browser console + backend)
3. 🔍 **Provide error messages** for debugging
4. 🔍 **Test with different images** to isolate the issue

---

## Contact & Support

If you encounter issues:
1. Check browser console for errors
2. Check backend logs on Railway
3. Verify Firebase configuration
4. Provide specific error messages for debugging

