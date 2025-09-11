// Debug script for production outfit edit button
// Run this in the browser console on https://closetgpt-frontend.vercel.app/outfits

console.log('🔍 Debugging Outfit Edit Button in Production');
console.log('==============================================');

// Check if React is loaded
console.log('1. React loaded:', typeof React !== 'undefined');

// Check if the page is fully loaded
console.log('2. Page loaded:', document.readyState);

// Look for outfit cards
const outfitCards = document.querySelectorAll('[data-testid="outfit-card"], .outfit-card, [class*="outfit"]');
console.log('3. Outfit cards found:', outfitCards.length);

// Look for edit buttons
const editButtons = document.querySelectorAll('button[onclick*="edit"], button[onclick*="Edit"], [class*="edit"]');
console.log('4. Edit buttons found:', editButtons.length);

// Look for pencil icons
const pencilIcons = document.querySelectorAll('svg[class*="edit"], [class*="pencil"], [class*="Edit"]');
console.log('5. Pencil icons found:', pencilIcons.length);

// Check for any JavaScript errors
console.log('6. Console errors:', window.console.errors || []);

// Test clicking on any button
console.log('7. Testing button clicks...');
const allButtons = document.querySelectorAll('button');
console.log('   Total buttons found:', allButtons.length);

// Look for the specific edit button pattern
const editButtonPattern = document.querySelectorAll('button:has(svg[class*="edit"]), button[onclick*="handleEdit"]');
console.log('8. Edit button pattern matches:', editButtonPattern.length);

// Check if the modal component is loaded
const modalElements = document.querySelectorAll('[class*="modal"], [class*="Modal"]');
console.log('9. Modal elements found:', modalElements.length);

// Check for any React components
const reactElements = document.querySelectorAll('[data-reactroot], [data-react-helmet]');
console.log('10. React elements found:', reactElements.length);

// Test function to simulate edit button click
function testEditButton() {
    console.log('🧪 Testing edit button click...');
    
    // Find the first edit button
    const editBtn = document.querySelector('button:has(svg[class*="edit"]), button[onclick*="handleEdit"]');
    
    if (editBtn) {
        console.log('✅ Edit button found, clicking...');
        editBtn.click();
        
        // Check if modal opened
        setTimeout(() => {
            const modal = document.querySelector('[class*="modal"], [class*="Modal"]');
            if (modal && modal.style.display !== 'none') {
                console.log('✅ Modal opened successfully!');
            } else {
                console.log('❌ Modal did not open');
            }
        }, 1000);
    } else {
        console.log('❌ No edit button found');
    }
}

// Make test function available globally
window.testEditButton = testEditButton;

console.log('==============================================');
console.log('Run testEditButton() to test the edit button');
console.log('==============================================');
