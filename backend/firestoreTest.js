// firestoreTest.js
const admin = require("firebase-admin");
const { initializeApp, applicationDefault } = require("firebase-admin/app");
const { getFirestore } = require("firebase-admin/firestore");

// Initialize Firebase Admin
initializeApp({
  credential: applicationDefault(), // Make sure GOOGLE_APPLICATION_CREDENTIALS is set
});

const db = getFirestore();

const currentUserId = "dANqjiI0CKgaitxzYtw1bhtvQrG3"; // replace with your user

async function runTest() {
  console.log("🔍 Firestore User Filtering Test");
  console.log("=".repeat(50));
  console.log(`👤 Testing with user ID: ${currentUserId}`);
  console.log();

  try {
    // Test 1: Direct query with user_id filter
    console.log("📊 Test 1: Direct user_id query");
    const snapshot = await db.collection("outfits")
      .where("user_id", "==", currentUserId)
      .limit(5)
      .get();

    console.log(`✅ Found ${snapshot.size} outfits for user: ${currentUserId}\n`);

    snapshot.forEach((doc, i) => {
      const data = doc.data();
      console.log(`#${i + 1} Outfit ID: ${doc.id}`);
      console.log(`👤 user_id: ${data.user_id}`);
      console.log(`🔍 userId: ${data.userId || 'NOT_FOUND'}`);
      console.log(`🧥 items: ${Array.isArray(data.items) ? data.items.length : 0}`);
      console.log(`🕒 created: ${data.createdAt?.toDate?.() || data.created_at?.toDate?.() || "N/A"}`);
      
      // Show first item details
      if (data.items && data.items.length > 0) {
        const firstItem = data.items[0];
        if (typeof firstItem === 'object' && firstItem.userId) {
          console.log(`🔍 First item userId: ${firstItem.userId}`);
        } else {
          console.log(`🔍 First item: ${typeof firstItem === 'string' ? 'String ID' : 'Object without userId'}`);
        }
      }
      console.log("---------");
    });

    // Test 2: Get all outfits and check filtering manually
    console.log("\n📊 Test 2: Manual filtering check");
    const allOutfits = await db.collection("outfits").limit(10).get();
    
    let directMatches = 0;
    let itemMatches = 0;
    let noMatches = 0;
    
    allOutfits.forEach((doc) => {
      const data = doc.data();
      const outfitUserId = data.user_id;
      const outfitUserIdAlt = data.userId;
      
      let hasDirectMatch = false;
      let hasItemMatch = false;
      
      // Check direct matches
      if (outfitUserId === currentUserId || outfitUserIdAlt === currentUserId) {
        directMatches++;
        hasDirectMatch = true;
      }
      
      // Check item-level matches
      if (data.items && Array.isArray(data.items)) {
        for (const item of data.items) {
          if (typeof item === 'object' && item.userId === currentUserId) {
            itemMatches++;
            hasItemMatch = true;
            break;
          }
        }
      }
      
      if (!hasDirectMatch && !hasItemMatch) {
        noMatches++;
      }
    });
    
    console.log(`📈 Summary:`);
    console.log(`   - Total outfits checked: ${allOutfits.size}`);
    console.log(`   - Direct user_id matches: ${directMatches}`);
    console.log(`   - Item-level userId matches: ${itemMatches}`);
    console.log(`   - No matches: ${noMatches}`);
    
    // Test 3: Check for any outfits with different user IDs
    console.log("\n📊 Test 3: Checking for other users' outfits");
    const otherUsers = new Set();
    allOutfits.forEach((doc) => {
      const data = doc.data();
      if (data.user_id && data.user_id !== currentUserId) {
        otherUsers.add(data.user_id);
      }
      if (data.userId && data.userId !== currentUserId) {
        otherUsers.add(data.userId);
      }
    });
    
    if (otherUsers.size > 0) {
      console.log(`⚠️ Found outfits from other users: ${Array.from(otherUsers).join(', ')}`);
    } else {
      console.log(`✅ All checked outfits belong to current user`);
    }

    console.log("\n✅ Firestore direct query complete.");
    
  } catch (error) {
    console.error("❌ Error:", error);
  }
}

// Check if credentials are set
if (!process.env.GOOGLE_APPLICATION_CREDENTIALS) {
  console.log("⚠️ Warning: GOOGLE_APPLICATION_CREDENTIALS not set");
  console.log("   Set it with: export GOOGLE_APPLICATION_CREDENTIALS='./path-to-service-account.json'");
  console.log("   Or the script will use default credentials if available");
  console.log();
}

runTest().catch(console.error); 