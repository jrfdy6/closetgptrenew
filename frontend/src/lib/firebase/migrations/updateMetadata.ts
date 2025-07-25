import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { ClothingItem } from '@shared/types';
import path from 'path';
import { config } from 'dotenv';

// Load environment variables
config({ path: path.resolve(process.cwd(), '.env.local') });

// Initialize Firebase Admin
const serviceAccount = require('../../../../serviceAccountKey.json');
const app = initializeApp({
  credential: cert(serviceAccount)
});

const db = getFirestore(app);
const WARDROBE_COLLECTION = 'wardrobe';

async function updateMetadata() {
  try {
    console.log('Starting metadata migration...');
    const batch = db.batch();
    const wardrobeRef = db.collection(WARDROBE_COLLECTION);
    const snapshot = await wardrobeRef.get();
    let updatedCount = 0;

    console.log(`Found ${snapshot.size} items in the wardrobe collection`);

    snapshot.forEach((doc) => {
      const item = doc.data() as ClothingItem;
      const itemRef = doc.ref;

      console.log(`Processing item ${item.id || doc.id}:`, {
        name: item.name,
        type: item.type,
        currentMetadata: item.metadata
      });

      // Create updated metadata structure
      const updatedMetadata = {
        analysisTimestamp: item.metadata?.analysisTimestamp || item.createdAt,
        originalType: item.metadata?.originalType || item.type,
        originalSubType: item.metadata?.originalSubType || item.subType || 'other',
        styleTags: item.metadata?.styleTags || item.style || [],
        occasionTags: item.metadata?.occasionTags || item.occasion || [],
        brand: item.metadata?.brand || item.brand || '',
        color: item.metadata?.color || item.color || 'unknown',
        colorName: item.metadata?.colorName || item.colorName || 'unknown',
        season: item.metadata?.season || item.season || [],
        colorAnalysis: {
          dominant: item.metadata?.colorAnalysis?.dominant || item.dominantColors || [],
          matching: item.metadata?.colorAnalysis?.matching || item.matchingColors || []
        }
      };

      console.log(`Updated metadata for item ${item.id || doc.id}:`, updatedMetadata);

      // Update the document with new metadata
      batch.update(itemRef, { metadata: updatedMetadata });
      updatedCount++;
    });

    // Commit all updates
    await batch.commit();
    console.log(`Successfully updated metadata for ${updatedCount} items`);
    return { success: true, updatedCount };
  } catch (error) {
    console.error('Error updating metadata:', error);
    return { success: false, error };
  }
}

// Export the migration function
export { updateMetadata }; 