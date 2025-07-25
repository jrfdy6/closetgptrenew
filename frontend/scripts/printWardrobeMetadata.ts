// printWardrobeMetadata.ts
// Usage: npx ts-node scripts/printWardrobeMetadata.ts

import readline from 'readline';
import { getWardrobeItems } from '../src/lib/firebase/wardrobeService';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question('Enter your userId: ', async (userId) => {
  if (!userId) {
    console.error('No userId provided. Exiting.');
    rl.close();
    process.exit(1);
  }
  const result = await getWardrobeItems(userId.trim());
  if (!result.success || !result.data) {
    console.error('Failed to fetch wardrobe items:', result.error);
    rl.close();
    process.exit(1);
  }
  const metadataArray = result.data.map(item => item.metadata);
  console.log(JSON.stringify(metadataArray, null, 2));
  rl.close();
}); 