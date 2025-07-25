import admin from 'firebase-admin';
import { readFileSync } from 'fs';
import { resolve } from 'path';

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

async function updateClothingItem(itemId: string) {
  const ref = db.collection('wardrobe').doc(itemId);
  await ref.update({
    name: 'Abercrombie & Fitch Ribbed Boxy Short-Sleeve Sweatshirt',
    subType: 'short_sleeve_sweatshirt',
    style: ['Boxy', 'Ribbed', 'Short Sleeve', 'Sweatshirt', 'Casual'],
    'metadata.visualAttributes.sleeveLength': 'Short',
    'metadata.visualAttributes.pattern': 'Textured',
    'metadata.visualAttributes.textureStyle': 'Ribbed',
    'metadata.visualAttributes.fit': 'boxy',
    'metadata.visualAttributes.material': 'Cotton',
    'metadata.naturalDescription': 'A ribbed, boxy, short-sleeve sweatshirt from Abercrombie & Fitch. Can be worn as an outer layer or under a jacket.'
  });
  console.log('Item updated!');
}

updateClothingItem('006crwqcyyl7kmby62lrf').catch(console.error); 