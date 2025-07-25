import { seedTrends } from "../lib/firebase/seedTrends";

async function main() {
  try {
    console.log("Starting database seeding...");
    
    // Seed trends
    await seedTrends();
    
    console.log("Database seeding completed successfully!");
  } catch (error) {
    console.error("Error during database seeding:", error);
    process.exit(1);
  }
}

main(); 