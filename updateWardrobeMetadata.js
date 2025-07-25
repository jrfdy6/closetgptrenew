const admin = require('firebase-admin');
const path = require('path');

// Initialize Firebase Admin
const serviceAccount = require('./backend/service-account-key.json');
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

// Define all possible tags
const TAGS = {
  occasions: [
    'Wedding', 'Funeral', 'Vacation', 'Business', 'Formal', 'Casual', 
    'Party', 'Date', 'Interview', 'Graduation', 'Beach', 'Gym', 
    'Travel', 'Outdoor', 'Indoor', 'Night Out', 'Brunch', 'Dinner',
    'Conference', 'Presentation', 'Religious', 'Cultural', 'Sporting Event'
  ],
  styles: [
    'Androgynous', 'Avant Garde', 'Athletic', 'Bohemian', 'Business', 
    'Casual', 'Classic', 'Coastal Chic', 'Contemporary', 'Elegant',
    'Formal', 'Gothic', 'Grunge', 'Hip Hop', 'Minimalist', 'Modern',
    'Punk', 'Retro', 'Romantic', 'Streetwear', 'Vintage', 'Preppy',
    'Glamorous', 'Industrial', 'Military', 'Nautical', 'Playful',
    'Professional', 'Relaxed', 'Sophisticated', 'Sporty', 'Urban'
  ],
  moods: [
    'Playful', 'Serious', 'Confident', 'Relaxed', 'Elegant', 'Edgy',
    'Romantic', 'Professional', 'Casual', 'Dramatic', 'Minimal',
    'Bold', 'Subtle', 'Sophisticated', 'Fun', 'Formal', 'Creative',
    'Traditional', 'Modern', 'Vintage', 'Luxurious', 'Simple'
  ],
  bodyTypes: [
    'Rectangle', 'Hourglass', 'Pear', 'Apple', 'Inverted Triangle',
    'Athletic', 'Curvy', 'Petite', 'Tall', 'Plus Size'
  ],
  genders: [
    'Masculine', 'Feminine', 'Androgynous', 'Gender Neutral', 'Unisex'
  ],
  weather: [
    'Hot', 'Warm', 'Mild', 'Cool', 'Cold', 'Rainy', 'Snowy',
    'Windy', 'Humid', 'Dry', 'Spring', 'Summer', 'Fall', 'Winter'
  ],
  fits: [
    'Loose', 'Relaxed', 'Regular', 'Fitted', 'Slim', 'Skinny',
    'Oversized', 'Tailored', 'Structured', 'Flowy', 'Boxy',
    'Cropped', 'Full Length', 'High Waisted', 'Low Waisted'
  ]
};

// Helper function to determine occasions based on item attributes
function determineOccasions(item) {
  const occasions = new Set(item.occasion || []);
  const style = item.style || [];
  const material = item.metadata?.visualAttributes?.material?.toLowerCase() || '';
  const formality = item.metadata?.visualAttributes?.formalLevel?.toLowerCase() || '';
  const pattern = item.metadata?.visualAttributes?.pattern?.toLowerCase() || '';

  // Add occasions based on style
  if (style.includes('Formal') || formality === 'formal') {
    occasions.add('Wedding');
    occasions.add('Funeral');
    occasions.add('Formal');
  }
  if (style.includes('Business')) {
    occasions.add('Business');
    occasions.add('Interview');
    occasions.add('Conference');
  }
  if (style.includes('Casual')) {
    occasions.add('Casual');
    occasions.add('Brunch');
    occasions.add('Dinner');
  }
  if (material.includes('linen') || material.includes('cotton')) {
    occasions.add('Beach');
    occasions.add('Vacation');
  }
  if (pattern.includes('floral') || pattern.includes('print')) {
    occasions.add('Party');
    occasions.add('Date');
  }

  return Array.from(occasions);
}

