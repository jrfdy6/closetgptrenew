import { updateMetadata } from '../lib/firebase/migrations/updateMetadata';

async function runMigration() {
  console.log('Starting metadata migration script...');
  try {
    const result = await updateMetadata();
    if (result.success) {
      console.log(`Migration completed successfully. Updated ${result.updatedCount} items.`);
    } else {
      console.error('Migration failed:', result.error);
    }
  } catch (error) {
    console.error('Error running migration:', error);
  }
}

// Run the migration
runMigration(); 