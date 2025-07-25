const admin = require('firebase-admin');
const path = require('path');

// Initialize Firebase Admin
const serviceAccount = require('./backend/service-account-key.json');
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

async function getVacationBottoms() {
  try {
    // Query for pants and shorts tagged for vacation
    const snapshot = await db.collection('wardrobe')
      .where('type', 'in', ['pants', 'shorts'])
      .where('occasion', 'array-contains', 'Vacation')
      .get();

    console.log('\nFound vacation bottoms:');
    console.log('=======================');

    if (snapshot.empty) {
      console.log('No vacation bottoms found. Trying alternative search...');
      
      // Try searching for casual/beach style items
      const casualSnapshot = await db.collection('wardrobe')
        .where('type', 'in', ['pants', 'shorts'])
        .where('style', 'array-contains', 'Casual')
        .get();

      console.log('\nFound casual bottoms:');
      console.log('=====================');

      casualSnapshot.forEach(doc => {
        const item = doc.data();
        console.log(`\nItem ID: ${doc.id}`);
        console.log(`Name: ${item.name || 'N/A'}`);
        console.log(`Type: ${item.type}`);
        console.log(`Colors: ${item.color || 'N/A'}`);
        console.log(`Material: ${item.metadata?.visualAttributes?.material || 'N/A'}`);
        console.log(`Fit: ${item.metadata?.visualAttributes?.fit || 'N/A'}`);
        console.log(`Style: ${item.style?.join(', ') || 'N/A'}`);
        console.log(`Occasions: ${item.occasion?.join(', ') || 'N/A'}`);
        console.log(`Season: ${item.season?.join(', ') || 'N/A'}`);
        console.log(`Brand: ${item.brand || 'N/A'}`);
        console.log('-----------------------');
      });

      console.log(`\nTotal casual items found: ${casualSnapshot.size}`);
      return;
    }

    snapshot.forEach(doc => {
      const item = doc.data();
      console.log(`\nItem ID: ${doc.id}`);
      console.log(`Name: ${item.name || 'N/A'}`);
      console.log(`Type: ${item.type}`);
      console.log(`Colors: ${item.color || 'N/A'}`);
      console.log(`Material: ${item.metadata?.visualAttributes?.material || 'N/A'}`);
      console.log(`Fit: ${item.metadata?.visualAttributes?.fit || 'N/A'}`);
      console.log(`Style: ${item.style?.join(', ') || 'N/A'}`);
      console.log(`Occasions: ${item.occasion?.join(', ') || 'N/A'}`);
      console.log(`Season: ${item.season?.join(', ') || 'N/A'}`);
      console.log(`Brand: ${item.brand || 'N/A'}`);
      console.log('-----------------------');
    });

    console.log(`\nTotal vacation items found: ${snapshot.size}`);

  } catch (error) {
    console.error('Error querying vacation bottoms:', error);
  } finally {
    // Clean up
    admin.app().delete();
  }
}

// Run the query
getVacationBottoms(); 