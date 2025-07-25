import { cleanAndStoreWardrobeItem, processAllWardrobeItems, compareItems, analyzeDataQuality } from './wardrobeCleaner';
import { ClothingItem } from '@/types/wardrobe';
import { Garment, GarmentStyle, GarmentMaterial, GarmentPattern, GarmentFit } from '@/types/photo-analysis';
import { collection, getDocs } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';
import { useFirebase } from './firebase-context';

export async function testWardrobeCleaner(userId: string) {
  // Sample original item
  const originalItem: ClothingItem = {
    id: 'test-item-1',
    userId,
    name: 'Blue Denim Jacket',
    type: 'jacket',
    color: '#1E3A8A',
    season: ['spring', 'fall'],
    imageUrl: 'https://via.placeholder.com/400x600/1E3A8A/FFFFFF?text=Jacket',
    tags: ['denim', 'casual'],
    style: ['Casual'],
    dominantColors: [{
      name: 'Navy Blue',
      hex: '#1E3A8A',
      rgb: [30, 58, 138]
    }],
    matchingColors: [{
      name: 'White',
      hex: '#FFFFFF',
      rgb: [255, 255, 255]
    }],
    occasion: ['casual', 'everyday'],
    brand: 'Levi\'s',
    createdAt: Date.now(),
    updatedAt: Date.now(),
    subType: 'denim',
    colorName: 'Navy Blue',
    backgroundRemoved: true,
    metadata: {
      brand: 'Levi\'s',
      analysisTimestamp: Date.now(),
      originalType: 'jacket',
      originalSubType: 'denim',
      styleTags: ['Casual'],
      occasionTags: ['casual', 'everyday'],
      imageHash: 'abc123',
      colorAnalysis: {
        dominant: [{
          name: 'Navy Blue',
          hex: '#1E3A8A',
          rgb: [30, 58, 138]
        }],
        matching: [{
          name: 'White',
          hex: '#FFFFFF',
          rgb: [255, 255, 255]
        }]
      },
      basicMetadata: {
        width: 800,
        height: 1200,
        orientation: 'portrait',
        dateTaken: '2024-03-20T12:00:00Z',
        deviceModel: 'iPhone 13',
        gps: null,
        flashUsed: false
      },
      visualAttributes: {
        material: 'denim',
        pattern: 'solid',
        textureStyle: 'woven',
        fabricWeight: 'medium',
        fit: 'regular',
        silhouette: 'boxy',
        length: 'hip-length',
        genderTarget: 'unisex',
        sleeveLength: 'long',
        hangerPresent: false,
        backgroundRemoved: true,
        wearLayer: 'outer',
        formalLevel: 'casual'
      },
      itemMetadata: {
        priceEstimate: '$89.99',
        careInstructions: 'Machine wash cold, tumble dry low',
        tags: ['denim', 'casual', 'jacket']
      },
      naturalDescription: 'A classic blue denim jacket with a regular fit and long sleeves'
    }
  };

  // Sample analyzed data
  const analyzedData: Garment = {
    type: 'jacket',
    color: '#1E3A8A',
    style: ['Casual', 'Streetwear'],
    pattern: 'solid',
    fit: 'regular',
    material: 'denim',
    confidence: 0.95,
    subType: 'denim',
    colorName: 'Navy Blue',
    backgroundRemoved: true,
    dominantColors: [{
      name: 'Navy Blue',
      hex: '#1E3A8A',
      rgb: [30, 58, 138]
    }],
    matchingColors: [{
      name: 'White',
      hex: '#FFFFFF',
      rgb: [255, 255, 255]
    }],
    occasion: ['casual', 'everyday', 'streetwear'],
    season: ['spring', 'fall', 'all-season'],
    brand: 'Levi\'s',
    name: 'Blue Denim Jacket',
    tags: ['denim', 'casual', 'streetwear', 'jacket'],
    metadata: {
      visualAttributes: {
        material: 'denim',
        pattern: 'solid',
        textureStyle: 'woven',
        fabricWeight: 'medium',
        fit: 'regular',
        silhouette: 'boxy',
        length: 'hip-length',
        genderTarget: 'unisex',
        sleeveLength: 'long',
        hangerPresent: false,
        backgroundRemoved: true,
        wearLayer: 'outer',
        formalLevel: 'casual'
      },
      itemMetadata: {
        priceEstimate: '$89.99',
        careInstructions: 'Machine wash cold, tumble dry low',
        tags: ['denim', 'casual', 'jacket', 'streetwear']
      },
      basicMetadata: {
        width: 800,
        height: 1200,
        orientation: 'portrait',
        dateTaken: '2024-03-20T12:00:00Z',
        deviceModel: 'iPhone 13',
        gps: null,
        flashUsed: false
      }
    }
  };

  try {
    const cleanedItem = await cleanAndStoreWardrobeItem(userId, originalItem, analyzedData);
    console.log('Successfully cleaned and stored item:', cleanedItem);
    return cleanedItem;
  } catch (error) {
    console.error('Error cleaning and storing item:', error);
    throw error;
  }
}