// Helper function to determine styles based on item attributes and gender
function determineStyles(item) {
  const styles = new Set(item.style || []);
  const material = item.metadata?.visualAttributes?.material?.toLowerCase() || '';
  const pattern = item.metadata?.visualAttributes?.pattern?.toLowerCase() || '';
  const silhouette = item.metadata?.visualAttributes?.silhouette?.toLowerCase() || '';
  const gender = item.gender || 'male';

  // Add styles based on material and pattern, considering gender
  if (material.includes('linen') && (item.type === 'shorts' || item.type === 'pants')) {
    if (gender === 'female' || gender === 'unisex') {
      styles.add('Coastal Chic');
    }
  }
  if (pattern.includes('abstract') || pattern.includes('geometric')) {
    styles.add('Avant Garde');
  }
  if (silhouette.includes('straight') && material.includes('cotton')) {
    styles.add('Minimalist');
  }
  if (material.includes('denim')) {
    styles.add('Casual');
    styles.add('Streetwear');
  }

  return Array.from(styles);
}

// Helper function to determine moods based on item attributes
function determineMoods(item) {
  const moods = new Set();
  const pattern = item.metadata?.visualAttributes?.pattern?.toLowerCase() || '';
  const color = item.color?.toLowerCase() || '';
  const style = item.style || [];

  if (pattern.includes('floral') || color.includes('bright')) {
    moods.add('Playful');
  }
  if (style.includes('Formal')) {
    moods.add('Serious');
    moods.add('Professional');
  }
  if (style.includes('Casual')) {
    moods.add('Relaxed');
  }
  if (pattern.includes('bold') || color.includes('vibrant')) {
    moods.add('Bold');
  }

  return Array.from(moods);
}

// Helper function to determine weather compatibility
function determineWeather(item) {
  const weather = new Set();
  const material = item.metadata?.visualAttributes?.material?.toLowerCase() || '';
  const season = item.season || [];
  const tempCompatibility = item.metadata?.visualAttributes?.temperatureCompatibility || {};

  // Add weather based on material
  if (material.includes('wool') || material.includes('fleece')) {
    weather.add('Cold');
    weather.add('Winter');
  }
  if (material.includes('linen') || material.includes('cotton')) {
    weather.add('Hot');
    weather.add('Warm');
    weather.add('Summer');
  }
  if (material.includes('waterproof')) {
    weather.add('Rainy');
  }

  // Add weather based on season
  season.forEach(s => weather.add(s.charAt(0).toUpperCase() + s.slice(1)));

  return Array.from(weather);
}

// Helper function to determine body type compatibility
function determineBodyTypes(item) {
  const bodyTypes = new Set();
  const fit = item.metadata?.visualAttributes?.fit?.toLowerCase() || '';
  const silhouette = item.metadata?.visualAttributes?.silhouette?.toLowerCase() || '';

  if (fit === 'loose' || fit === 'relaxed') {
    bodyTypes.add('Rectangle');
    bodyTypes.add('Apple');
  }
  if (fit === 'fitted' || fit === 'slim') {
    bodyTypes.add('Hourglass');
    bodyTypes.add('Pear');
  }
  if (silhouette.includes('straight')) {
    bodyTypes.add('Rectangle');
  }

  return Array.from(bodyTypes);
}

async function updateWardrobeMetadata() {
  try {
    console.log('Starting wardrobe metadata update...');
    
    // Get all wardrobe items
    const snapshot = await db.collection('wardrobe').get();
    
    console.log(`Found ${snapshot.size} items to process`);
    
    let updatedCount = 0;
    
    // Process each item
    for (const doc of snapshot.docs) {
      const item = doc.data();
      const updates = {
        occasion: determineOccasions(item),
        style: determineStyles(item),
        mood: determineMoods(item),
        weatherCompatibility: determineWeather(item),
        bodyTypeCompatibility: determineBodyTypes(item),
        gender: item.gender || 'male', // Add gender field, defaulting to 'male'
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      };

      // Update the document
      await doc.ref.update(updates);
      updatedCount++;
      
      if (updatedCount % 10 === 0) {
        console.log(`Updated ${updatedCount} items...`);
      }
    }

    console.log(`\nUpdate complete! Updated ${updatedCount} items.`);

  } catch (error) {
    console.error('Error updating wardrobe metadata:', error);
  } finally {
    // Clean up
    admin.app().delete();
  }
}

// Run the update
updateWardrobeMetadata(); 