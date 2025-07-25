#!/usr/bin/env node

/**
 * Authentication Helper for Live Route Testing
 * Provides methods to get authentication tokens for testing
 */

const admin = require('firebase-admin');

// Initialize Firebase Admin (you'll need to set up service account)
function initializeFirebase() {
  try {
    if (!admin.apps.length) {
      admin.initializeApp({
        credential: admin.credential.applicationDefault(),
        // Or use service account key:
        // credential: admin.credential.cert(require('./path/to/serviceAccountKey.json'))
      });
    }
    return true;
  } catch (error) {
    console.error('Failed to initialize Firebase Admin:', error);
    return false;
  }
}

/**
 * Generate a custom token for testing
 * @param {string} userId - The user ID to create a token for
 * @returns {Promise<string>} - The custom token
 */
async function generateTestToken(userId = 'test-user-123') {
  if (!initializeFirebase()) {
    throw new Error('Firebase Admin not initialized');
  }
  
  try {
    const customToken = await admin.auth().createCustomToken(userId, {
      test: true,
      role: 'tester'
    });
    
    console.log(`✅ Generated test token for user: ${userId}`);
    return customToken;
  } catch (error) {
    console.error('Failed to generate test token:', error);
    throw error;
  }
}

/**
 * Create a test user in Firebase Auth
 * @param {string} email - Email for the test user
 * @param {string} password - Password for the test user
 * @returns {Promise<string>} - The user ID
 */
async function createTestUser(email = 'test@closetgpt.com', password = 'testpass123') {
  if (!initializeFirebase()) {
    throw new Error('Firebase Admin not initialized');
  }
  
  try {
    const userRecord = await admin.auth().createUser({
      email,
      password,
      displayName: 'Test User',
      emailVerified: true
    });
    
    console.log(`✅ Created test user: ${userRecord.uid}`);
    return userRecord.uid;
  } catch (error) {
    if (error.code === 'auth/email-already-exists') {
      console.log('⚠️  Test user already exists, getting existing user...');
      const userRecord = await admin.auth().getUserByEmail(email);
      return userRecord.uid;
    }
    console.error('Failed to create test user:', error);
    throw error;
  }
}

/**
 * Get an ID token for a user (requires client-side Firebase Auth)
 * This is a placeholder - you'll need to implement client-side auth
 */
async function getIdToken(userId) {
  // This would require client-side Firebase Auth
  // For testing, you might want to use a pre-generated token
  console.log('⚠️  getIdToken requires client-side Firebase Auth implementation');
  return null;
}

/**
 * Clean up test users
 * @param {string} email - Email of the test user to delete
 */
async function cleanupTestUser(email = 'test@closetgpt.com') {
  if (!initializeFirebase()) {
    throw new Error('Firebase Admin not initialized');
  }
  
  try {
    const userRecord = await admin.auth().getUserByEmail(email);
    await admin.auth().deleteUser(userRecord.uid);
    console.log(`✅ Deleted test user: ${userRecord.uid}`);
  } catch (error) {
    console.error('Failed to cleanup test user:', error);
  }
}

// Export functions
module.exports = {
  generateTestToken,
  createTestUser,
  getIdToken,
  cleanupTestUser,
  initializeFirebase
};

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  const email = process.argv[3] || 'test@closetgpt.com';
  
  switch (command) {
    case 'create-user':
      createTestUser(email).then(uid => {
        console.log(`User ID: ${uid}`);
      }).catch(console.error);
      break;
      
    case 'generate-token':
      const userId = process.argv[3] || 'test-user-123';
      generateTestToken(userId).then(token => {
        console.log(`Token: ${token}`);
      }).catch(console.error);
      break;
      
    case 'cleanup':
      cleanupTestUser(email).catch(console.error);
      break;
      
    default:
      console.log('Usage:');
      console.log('  node auth_helper.js create-user [email]');
      console.log('  node auth_helper.js generate-token [userId]');
      console.log('  node auth_helper.js cleanup [email]');
  }
} 