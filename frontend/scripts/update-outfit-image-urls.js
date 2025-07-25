const fs = require('fs');
const path = require('path');

// Path to the outfit quiz component file
const outfitQuizPath = path.join(__dirname, '../src/components/onboarding/steps/StepOutfitStyleQuiz.tsx');

if (!fs.existsSync(outfitQuizPath)) {
  console.error('❌ Could not find StepOutfitStyleQuiz.tsx');
  process.exit(1);
}

// Read the current outfit quiz data
let outfitQuizData = fs.readFileSync(outfitQuizPath, 'utf8');

// Replace all .svg extensions with .png
const updatedQuizData = outfitQuizData.replace(/\.svg/g, '.png');

// Write the updated data back
fs.writeFileSync(outfitQuizPath, updatedQuizData);

console.log('✅ Updated StepOutfitStyleQuiz.tsx to use .png extensions for all imageUrl properties!'); 