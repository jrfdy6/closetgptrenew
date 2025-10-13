#!/usr/bin/env node

const fs = require('fs');
const glob = require('glob');

// Configuration
const MALFORMED_URL = 'process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:3001"';
const CORRECT_URL = 'http://localhost:3001';

// Find all TypeScript and TypeScript React files
const files = glob.sync('src/**/*.{ts,tsx}');

let updatedFiles = 0;
let totalReplacements = 0;

files.forEach(filePath => {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    
    // Replace the malformed URL with the correct one
    const newContent = content.replace(new RegExp(MALFORMED_URL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), CORRECT_URL);
    
    if (newContent !== originalContent) {
      fs.writeFileSync(filePath, newContent, 'utf8');
      updatedFiles++;
      
      const replacements = (content.match(new RegExp(MALFORMED_URL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
      totalReplacements += replacements;
      
      console.log(`✅ Fixed ${filePath} (${replacements} replacements)`);
    }
  } catch (error) {
    console.error(`❌ Error fixing ${filePath}:`, error.message);
  }
});

console.log(`\n🎉 Fix complete!`);
console.log(`📁 Fixed ${updatedFiles} files`);
console.log(`🔄 Made ${totalReplacements} total replacements`);
console.log(`\n💡 Now your frontend will properly use the environment variable:`);
console.log(`   NEXT_PUBLIC_BACKEND_URL=https://closetgptrenew-backend-production.up.railway.app`);
console.log(`\n🔄 Restart your frontend server to apply the changes!`);
