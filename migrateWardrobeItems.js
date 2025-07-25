const admin = require('firebase-admin');
const path = require('path');

// Use your downloaded service account key
const serviceAccount = require('./backend/service-account-key.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

async function migrateWardrobeItems() {
  const wardrobeRef = db.collection('wardrobe');
  const snapshot = await wardrobeRef.get();

  let updatedCount = 0;
  for (const doc of snapshot.docs) {
    const data = doc.data();
    let needsUpdate = false;

    // Helper to ensure array of Color objects
    function fixColorArray(arr, fallbackHex = '#000000', fallbackRgb = [0,0,0]) {
      if (!Array.isArray(arr)) return [];
      return arr.map(item => {
        if (typeof item === 'object' && item && item.name && item.hex && item.rgb) {
          return item;
        }
        if (typeof item === 'string') {
          return {
            name: item,
            hex: fallbackHex,
            rgb: fallbackRgb
          };
        }
        return null;
      }).filter(Boolean);
    }

    // Fix metadata.colorAnalysis
    if (data.metadata && data.metadata.colorAnalysis) {
      const ca = data.metadata.colorAnalysis;
      const fixedDominant = fixColorArray(ca.dominant);
      const fixedMatching = fixColorArray(ca.matching);
      if (JSON.stringify(ca.dominant) !== JSON.stringify(fixedDominant) ||
          JSON.stringify(ca.matching) !== JSON.stringify(fixedMatching)) {
        data.metadata.colorAnalysis.dominant = fixedDominant;
        data.metadata.colorAnalysis.matching = fixedMatching;
        needsUpdate = true;
      }
    }

    // Ensure arrays are not null
    const arrayFields = [
      'tags', 'style', 'occasion', 'season', 'dominantColors', 'matchingColors',
      'metadata.styleTags', 'metadata.occasionTags'
    ];
    arrayFields.forEach(fieldPath => {
      const [root, sub] = fieldPath.split('.');
      if (sub) {
        if (data[root] && data[root][sub] == null) {
          data[root][sub] = [];
          needsUpdate = true;
        }
      } else {
        if (data[root] == null) {
          data[root] = [];
          needsUpdate = true;
        }
      }
    });

    if (needsUpdate) {
      await doc.ref.update(data);
      updatedCount++;
      console.log(`Updated item ${doc.id}`);
    }
  }

  console.log(`Migration complete. Updated ${updatedCount} items.`);
}

migrateWardrobeItems().catch(console.error); 