export async function processEntireWardrobe(userId: string) {
  try {
    if (!db) {
      throw new Error("Firestore is not initialized");
    }
    // Get all items from the user's wardrobe
    const wardrobeRef = collection(db, 'wardrobe');
    const wardrobeSnapshot = await getDocs(wardrobeRef);
    
    // Create a map of analyzed data for all items
    const analyzedDataMap = new Map<string, Garment>();
    
    // Process each item
    for (const doc of wardrobeSnapshot.docs) {
      const item = doc.data() as ClothingItem;
      // Only process items belonging to the current user
      if (item.userId !== userId) continue;
      
      // For now, we'll use the existing metadata as analyzed data
      // In a real scenario, this would come from the photo analysis
      const analyzedData: Garment = {
        id: item.id,
        name: item.name,
        type: item.type,
        color: item.color,
        season: item.season,
        tags: item.tags,
        style: item.style as GarmentStyle[],
        dominantColors: item.dominantColors,
        matchingColors: item.matchingColors,
        occasion: item.occasion,
        brand: item.brand || undefined,
        subType: item.subType || undefined,
        colorName: item.colorName || undefined,
        backgroundRemoved: item.backgroundRemoved || false,
        material: (item.metadata?.visualAttributes?.material || 'cotton') as GarmentMaterial,
        pattern: (item.metadata?.visualAttributes?.pattern || 'solid') as GarmentPattern,
        fit: (item.metadata?.visualAttributes?.fit || 'regular') as GarmentFit,
        confidence: 0.95,
        metadata: {
          basicMetadata: {
            width: item.metadata?.basicMetadata?.width || 800,
            height: item.metadata?.basicMetadata?.height || 1200,
            orientation: item.metadata?.basicMetadata?.orientation || 'portrait',
            dateTaken: item.metadata?.basicMetadata?.dateTaken || new Date().toISOString(),
            deviceModel: item.metadata?.basicMetadata?.deviceModel || 'iPhone 13',
            gps: item.metadata?.basicMetadata?.gps || null,
            flashUsed: item.metadata?.basicMetadata?.flashUsed || false
          },
          visualAttributes: {
            material: item.metadata?.visualAttributes?.material || 'cotton',
            pattern: item.metadata?.visualAttributes?.pattern || 'solid',
            textureStyle: item.metadata?.visualAttributes?.textureStyle || 'woven',
            fabricWeight: item.metadata?.visualAttributes?.fabricWeight || 'medium',
            fit: item.metadata?.visualAttributes?.fit || 'regular',
            silhouette: item.metadata?.visualAttributes?.silhouette || 'regular',
            length: item.metadata?.visualAttributes?.length || 'regular',
            genderTarget: item.metadata?.visualAttributes?.genderTarget || 'unisex',
            sleeveLength: item.metadata?.visualAttributes?.sleeveLength || 'regular',
            hangerPresent: item.metadata?.visualAttributes?.hangerPresent || false,
            backgroundRemoved: item.metadata?.visualAttributes?.backgroundRemoved || false,
            wearLayer: item.metadata?.visualAttributes?.wearLayer || 'outer',
            formalLevel: item.metadata?.visualAttributes?.formalLevel || 'casual'
          },
          itemMetadata: {
            priceEstimate: item.metadata?.itemMetadata?.priceEstimate || '$0.00',
            careInstructions: item.metadata?.itemMetadata?.careInstructions || 'Check label',
            tags: item.metadata?.itemMetadata?.tags || []
          }
        }
      };
      analyzedDataMap.set(item.id, analyzedData);
    }

    // Process all items
    const result = await processAllWardrobeItems(userId, analyzedDataMap);
    
    // Display enhancement summary
    console.log('\n=== Wardrobe Data Enhancement Summary ===');
    console.log(`Timestamp: ${new Date(result.summary.timestamp).toLocaleString()}`);
    
    console.log('\n--- Statistics ---');
    console.log(`Total Items: ${result.summary.statistics.totalItems}`);
    console.log(`Items with Enhancements: ${result.summary.statistics.itemsWithEnhancements}`);
    console.log(`Total Enhancements: ${result.summary.statistics.totalEnhancements}`);
    
    console.log('\n--- Enhancements by Field ---');
    Object.entries(result.summary.enhancements.byField)
      .sort(([, a], [, b]) => b.count - a.count)
      .forEach(([field, data]) => {
        console.log(`\n${field} (${data.count} enhancements):`);
        data.examples.slice(0, 3).forEach(example => {
          console.log(`  ${example.itemName}:`);
          console.log(`    From: ${JSON.stringify(example.original)}`);
          console.log(`    To:   ${JSON.stringify(example.enhanced)}`);
        });
        if (data.examples.length > 3) {
          console.log(`  ... and ${data.examples.length - 3} more examples`);
        }
      });
    
    console.log('\n--- Enhanced Items ---');
    result.summary.items.forEach(item => {
      console.log(`\n${item.name} (${item.id})`);
      console.log(`  Total Enhancements: ${item.enhancements.length}`);
      item.enhancements.forEach(enhancement => {
        console.log(`  - ${enhancement.field}:`);
        console.log(`    From: ${JSON.stringify(enhancement.original)}`);
        console.log(`    To:   ${JSON.stringify(enhancement.enhanced)}`);
        console.log(`    ${enhancement.description}`);
      });
    });

    return result;
  } catch (error) {
    console.error('Error processing wardrobe:', error);
    throw error;
  }
}

