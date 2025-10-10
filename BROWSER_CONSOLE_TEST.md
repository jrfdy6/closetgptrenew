# Browser Console Testing Scripts

Use these scripts in your browser console to quickly verify wardrobe uploads.

## How to Use

1. Open your browser's developer tools (F12)
2. Go to the **Console** tab
3. Copy and paste the script
4. Press Enter to run

---

## Script 1: Check Latest Uploaded Item

This script fetches and displays the metadata of your most recently uploaded item.

```javascript
// Fetch latest uploaded item
(async function checkLatestUpload() {
  console.log('🔍 Fetching latest uploaded item...\n');
  
  try {
    // Get auth token from Firebase
    const user = firebase.auth().currentUser;
    if (!user) {
      console.error('❌ Not logged in');
      return;
    }
    
    const token = await user.getIdToken();
    
    // Fetch wardrobe items
    const response = await fetch('/api/wardrobe', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      console.error('❌ Failed to fetch wardrobe:', response.statusText);
      return;
    }
    
    const data = await response.json();
    const items = data.items || [];
    
    if (items.length === 0) {
      console.log('⚠️  No items found in wardrobe');
      return;
    }
    
    // Sort by createdAt (most recent first)
    const sortedItems = items.sort((a, b) => 
      new Date(b.createdAt) - new Date(a.createdAt)
    );
    
    const latestItem = sortedItems[0];
    
    console.log('✅ Latest Uploaded Item:');
    console.log('═══════════════════════════════════════\n');
    console.log('📦 Basic Info:');
    console.log(`   Name: ${latestItem.name}`);
    console.log(`   Type: ${latestItem.type}`);
    console.log(`   Color: ${latestItem.color}`);
    console.log(`   Brand: ${latestItem.brand || 'N/A'}`);
    console.log(`   Created: ${latestItem.createdAt}`);
    
    console.log('\n🎨 AI Analysis:');
    if (latestItem.analysis) {
      console.log(`   ✅ Analysis data present`);
      console.log(`   Dominant Colors:`, latestItem.analysis.dominantColors);
      console.log(`   Matching Colors:`, latestItem.analysis.matchingColors);
      console.log(`   Sub Type: ${latestItem.analysis.subType || 'N/A'}`);
      
      if (latestItem.analysis.metadata?.visualAttributes) {
        const va = latestItem.analysis.metadata.visualAttributes;
        console.log('\n   Visual Attributes:');
        console.log(`     Material: ${va.material || 'N/A'}`);
        console.log(`     Pattern: ${va.pattern || 'N/A'}`);
        console.log(`     Fit: ${va.fit || 'N/A'}`);
        console.log(`     Sleeve Length: ${va.sleeveLength || 'N/A'}`);
      }
    } else {
      console.log(`   ❌ No analysis data`);
    }
    
    console.log('\n👔 Style Attributes:');
    console.log(`   Styles: ${latestItem.style?.join(', ') || 'N/A'}`);
    console.log(`   Seasons: ${latestItem.season?.join(', ') || 'N/A'}`);
    console.log(`   Occasions: ${latestItem.occasion?.join(', ') || 'N/A'}`);
    console.log(`   Material: ${latestItem.material || 'N/A'}`);
    
    console.log('\n🔍 Duplicate Detection:');
    console.log(`   Image Hash: ${latestItem.imageHash ? '✅ Present' : '❌ Missing'}`);
    console.log(`   File Size: ${latestItem.fileSize ? `${(latestItem.fileSize / 1024).toFixed(2)} KB` : '❌ Missing'}`);
    if (latestItem.metadata) {
      console.log(`   Dimensions: ${latestItem.metadata.width}x${latestItem.metadata.height}`);
      console.log(`   Aspect Ratio: ${latestItem.metadata.aspectRatio}`);
    }
    
    console.log('\n📊 Usage Tracking:');
    console.log(`   Favorite: ${latestItem.favorite ? '❤️ Yes' : 'No'}`);
    console.log(`   Wear Count: ${latestItem.wearCount || 0}`);
    console.log(`   Last Worn: ${latestItem.lastWorn || 'Never'}`);
    
    console.log('\n═══════════════════════════════════════');
    console.log('\n📄 Full JSON:');
    console.log(JSON.stringify(latestItem, null, 2));
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
})();
```

