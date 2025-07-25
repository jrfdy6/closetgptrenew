const admin = require('firebase-admin');
const path = require('path');

// Initialize Firebase Admin
const serviceAccount = require('../serviceAccountKey.json');
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

const sampleTrends = [
  {
    name: "Quiet Luxury",
    category: "Luxury",
    subCategories: ["Minimalist", "High-End"],
    season: "All Seasons",
    popularity: 95,
    description: "Understated elegance and premium quality without flashy logos",
    keyItems: ["Cashmere sweaters", "Tailored suits", "Leather accessories"],
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    gender: "Unisex",
    priceRange: "High",
    sustainability: "Medium",
    culturalInfluence: "European",
    colorPalette: ["Neutral", "Cream", "Black", "Navy"],
    fabricTypes: ["Cashmere", "Silk", "Wool", "Leather"]
  },
  {
    name: "Gorpcore",
    category: "Outdoor",
    subCategories: ["Technical", "Urban"],
    season: "All Seasons",
    popularity: 85,
    description: "Outdoor technical wear adapted for urban environments",
    keyItems: ["Hiking boots", "Technical jackets", "Cargo pants"],
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    gender: "Unisex",
    priceRange: "Medium-High",
    sustainability: "High",
    culturalInfluence: "Outdoor Sports",
    colorPalette: ["Earth tones", "Technical colors", "Neon accents"],
    fabricTypes: ["Gore-Tex", "Nylon", "Ripstop"]
  },
  {
    name: "Old Money",
    category: "Classic",
    subCategories: ["Preppy", "Heritage"],
    season: "All Seasons",
    popularity: 90,
    description: "Timeless, high-quality pieces that exude wealth and sophistication",
    keyItems: ["Blazers", "Polo shirts", "Loafers"],
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    gender: "Unisex",
    priceRange: "High",
    sustainability: "Medium",
    culturalInfluence: "American East Coast",
    colorPalette: ["Navy", "Burgundy", "Cream", "Forest Green"],
    fabricTypes: ["Wool", "Cotton", "Tweed", "Leather"]
  }
];

async function seedTrends() {
  console.log('Starting to seed trends...');
  
  for (const trend of sampleTrends) {
    try {
      await db.collection('trends').add(trend);
      console.log(`Successfully added trend: ${trend.name}`);
    } catch (error) {
      console.error(`Error adding trend ${trend.name}:`, error);
    }
  }
  
  console.log('Finished seeding trends');
}

// Run the seeding function
seedTrends()
  .then(() => {
    console.log('Seeding completed successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Error during seeding:', error);
    process.exit(1);
  }); 