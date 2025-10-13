#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Configuration
const OLD_URL = 'https://acceptable-wisdom-production-ac06.up.railway.app';
const NEW_URL = 'process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:3001"';

// Find all TypeScript and TypeScript React files
const files = glob.sync('src/**/*.{ts,tsx}');

let updatedFiles = 0;
let totalReplacements = 0;

files.forEach(filePath => {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    
    // Replace the old URL with the new one
    const newContent = content.replace(new RegExp(OLD_URL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), NEW_URL);
    
    if (newContent !== originalContent) {
      fs.writeFileSync(filePath, newContent, 'utf8');
      updatedFiles++;
      
      const replacements = (content.match(new RegExp(OLD_URL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
      totalReplacements += replacements;
      
      console.log(`✅ Updated ${filePath} (${replacements} replacements)`);
    }
  } catch (error) {
    console.error(`❌ Error updating ${filePath}:`, error.message);
  }
});

console.log(`\n🎉 Update complete!`);
console.log(`📁 Updated ${updatedFiles} files`);
console.log(`🔄 Made ${totalReplacements} total replacements`);
console.log(`\n💡 Now your frontend will use the backend URL from your .env.local file:`);
console.log(`   NEXT_PUBLIC_BACKEND_URL=https://closetgptrenew-production.up.railway.app`);
console.log(`\n🔄 Restart your frontend server to apply the changes!`);