---

## Script 2: Verify All Required Fields

This script checks if all required fields are present in your wardrobe items.

```javascript
// Verify all required fields
(async function verifyRequiredFields() {
  console.log('🔍 Verifying required fields in wardrobe items...\n');
  
  const REQUIRED_FIELDS = [
    'id', 'userId', 'name', 'type', 'color', 'imageUrl', 'createdAt'
  ];
  
  const EXPECTED_FIELDS = [
    'analysis', 'style', 'season', 'occasion', 'imageHash', 'metadata'
  ];
  
  try {
    const user = firebase.auth().currentUser;
    if (!user) {
      console.error('❌ Not logged in');
      return;
    }
    
    const token = await user.getIdToken();
    const response = await fetch('/api/wardrobe', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      console.error('❌ Failed to fetch wardrobe');
      return;
    }
    
    const data = await response.json();
    const items = data.items || [];
    
    console.log(`📦 Checking ${items.length} items...\n`);
    
    let successCount = 0;
    let warningCount = 0;
    let errorCount = 0;
    
    items.forEach((item, index) => {
      const missing = REQUIRED_FIELDS.filter(field => !item[field]);
      const missingExpected = EXPECTED_FIELDS.filter(field => !item[field]);
      
      if (missing.length === 0) {
        successCount++;
        if (missingExpected.length === 0) {
          console.log(`✅ Item ${index + 1}: ${item.name} - All fields present`);
        } else {
          warningCount++;
          console.log(`⚠️  Item ${index + 1}: ${item.name} - Missing optional: ${missingExpected.join(', ')}`);
        }
      } else {
        errorCount++;
        console.log(`❌ Item ${index + 1}: ${item.name} - Missing required: ${missing.join(', ')}`);
      }
    });
    
    console.log('\n═══════════════════════════════════════');
    console.log('📊 Summary:');
    console.log(`   ✅ Complete: ${successCount}`);
    console.log(`   ⚠️  Warnings: ${warningCount}`);
    console.log(`   ❌ Errors: ${errorCount}`);
    console.log(`   📦 Total: ${items.length}`);
    console.log('═══════════════════════════════════════\n');
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
})();
```

---

## Script 3: Compare Upload Before/After

Run this BEFORE uploading to capture the current state:

```javascript
// STEP 1: Run BEFORE upload
window.itemCountBefore = null;

(async function captureBeforeUpload() {
  try {
    const user = firebase.auth().currentUser;
    const token = await user.getIdToken();
    const response = await fetch('/api/wardrobe', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    window.itemCountBefore = data.items?.length || 0;
    console.log(`📸 Captured: ${window.itemCountBefore} items in wardrobe`);
    console.log('✅ Ready for upload! Upload your item now, then run the "after" script.');
  } catch (error) {
    console.error('❌ Error:', error);
  }
})();
```

Run this AFTER uploading to see what changed:

```javascript
// STEP 2: Run AFTER upload
(async function verifyAfterUpload() {
  if (!window.itemCountBefore) {
    console.error('❌ Please run the "before" script first!');
    return;
  }
  
  try {
    const user = firebase.auth().currentUser;
    const token = await user.getIdToken();
    const response = await fetch('/api/wardrobe', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    const itemCountAfter = data.items?.length || 0;
    const newItemsCount = itemCountAfter - window.itemCountBefore;
    
    console.log('\n═══════════════════════════════════════');
    console.log('📊 Upload Verification:');
    console.log(`   Before: ${window.itemCountBefore} items`);
    console.log(`   After: ${itemCountAfter} items`);
    console.log(`   New items: ${newItemsCount}`);
    
    if (newItemsCount > 0) {
      console.log('\n✅ Upload successful!');
      
      // Show the new items
      const sortedItems = data.items.sort((a, b) => 
        new Date(b.createdAt) - new Date(a.createdAt)
      );
      const newItems = sortedItems.slice(0, newItemsCount);
      
      console.log('\n📦 New Items:');
      newItems.forEach((item, index) => {
        console.log(`   ${index + 1}. ${item.name} (${item.type}, ${item.color})`);
      });
    } else {
      console.log('\n⚠️  No new items detected. Check if upload failed or items were marked as duplicates.');
    }
    console.log('═══════════════════════════════════════\n');
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
})();
```

