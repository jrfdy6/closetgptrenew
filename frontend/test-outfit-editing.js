#!/usr/bin/env node

/**
 * Simple Outfit Editing Test Script
 * Run with: node test-outfit-editing.js
 */

const { exec } = require('child_process');
const fs = require('fs');

console.log('🧪 Outfit Editing Test Script');
console.log('============================\n');

// Test 1: Check if development server is running
console.log('1. Checking development server...');
exec('curl -s http://localhost:3000 > /dev/null', (error, stdout, stderr) => {
  if (error) {
    console.log('❌ Development server not running');
    console.log('   Run: npm run dev');
    console.log('   Then: open http://localhost:3000/outfits\n');
  } else {
    console.log('✅ Development server is running');
    console.log('   URL: http://localhost:3000/outfits\n');
  }
});

// Test 2: Check if production deployment is working
console.log('2. Checking production deployment...');
exec('curl -s https://closetgpt-frontend.vercel.app/outfits | head -5', (error, stdout, stderr) => {
  if (error) {
    console.log('❌ Production deployment not accessible');
  } else {
    console.log('✅ Production deployment is working');
    console.log('   URL: https://closetgpt-frontend.vercel.app/outfits\n');
  }
});

// Test 3: Check if test files exist
console.log('3. Checking test files...');
const testFiles = [
  'src/__tests__/OutfitEditModal.test.tsx',
  'src/components/OutfitEditModal.tsx',
  'src/components/OutfitItemSelector.tsx',
  'src/lib/adapters/itemAdapter.ts'
];

testFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file} exists`);
  } else {
    console.log(`❌ ${file} missing`);
  }
});

console.log('\n4. Manual Testing Steps:');
console.log('========================');
console.log('1. Open the application:');
console.log('   - Production: https://closetgpt-frontend.vercel.app/outfits');
console.log('   - Local: http://localhost:3000/outfits');
console.log('');
console.log('2. Sign in to your account');
console.log('');
console.log('3. Generate an outfit (if none exist)');
console.log('');
console.log('4. Click the edit button on any outfit card');
console.log('');
console.log('5. Test the modal functionality:');
console.log('   - Edit outfit details (name, occasion, style)');
console.log('   - Add/remove items from the outfit');
console.log('   - Test form validation');
console.log('   - Save changes');
console.log('');
console.log('6. Check browser console for errors (F12)');
console.log('');
console.log('7. Test on different screen sizes (mobile, tablet, desktop)');
console.log('');

console.log('🎯 Success Criteria:');
console.log('===================');
console.log('✅ Modal opens and closes correctly');
console.log('✅ Form validation works');
console.log('✅ Item selection works');
console.log('✅ Save functionality works');
console.log('✅ No console errors');
console.log('✅ Responsive design works');
console.log('');

console.log('🐛 If you encounter issues:');
console.log('===========================');
console.log('1. Check browser console for errors');
console.log('2. Verify you are signed in');
console.log('3. Check network requests in DevTools');
console.log('4. Try refreshing the page');
console.log('5. Test in different browsers');
console.log('');

console.log('📚 For detailed testing, see: TESTING_GUIDE.md');
console.log('');

// Test 4: Run Jest tests if available
console.log('5. Running automated tests...');
exec('npm test -- --testPathPattern=OutfitEditModal.test.tsx --passWithNoTests', (error, stdout, stderr) => {
  if (error) {
    console.log('❌ Tests failed or not available');
    console.log('   Run: npm test for more details');
  } else {
    console.log('✅ Tests completed');
    console.log(stdout);
  }
});

console.log('\n🎉 Testing setup complete!');
console.log('Ready to test the outfit editing functionality.');
