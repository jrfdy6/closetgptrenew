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

// Helper to capitalize first letter
function capitalize(str: string) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}

// Helper to check if a word starts with a vowel sound
function startsWithVowel(word: string) {
  return /^[aeiou]/i.test(word);
}

// List of known accessory subtypes
const accessorySubtypes = [
  'belt', 'scarf', 'hat', 'watch', 'gloves', 'tie', 'bowtie', 'bracelet', 'necklace', 'ring', 'wallet', 'bag', 'purse', 'sunglasses', 'earrings', 'cufflinks', 'beanie', 'cap', 'headband', 'hairclip', 'brooch', 'pin', 'shawl', 'wrap', 'mask', 'lanyard', 'keychain', 'umbrella', 'suspenders', 'backpack', 'duffle', 'tote', 'clutch', 'fanny pack', 'crossbody', 'satchel', 'messenger', 'briefcase', 'case', 'pouch', 'coin purse', 'card holder', 'passport holder', 'glasses', 'visor', 'mitten', 'muffler', 'earmuffs', 'anklet', 'charm', 'chain', 'strap', 'strap cover', 'strap pad', 'strap extender', 'strap adjuster', 'strap keeper', 'strap lock', 'strap loop', 'strap ring', 'strap slider', 'strap tab', 'strap tip', 'strap buckle', 'strap button', 'strap clip', 'strap hook', 'strap latch', 'strap rivet', 'strap screw', 'strap snap', 'strap stud', 'strap tie', 'strap toggle', 'strap washer', 'strap zip', 'strap zipper', 'strap zip pull', 'strap zip slider', 'strap zip stop', 'strap zip tab', 'strap zip tip', 'strap zip toggle', 'strap zip washer', 'strap zip zipper', 'strap zip zip pull', 'strap zip zip slider', 'strap zip zip stop', 'strap zip zip tab', 'strap zip zip tip', 'strap zip zip toggle', 'strap zip zip washer', 'strap zip zip zipper'
];

function buildNaturalName(item: any): string {
  const fit = item.metadata?.visualAttributes?.fit;
  const sleeve = item.metadata?.visualAttributes?.sleeveLength;
  const pattern = item.metadata?.visualAttributes?.pattern;
  const texture = item.metadata?.visualAttributes?.textureStyle;
  // Prefer subType, then visualAttributes.type, then itemMetadata.type, then type
  let type = item.subType || item.metadata?.visualAttributes?.type || item.metadata?.itemMetadata?.type || item.type || '';
  // For accessories, use subType if it's a known accessory subtype
  if ((item.type === 'accessory' || type === 'accessory') && item.subType && accessorySubtypes.includes(item.subType.toLowerCase())) {
    type = item.subType;
  }
  const brand = item.brand || item.metadata?.itemMetadata?.brand || '';
  // Compose the features, skipping empty
  const features = [fit, sleeve, pattern, texture].filter(Boolean).map(s => s.toLowerCase());
  // Compose the main phrase
  let phrase = '';
  if (features.length) {
    phrase = features.join(', ');
  }
  if (type) {
    phrase = phrase ? `${phrase} ${type.toLowerCase()}` : type.toLowerCase();
  }
  // Determine 'a' or 'an'
  let article = 'A';
  if (phrase && startsWithVowel(phrase.trim())) {
    article = 'An';
  }
  // Compose brand part
  const brandPart = brand ? ` by ${capitalize(brand)}` : '';
  // Final sentence
  return phrase ? `${article} ${phrase}${brandPart}` : (brand ? `${capitalize(brand)}` : '');
}

async function updateAllWardrobeNames() {
  const snapshot = await db.collection('wardrobe').get();
  let count = 0;
  for (const doc of snapshot.docs) {
    const item = doc.data();
    const newName = buildNaturalName(item);
    if (newName && newName !== item.name) {
      await doc.ref.update({ name: newName });
      count++;
      console.log(`Updated ${doc.id}: ${newName}`);
    }
  }
  console.log(`Updated ${count} items with new natural language names.`);
}

updateAllWardrobeNames().catch(console.error); 