import { config } from 'dotenv';
import { resolve } from 'path';

// Load environment variables from .env.local
config({ path: resolve(__dirname, '../../.env.local') });

import { updateClothingSchema } from '../lib/firebase/migrations/updateClothingSchema';

async function runMigration() {
  try {
    console.log('Starting migration...');
    await updateClothingSchema();
    console.log('Migration completed successfully');
    process.exit(0);
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

runMigration(); 