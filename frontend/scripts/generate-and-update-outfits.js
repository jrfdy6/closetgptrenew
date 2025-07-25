const fs = require('fs');
const path = require('path');
const OpenAI = require('openai');

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || 'your-openai-api-key-here'
});

// Create images directory
const imagesDir = path.join(__dirname, '../public/images/outfit-quiz');
if (!fs.existsSync(imagesDir)) {
  fs.mkdirSync(imagesDir, { recursive: true });
}

// Get all prompt files
const promptsDir = path.join(__dirname, '../prompts');
const promptFiles = fs.readdirSync(promptsDir).filter(file => file.endsWith('-prompt.txt'));

console.log(`Found ${promptFiles.length} prompt files`);

async function generateImage(promptFile) {
  const outfitId = promptFile.replace('-prompt.txt', '');
  const promptPath = path.join(promptsDir, promptFile);
  const prompt = fs.readFileSync(promptPath, 'utf8');
  
  const outputPath = path.join(imagesDir, `${outfitId}.png`);
  
  // Skip if image already exists
  if (fs.existsSync(outputPath)) {
    console.log(`Skipping ${outfitId}.png - already exists`);
    return;
  }

  try {
    console.log(`Generating image for ${outfitId}...`);
    
    const response = await openai.images.generate({
      model: "dall-e-3",
      prompt: prompt,
      n: 1,
      size: "1024x1024",
      quality: "standard",
      response_format: "b64_json"
    });

    // Save the image
    const imageBuffer = Buffer.from(response.data[0].b64_json, 'base64');
    fs.writeFileSync(outputPath, imageBuffer);
    
    console.log(`✅ Generated ${outfitId}.png`);
    
    // Add a small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 1000));
    
  } catch (error) {
    console.error(`❌ Error generating ${outfitId}:`, error.message);
  }
}

function updateOutfitData() {
  console.log('\n🔄 Updating outfit data to use PNG extensions...');
  
  // Path to the outfit data file
  const outfitDataPath = path.join(__dirname, '../src/data/outfitBank.ts');
  
  if (!fs.existsSync(outfitDataPath)) {
    console.log('⚠️  Outfit data file not found, skipping update');
    return;
  }

  // Read the current outfit data
  let outfitData = fs.readFileSync(outfitDataPath, 'utf8');
  
  // Replace all .svg extensions with .png
  const updatedData = outfitData.replace(/\.svg/g, '.png');
  
  // Write the updated data back
  fs.writeFileSync(outfitDataPath, updatedData);
  
  console.log('✅ Updated outfit data to use .png extensions');
  
  // Also update the outfit quiz component if it exists
  const outfitQuizPath = path.join(__dirname, '../src/components/onboarding/steps/StepOutfitQuiz.tsx');
  if (fs.existsSync(outfitQuizPath)) {
    let outfitQuizData = fs.readFileSync(outfitQuizPath, 'utf8');
    const updatedQuizData = outfitQuizData.replace(/\.svg/g, '.png');
    fs.writeFileSync(outfitQuizPath, updatedQuizData);
    console.log('✅ Updated outfit quiz component to use .png extensions');
  }
}

async function generateAllImages() {
  console.log('🚀 Starting image generation...');
  console.log(`Images will be saved to: ${imagesDir}`);
  console.log('');
  
  for (const promptFile of promptFiles) {
    await generateImage(promptFile);
  }
  
  console.log('\n🎉 Image generation complete!');
}

async function main() {
  // Check if OpenAI API key is set
  if (!process.env.OPENAI_API_KEY) {
    console.error('❌ OPENAI_API_KEY environment variable is not set');
    console.log('Please set your OpenAI API key:');
    console.log('export OPENAI_API_KEY="your-api-key-here"');
    console.log('Or add it to your .env file');
    process.exit(1);
  }

  try {
    // Generate all images
    await generateAllImages();
    
    // Update outfit data
    updateOutfitData();
    
    console.log('\n🎉 Complete! All outfit images generated and data updated!');
    console.log('\nNext steps:');
    console.log('1. Test the images in your app');
    console.log('2. Run the development server: npm run dev');
    console.log('3. Navigate to the onboarding flow to see the new images');
    
  } catch (error) {
    console.error('❌ Error in main process:', error);
  }
}

// Run the script
main(); 