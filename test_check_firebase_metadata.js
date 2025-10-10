/**
 * Check actual Firebase metadata by making authenticated API call
 */

const https = require('https');

// This would need your Firebase token - run this in browser console instead
console.log(`
To check Firebase metadata, run this in your browser console while logged into the app:

async function checkMetadata() {
  // Get Firebase token
  const user = firebase.auth().currentUser;
  const token = await user.getIdToken();
  
  // Fetch wardrobe items
  const response = await fetch('https://closetgptrenew-backend-production.up.railway.app/api/wardrobe', {
    headers: {
      'Authorization': \`Bearer \${token}\`
    }
  });
  
  const data = await response.json();
  const items = data.items || [];
  
  console.log(\`Total items: \${items.length}\`);
  
  // Check first 5 items for metadata
  items.slice(0, 5).forEach((item, i) => {
    console.log(\`\\n===== Item \${i+1}: \${item.name} =====\`);
    console.log(\`Occasion tags:\`, item.occasion || '❌ EMPTY');
    console.log(\`Style tags:\`, item.style || '❌ EMPTY');
    console.log(\`Mood tags:\`, item.mood || '❌ EMPTY');
    
    if (item.metadata) {
      console.log(\`Metadata.occasionTags:\`, item.metadata.occasionTags || '❌ MISSING');
      console.log(\`Metadata.styleTags:\`, item.metadata.styleTags || '❌ MISSING');
    } else {
      console.log(\`❌ No metadata object\`);
    }
  });
}

checkMetadata();
`);