---

## Script 4: Check Specific Item by Name

```javascript
// Find and check specific item
(async function checkItemByName() {
  const itemName = prompt('Enter item name to search for:');
  if (!itemName) return;
  
  try {
    const user = firebase.auth().currentUser;
    const token = await user.getIdToken();
    const response = await fetch('/api/wardrobe', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    const items = data.items || [];
    
    const matchingItems = items.filter(item => 
      item.name.toLowerCase().includes(itemName.toLowerCase())
    );
    
    if (matchingItems.length === 0) {
      console.log(`⚠️  No items found matching "${itemName}"`);
      return;
    }
    
    console.log(`✅ Found ${matchingItems.length} matching item(s):\n`);
    matchingItems.forEach((item, index) => {
      console.log(`\n${index + 1}. ${item.name}`);
      console.log(`   Type: ${item.type}`);
      console.log(`   Color: ${item.color}`);
      console.log(`   Created: ${item.createdAt}`);
      console.log(`   Has Analysis: ${item.analysis ? '✅' : '❌'}`);
      console.log(`   Has Metadata: ${item.metadata ? '✅' : '❌'}`);
      console.log(`   Image Hash: ${item.imageHash ? '✅' : '❌'}`);
    });
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
})();
```

---

## Quick Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **Script 1** | Check latest item | After uploading to verify metadata |
| **Script 2** | Verify all fields | To audit entire wardrobe |
| **Script 3** | Before/After | To track upload in real-time |
| **Script 4** | Search by name | To find specific items |

---

## Expected Output

### Successful Upload
```
✅ Latest Uploaded Item:
═══════════════════════════════════════

📦 Basic Info:
   Name: Navy Blue Polo Shirt
   Type: polo
   Color: navy
   Brand: Ralph Lauren
   Created: 2025-10-09T12:00:00.000Z

🎨 AI Analysis:
   ✅ Analysis data present
   Dominant Colors: [...]
   Matching Colors: [...]
   
   Visual Attributes:
     Material: cotton
     Pattern: solid
     Fit: regular
     Sleeve Length: short

👔 Style Attributes:
   Styles: casual, preppy
   Seasons: spring, summer, fall
   Occasions: everyday, casual, work

🔍 Duplicate Detection:
   Image Hash: ✅ Present
   File Size: 245.67 KB
   Dimensions: 800x1200
   Aspect Ratio: 0.6667

📊 Usage Tracking:
   Favorite: No
   Wear Count: 0
   Last Worn: Never
```

### Missing Metadata
```
❌ Item 5: White T-Shirt - Missing required: imageUrl, analysis
⚠️  Item 8: Blue Jeans - Missing optional: imageHash, metadata
```

---

## Troubleshooting

### "Not logged in" Error
- Make sure you're logged in to the app
- Refresh the page and try again

### "Failed to fetch wardrobe" Error
- Check your internet connection
- Verify backend is running
- Check browser console for detailed errors

### No items found
- Make sure you've uploaded at least one item
- Check that you're logged in with the correct account
- Try refreshing the page

---

## Next Steps

After verifying with browser scripts:
1. ✅ Run the Node.js verification script
2. ✅ Check Firebase Console directly
3. ✅ Test editing metadata
4. ✅ Test outfit generation with uploaded items