export async function processCurrentUserWardrobe(userId: string) {
  if (!userId) {
    console.error('No user ID provided');
    return;
  }

  try {
    console.log('\n🔍 Starting Wardrobe Data Enhancement Process');
    console.log(`👤 User ID: ${userId}`);
    console.log('⏳ Processing...\n');

    const result = await processEntireWardrobe(userId);
    
    // Print detailed metrics
    console.log('\n📊 Data Quality Metrics Summary');
    console.log('=============================');
    
    // Print field-specific metrics
    console.log('\n🔍 Field-Specific Enhancements');
    console.log('---------------------------');
    Object.entries(result.summary.enhancements.byField)
      .sort(([, a], [, b]) => b.count - a.count)
      .forEach(([field, data]) => {
        console.log(`\n${field}:`);
        console.log(`  Total Enhancements: ${data.count}`);
        console.log('  Examples:');
        data.examples.slice(0, 3).forEach(example => {
          console.log(`    - ${example.itemName}:`);
          console.log(`      From: ${JSON.stringify(example.original)}`);
          console.log(`      To:   ${JSON.stringify(example.enhanced)}`);
        });
        if (data.examples.length > 3) {
          console.log(`    ... and ${data.examples.length - 3} more examples`);
        }
      });
    
    // Print item-specific metrics
    console.log('\n👕 Enhanced Items');
    console.log('---------------');
    result.summary.items.forEach(item => {
      console.log(`\n${item.name} (${item.id})`);
      console.log(`  Total Enhancements: ${item.enhancements.length}`);
      item.enhancements.forEach(enhancement => {
        console.log(`  - ${enhancement.field}:`);
        console.log(`    From: ${JSON.stringify(enhancement.original)}`);
        console.log(`    To:   ${JSON.stringify(enhancement.enhanced)}`);
        console.log(`    ${enhancement.description}`);
      });
    });

    // Print final statistics
    console.log('\n📈 Final Statistics');
    console.log('----------------');
    console.log(`Total Items Processed: ${result.summary.statistics.totalItems}`);
    console.log(`Items with Enhancements: ${result.summary.statistics.itemsWithEnhancements}`);
    console.log(`Total Enhancements Made: ${result.summary.statistics.totalEnhancements}`);
    console.log(`Items Skipped: ${result.skipped}`);
    
    console.log('\n✅ Process completed successfully!\n');
    return result;
  } catch (error) {
    console.error('\n❌ Error processing wardrobe:', error);
    throw error;
  }
} 