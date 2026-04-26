import { NextResponse } from 'next/server';
import { serverDebugLog } from '@/lib/server/debug';
import { getFirebaseAdminDb, initFirebaseAdminApp } from '@/lib/server/firebaseAdmin';

interface OldClothingItem {
  id: string;
  userId: string;
  type: string;
  color?: string;
  season?: string[];
  imageUrl?: string;
  tags?: string[];
  style?: string[];
  brand?: string;
  createdAt: any;
  updatedAt: any;
}

// Map of old types to new types
const typeMapping: Record<string, 'shirt' | 'pants' | 'dress' | 'skirt' | 'jacket' | 'sweater' | 'shoes' | 'accessory' | 'other'> = {
  'shorts': 'pants',
  't-shirt': 'shirt',
  'tshirt': 'shirt',
  'tank top': 'shirt',
  'blouse': 'shirt',
  'sweatshirt': 'sweater',
  'hoodie': 'sweater',
  'jeans': 'pants',
  'trousers': 'pants',
  'slacks': 'pants',
  'skirt': 'skirt',
  'dress': 'dress',
  'jacket': 'jacket',
  'coat': 'jacket',
  'sweater': 'sweater',
  'shoes': 'shoes',
  'sneakers': 'shoes',
  'boots': 'shoes',
  'sandals': 'shoes',
  'heels': 'shoes',
  'accessory': 'accessory',
  'jewelry': 'accessory',
  'bag': 'accessory',
  'hat': 'accessory',
  'scarf': 'accessory',
  'belt': 'accessory',
  'gloves': 'accessory',
  'socks': 'accessory',
  'underwear': 'accessory',
  'swimwear': 'accessory',
  'other': 'other'
};

export async function POST() {
  try {
    serverDebugLog('Starting schema update...');
    initFirebaseAdminApp();
    const db = getFirebaseAdminDb();
    
    // Get all clothing items
    const snapshot = await db.collection('wardrobe').get();
    serverDebugLog(`Found ${snapshot.size} items to update`);
    
    // Update each item
    let batch = db.batch();
    let updatedCount = 0;
    let pendingCount = 0;
    
    for (const doc of snapshot.docs) {
      const oldData = doc.data() as OldClothingItem;
      serverDebugLog('Original data:', JSON.stringify(oldData, null, 2));
      
      try {
        // Map the type to a valid enum value
        const mappedType = typeMapping[oldData.type?.toLowerCase()] || 'other';
        
        // Create new data structure with all required fields and proper defaults
        const newData = {
          id: doc.id,
          userId: oldData.userId,
          name: oldData.type || 'Unnamed Item',
          type: mappedType,
          color: oldData.color || 'unknown',
          season: (oldData.season || []).map(s => s.toLowerCase()) as ('spring' | 'summer' | 'fall' | 'winter')[],
          imageUrl: oldData.imageUrl || '',
          tags: oldData.tags || [],
          style: oldData.style || [],
          dominantColors: [{
            name: oldData.color || 'unknown',
            hex: '#000000',
            rgb: [0, 0, 0] as number[]
          }],
          matchingColors: [{
            name: oldData.color || 'unknown',
            hex: '#000000',
            rgb: [0, 0, 0] as number[]
          }],
          occasion: [],
          createdAt: oldData.createdAt?.toMillis?.() || Date.now(),
          updatedAt: oldData.updatedAt?.toMillis?.() || Date.now(),
          subType: oldData.type || 'other',
          brand: oldData.brand || '',
          colorName: oldData.color || 'unknown',
          metadata: {}
        };
        
        serverDebugLog('Transformed data:', JSON.stringify(newData, null, 2));
        
        // Update the document
        batch.update(doc.ref, newData);
        updatedCount++;
        pendingCount++;
        
        // Commit batch every 500 operations
        if (pendingCount === 500) {
          await batch.commit();
          serverDebugLog(`Committed ${updatedCount} updates`);
          batch = db.batch();
          pendingCount = 0;
        }
      } catch (error) {
        console.error(`Validation failed for item ${doc.id}:`, error);
        continue;
      }
    }
    
    // Commit any remaining updates
    if (pendingCount > 0) {
      await batch.commit();
    }
    
    return NextResponse.json({ 
      success: true, 
      message: `Successfully updated ${updatedCount} items` 
    });
  } catch (error) {
    console.error('Error updating schema:', error);
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 });
  }
} 
