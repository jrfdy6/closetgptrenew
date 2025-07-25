const admin = require('firebase-admin');
const path = require('path');

// Initialize Firebase Admin
const serviceAccount = require('./backend/service-account-key.json');
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

const STYLES = [
  'Dark Academia',
  'Old Money',
  'Streetwear',
  'Y2K',
  'Minimalist',
  'Boho',
  'Preppy',
  'Grunge',
  'Classic',
  'Techwear',
  'Androgynous',
  'Coastal Chic',
  'Business Casual',
  'Avant-Garde',
  'Cottagecore',
  'Edgy',
  'Athleisure',
  'Casual Cool',
  'Romantic',
  'Artsy'
];

const OCCASIONS = [
  'Casual',
  'Business Casual',
  'Formal',
  'Gala',
  'Party',
  'Date Night',
  'Work',
  'Interview',
  'Brunch',
  'Wedding Guest',
  'Cocktail',
  'Travel',
  'Airport',
  'Loungewear',
  'Beach',
  'Vacation',
  'Festival',
  'Rainy Day',
  'Snow Day',
  'Hot Weather',
  'Cold Weather',
  'Night Out',
  'Athletic / Gym',
  'School',
  'Holiday',
  'Concert',
  'Errands',
  'Chilly Evening',
  'Museum / Gallery',
  'First Date',
  'Business Formal',
  'Funeral / Memorial',
  'Fashion Event',
  'Outdoor Gathering'
];

const MALE_STYLES = [
  'Minimalist',
  'Preppy',
  'Streetwear',
  'Classic',
  'Business Casual',
  'Techwear',
  'Athleisure',
  'Casual Cool'
];

// Example query parameters - modify these to match your search criteria
const queryParams = {
  occasion: 'Vacation',
  style: 'Old Money',
  mood: 'Playful',
  type: ['pants', 'shorts']
};

async function queryWardrobeItems(params) {
  try {
    console.log('\nSearching for items matching criteria:');
    console.log('=====================================');
    Object.entries(params).forEach(([key, value]) => {
      if (value) console.log(`${key}: ${Array.isArray(value) ? value.join(', ') : value}`);
    });
    console.log('=====================================\n');

    // Start with the base query
    let query = db.collection('wardrobe');

    // Add filters based on provided parameters
    if (params.type) {
      if (Array.isArray(params.type)) {
        // Firestore supports 'in' queries for up to 10 values
        query = query.where('type', 'in', params.type);
      } else {
        query = query.where('type', '==', params.type);
      }
    }

    // Execute the query
    const snapshot = await query.get();

    // Filter results in memory for array fields and complex conditions
    const results = snapshot.docs
      .map(doc => ({ id: doc.id, ...doc.data() }))
      .filter(item => {
        // Check occasion (case-insensitive)
        if (params.occasion && !item.occasion?.map(o => o.toLowerCase()).includes(params.occasion.toLowerCase())) {
          return false;
        }

        // Check style (case-insensitive)
        if (params.style && !item.style?.map(s => s.toLowerCase()).includes(params.style.toLowerCase())) {
          return false;
        }

        // Check mood (case-insensitive)
        if (params.mood && !item.mood?.map(m => m.toLowerCase()).includes(params.mood.toLowerCase())) {
          return false;
        }

        // Check body type compatibility
        if (params.bodyType && !item.bodyTypeCompatibility?.includes(params.bodyType)) {
          return false;
        }

        // Check fit
        if (params.fit && item.metadata?.visualAttributes?.fit?.toLowerCase() !== params.fit.toLowerCase()) {
          return false;
        }

        // Check weather compatibility
        if (params.weather && !item.weatherCompatibility?.includes(params.weather)) {
          return false;
        }

        // Check material
        if (params.material && !item.metadata?.visualAttributes?.material?.toLowerCase().includes(params.material.toLowerCase())) {
          return false;
        }

        // Check color
        if (params.color && !item.color?.toLowerCase().includes(params.color.toLowerCase())) {
          return false;
        }

        return true;
      });

    // Print results
    if (results.length === 0) {
      console.log('No items found matching the criteria.');
      return;
    }

    console.log(`Found ${results.length} matching items:\n`);

    results.forEach((item, index) => {
      console.log(`Item ${index + 1}:`);
      console.log(`ID: ${item.id}`);
      console.log(`Name: ${item.name || 'N/A'}`);
      console.log(`Type: ${item.type}`);
      console.log(`Gender: ${item.gender || 'N/A'}`);
      console.log(`Colors: ${item.color || 'N/A'}`);
      console.log(`Material: ${item.metadata?.visualAttributes?.material || 'N/A'}`);
      console.log(`Fit: ${item.metadata?.visualAttributes?.fit || 'N/A'}`);
      console.log(`Style: ${item.style?.join(', ') || 'N/A'}`);
      console.log(`Occasions: ${item.occasion?.join(', ') || 'N/A'}`);
      console.log(`Moods: ${item.mood?.join(', ') || 'N/A'}`);
      console.log(`Weather Compatibility: ${item.weatherCompatibility?.join(', ') || 'N/A'}`);
      console.log(`Body Type Compatibility: ${item.bodyTypeCompatibility?.join(', ') || 'N/A'}`);
      console.log(`Season: ${item.season?.join(', ') || 'N/A'}`);
      console.log(`Brand: ${item.brand || 'N/A'}`);
      console.log('-----------------------\n');
    });

  } catch (error) {
    console.error('Error querying wardrobe items:', error);
  } finally {
    // Clean up
    admin.app().delete();
  }
}

async function generateStyleOccasionMatrix() {
  try {
    console.log('Generating style and occasion matrix (non-zero, male/unisex styles only)...');
    
    // Get all wardrobe items
    const snapshot = await db.collection('wardrobe').get();
    
    // Initialize the matrix
    const matrix = {};
    MALE_STYLES.forEach(style => {
      matrix[style] = {};
      OCCASIONS.forEach(occasion => {
        matrix[style][occasion] = 0;
      });
    });

    // Count items for each style and occasion combination
    snapshot.docs.forEach(doc => {
      const item = doc.data();
      const styles = item.style || [];
      const occasions = item.occasion || [];

      styles.forEach(style => {
        if (MALE_STYLES.includes(style)) {
          occasions.forEach(occasion => {
            if (matrix[style] && matrix[style][occasion] !== undefined) {
              matrix[style][occasion]++;
            }
          });
        }
      });
    });

    // Print the matrix (only non-zero entries)
    console.log('\nFiltered Style and Occasion Matrix (Non-Zero Entries):');
    console.log('=====================================');
    MALE_STYLES.forEach(style => {
      let hasNonZero = false;
      OCCASIONS.forEach(occasion => {
        if (matrix[style][occasion] > 0) {
          if (!hasNonZero) {
            console.log(`\n${style}:`);
            hasNonZero = true;
          }
          console.log(`  ${occasion}: ${matrix[style][occasion]}`);
        }
      });
    });
    console.log('=====================================');

  } catch (error) {
    console.error('Error generating style and occasion matrix:', error);
  } finally {
    // Clean up
    admin.app().delete();
  }
}

// Run the query with the example parameters
queryWardrobeItems(queryParams);

// Run the matrix generation
generateStyleOccasionMatrix(); 