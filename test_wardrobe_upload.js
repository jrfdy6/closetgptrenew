/**
 * Wardrobe Upload Verification Script
 * 
 * This script verifies that uploaded wardrobe items contain all required metadata
 * and are properly stored in Firestore.
 */

import admin from 'firebase-admin';
import { readFileSync } from 'fs';

// Initialize Firebase Admin (if not already initialized)
try {
  const serviceAccount = JSON.parse(
    readFileSync('./config/closetgpt-firebase-adminsdk.json', 'utf8')
  );
  
  if (!admin.apps.length) {
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
      storageBucket: 'closetgpt.appspot.com'
    });
  }
} catch (error) {
  console.error('❌ Failed to initialize Firebase Admin:', error.message);
  process.exit(1);
}

const db = admin.firestore();

// Required fields for wardrobe items
const REQUIRED_FIELDS = [
  'id',
  'userId',
  'name',
  'type',
  'color',
  'imageUrl',
  'createdAt'
];

// Optional but expected fields from AI analysis
const EXPECTED_AI_FIELDS = [
  'analysis',
  'style',
  'season',
  'occasion',
  'material',
  'subType',
  'dominantColors',
  'matchingColors'
];

// Duplicate detection fields
const DUPLICATE_DETECTION_FIELDS = [
  'imageHash',
  'metadata',
  'fileSize'
];

// Usage tracking fields
const USAGE_FIELDS = [
  'favorite',
  'wearCount',
  'lastWorn',
  'backgroundRemoved'
];

/**
 * Check if an item has all required fields
 */
function checkRequiredFields(item) {
  const missing = [];
  const present = [];
  
  for (const field of REQUIRED_FIELDS) {
    if (!item[field]) {
      missing.push(field);
    } else {
      present.push(field);
    }
  }
  
  return { missing, present };
}

/**
 * Check AI analysis fields
 */
function checkAIFields(item) {
  const missing = [];
  const present = [];
  
  for (const field of EXPECTED_AI_FIELDS) {
    if (!item[field]) {
      missing.push(field);
    } else {
      present.push(field);
    }
  }
  
  // Check nested analysis metadata
  if (item.analysis) {
    const analysisFields = ['name', 'type', 'dominantColors', 'matchingColors', 'style', 'season', 'occasion'];
    const missingAnalysis = analysisFields.filter(f => !item.analysis[f]);
    
    if (missingAnalysis.length > 0) {
      missing.push(`analysis.${missingAnalysis.join(', analysis.')}`);
    }
    
    // Check visualAttributes
    if (item.analysis.metadata?.visualAttributes) {
      present.push('analysis.metadata.visualAttributes');
      const visualAttrs = ['material', 'pattern', 'fit', 'sleeveLength'];
      const presentVisual = visualAttrs.filter(f => item.analysis.metadata.visualAttributes[f]);
      present.push(...presentVisual.map(f => `visualAttributes.${f}`));
    } else {
      missing.push('analysis.metadata.visualAttributes');
    }
  }
  
  return { missing, present };
}

/**
 * Check duplicate detection fields
 */
function checkDuplicateDetectionFields(item) {
  const missing = [];
  const present = [];
  
  for (const field of DUPLICATE_DETECTION_FIELDS) {
    if (!item[field]) {
      missing.push(field);
    } else {
      present.push(field);
    }
  }
  
  // Check nested metadata fields
  if (item.metadata) {
    const metadataFields = ['width', 'height', 'aspectRatio', 'fileSize', 'type'];
    const presentMetadata = metadataFields.filter(f => item.metadata[f] !== undefined);
    present.push(...presentMetadata.map(f => `metadata.${f}`));
    
    const missingMetadata = metadataFields.filter(f => item.metadata[f] === undefined);
    if (missingMetadata.length > 0) {
      missing.push(...missingMetadata.map(f => `metadata.${f}`));
    }
  }
  
  return { missing, present };
}

/**
 * Check usage tracking fields
 */
function checkUsageFields(item) {
  const missing = [];
  const present = [];
  
  for (const field of USAGE_FIELDS) {
    if (item[field] === undefined) {
      missing.push(field);
    } else {
      present.push(field);
    }
  }
  
  return { missing, present };
}

/**
 * Main verification function
 */
