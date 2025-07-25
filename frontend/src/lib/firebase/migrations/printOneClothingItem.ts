import admin from 'firebase-admin';
import { readFileSync } from 'fs';
import { resolve } from 'path';

// Load service account
const serviceAccount = JSON.parse(
  readFileSync(resolve(__dirname, '../../../../serviceAccountKey.json'), 'utf8')
);

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: 'https://closetgptrenew.firebaseio.com',
  });
}

const db = admin.firestore();

async function printOneClothingItem() {
  const snapshot = await db.collection('wardrobe').limit(1).get();
  if (snapshot.empty) {
    console.log('No items found.');
    return;
  }
  snapshot.forEach(doc => {
    console.log(JSON.stringify(doc.data(), null, 2));
  });
  process.exit(0);
}

printOneClothingItem().catch(err => {
  console.error('Error fetching clothing item:', err);
  process.exit(1);
}); 