async function verifyWardrobeUploads(userId = null, limit = 10) {
  console.log('🔍 Starting wardrobe upload verification...\n');
  
  try {
    let query = db.collection('wardrobe');
    
    if (userId) {
      query = query.where('userId', '==', userId);
      console.log(`📂 Filtering by userId: ${userId}`);
    }
    
    // Get most recent items
    query = query.orderBy('createdAt', 'desc').limit(limit);
    
    const snapshot = await query.get();
    
    if (snapshot.empty) {
      console.log('⚠️  No wardrobe items found');
      return;
    }
    
    console.log(`✅ Found ${snapshot.size} wardrobe items\n`);
    console.log('='.repeat(80));
    
    let successCount = 0;
    let warningCount = 0;
    let errorCount = 0;
    
    snapshot.forEach((doc, index) => {
      const item = doc.to_dict();
      const itemNumber = index + 1;
      
      console.log(`\n📦 Item ${itemNumber}: ${item.name || 'Unnamed Item'}`);
      console.log(`   ID: ${doc.id}`);
      console.log(`   Type: ${item.type || 'unknown'}`);
      console.log(`   Color: ${item.color || 'unknown'}`);
      console.log(`   Created: ${item.createdAt || 'unknown'}`);
      
      // Check required fields
      const requiredCheck = checkRequiredFields(item);
      if (requiredCheck.missing.length === 0) {
        console.log(`   ✅ All required fields present`);
        successCount++;
      } else {
        console.log(`   ❌ Missing required fields: ${requiredCheck.missing.join(', ')}`);
        errorCount++;
      }
      
      // Check AI analysis fields
      const aiCheck = checkAIFields(item);
      if (aiCheck.missing.length === 0) {
        console.log(`   ✅ All AI analysis fields present`);
      } else {
        console.log(`   ⚠️  Missing AI fields: ${aiCheck.missing.join(', ')}`);
        warningCount++;
      }
      
      // Check duplicate detection fields
      const dupCheck = checkDuplicateDetectionFields(item);
      if (dupCheck.missing.length === 0) {
        console.log(`   ✅ All duplicate detection fields present`);
      } else {
        console.log(`   ⚠️  Missing duplicate detection fields: ${dupCheck.missing.join(', ')}`);
      }
      
      // Check usage tracking fields
      const usageCheck = checkUsageFields(item);
      if (usageCheck.missing.length === 0) {
        console.log(`   ✅ All usage tracking fields present`);
      } else {
        console.log(`   ⚠️  Missing usage fields: ${usageCheck.missing.join(', ')}`);
      }
      
      // Show sample of metadata structure
      if (item.analysis?.metadata?.visualAttributes) {
        const va = item.analysis.metadata.visualAttributes;
        console.log(`   🎨 Visual Attributes:`);
        console.log(`      - Material: ${va.material || 'N/A'}`);
        console.log(`      - Pattern: ${va.pattern || 'N/A'}`);
        console.log(`      - Fit: ${va.fit || 'N/A'}`);
        console.log(`      - Sleeve: ${va.sleeveLength || 'N/A'}`);
      }
      
      // Show dominant colors
      if (item.analysis?.dominantColors?.length > 0) {
        const colors = item.analysis.dominantColors.slice(0, 3);
        console.log(`   🎨 Dominant Colors: ${colors.map(c => c.name).join(', ')}`);
      }
      
      // Show styles, seasons, occasions
      if (item.style?.length > 0) {
        console.log(`   👔 Styles: ${item.style.join(', ')}`);
      }
      if (item.season?.length > 0) {
        console.log(`   🌡️  Seasons: ${item.season.join(', ')}`);
      }
      if (item.occasion?.length > 0) {
        console.log(`   🎉 Occasions: ${item.occasion.join(', ')}`);
      }
      
      console.log(`   ${'─'.repeat(76)}`);
    });
    
    // Summary
    console.log('\n' + '='.repeat(80));
    console.log('\n📊 VERIFICATION SUMMARY');
    console.log('='.repeat(80));
    console.log(`✅ Items with all required fields: ${successCount}`);
    console.log(`⚠️  Items with warnings: ${warningCount}`);
    console.log(`❌ Items with errors: ${errorCount}`);
    console.log(`📦 Total items checked: ${snapshot.size}`);
    
    if (errorCount === 0 && warningCount === 0) {
      console.log('\n✨ All items are properly formatted! Upload system is working correctly.');
    } else if (errorCount === 0) {
      console.log('\n⚠️  Some optional fields are missing, but all required fields are present.');
    } else {
      console.log('\n❌ Some items are missing required fields. Please investigate.');
    }
    
  } catch (error) {
    console.error('❌ Error during verification:', error);
    throw error;
  }
}

/**
 * Show the most recently uploaded item in detail
 */
async function showLatestItem(userId = null) {
  console.log('\n📦 Fetching most recently uploaded item...\n');
  
  try {
    let query = db.collection('wardrobe');
    
    if (userId) {
      query = query.where('userId', '==', userId);
    }
    
    query = query.orderBy('createdAt', 'desc').limit(1);
    
    const snapshot = await query.get();
    
    if (snapshot.empty) {
      console.log('⚠️  No items found');
      return;
    }
    
    const doc = snapshot.docs[0];
    const item = doc.to_dict();
    
    console.log('='.repeat(80));
    console.log('LATEST WARDROBE ITEM - DETAILED VIEW');
    console.log('='.repeat(80));
    console.log('\nDocument ID:', doc.id);
    console.log('\nFull Data Structure:');
    console.log(JSON.stringify(item, null, 2));
    console.log('='.repeat(80));
    
  } catch (error) {
    console.error('❌ Error fetching latest item:', error);
    throw error;
  }
}

// Main execution
const args = process.argv.slice(2);
const command = args[0] || 'verify';
const userId = args[1] || null;

console.log('\n' + '='.repeat(80));
console.log('WARDROBE UPLOAD VERIFICATION TOOL');
console.log('='.repeat(80) + '\n');

if (command === 'verify') {
  verifyWardrobeUploads(userId)
    .then(() => {
      console.log('\n✅ Verification complete\n');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Verification failed:', error);
      process.exit(1);
    });
} else if (command === 'latest') {
  showLatestItem(userId)
    .then(() => {
      console.log('\n✅ Done\n');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Failed:', error);
      process.exit(1);
    });
} else {
  console.log('Usage:');
  console.log('  node test_wardrobe_upload.js verify [userId]  - Verify recent uploads');
  console.log('  node test_wardrobe_upload.js latest [userId]   - Show latest item details');
  console.log('\nExamples:');
  console.log('  node test_wardrobe_upload.js verify');
  console.log('  node test_wardrobe_upload.js verify dANqjiI0CKgaitxzYtw1bhtvQrG3');
  console.log('  node test_wardrobe_upload.js latest');
  process.exit(0);
}

