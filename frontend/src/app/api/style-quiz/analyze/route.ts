import { NextRequest, NextResponse } from 'next/server';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import { initializeApp, getApps, cert } from 'firebase-admin/app';

// Lazy initialization function
function initializeFirebaseAdmin() {
  if (getApps().length === 0) {
    try {
      const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');
      if (!privateKey) {
        throw new Error('FIREBASE_PRIVATE_KEY is not set');
      }

      initializeApp({
        credential: cert({
          projectId: process.env.FIREBASE_PROJECT_ID,
          clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
          privateKey: privateKey,
        }),
      });
      console.log('Firebase Admin initialized successfully');
    } catch (error) {
      console.error('Error initializing Firebase Admin:', error);
      throw error;
    }
  }
}

// Function to calculate quiz results (matching backend logic)
function calculateQuizResults(answers: any[]) {
  const aestheticScores: Record<string, number> = {};
  const colorScores: Record<string, number> = {};
  const bodyTypeScores: Record<string, number> = {};
  const styleScores: Record<string, number> = {};

  // Quiz questions mapping (matching the frontend questions)
  const quizQuestions = [
    {
      id: "movie_vibe",
      category: "aesthetic",
      options: [
        { text: "Classic Hollywood Glamour", scores: { "classic": 0.8, "sophisticated": 0.6, "romantic": 0.4 } },
        { text: "Indie Romance", scores: { "romantic": 0.8, "bohemian": 0.6, "vintage": 0.4 } },
        { text: "Minimalist Scandinavian", scores: { "minimalist": 0.9, "sophisticated": 0.5, "comfortable": 0.3 } },
        { text: "Urban Street Style", scores: { "streetwear": 0.8, "edgy": 0.6, "athletic": 0.4 } }
      ]
    },
    {
      id: "color_preference",
      category: "color",
      options: [
        { text: "Warm & Fresh", scores: { "warm_spring": 0.9, "warm_autumn": 0.7 } },
        { text: "Soft & Cool", scores: { "cool_summer": 0.9, "cool_spring": 0.7 } },
        { text: "Rich & Deep", scores: { "cool_winter": 0.9, "warm_winter": 0.7 } },
        { text: "Earthy & Warm", scores: { "warm_autumn": 0.9, "cool_autumn": 0.7 } }
      ]
    },
    {
      id: "silhouette_preference",
      category: "fit",
      options: [
        { text: "Fitted & Structured", scores: { "hourglass": 0.8, "rectangle": 0.6 } },
        { text: "Flowy & Relaxed", scores: { "pear": 0.8, "apple": 0.6 } },
        { text: "Balanced & Proportional", scores: { "rectangle": 0.8, "hourglass": 0.6 } },
        { text: "Dramatic & Statement", scores: { "inverted_triangle": 0.8, "triangle": 0.6 } }
      ]
    },
    {
      id: "daily_activities",
      category: "lifestyle",
      options: [
        { text: "Office work and meetings", scores: { "professional": 0.8, "classic": 0.6, "sophisticated": 0.4 } },
        { text: "Creative work and casual meetings", scores: { "bohemian": 0.7, "minimalist": 0.5, "comfortable": 0.3 } },
        { text: "Active lifestyle and sports", scores: { "athletic": 0.8, "streetwear": 0.6, "comfortable": 0.4 } },
        { text: "Mix of everything", scores: { "versatile": 0.8, "comfortable": 0.6, "sophisticated": 0.4 } }
      ]
    },
    {
      id: "style_elements",
      category: "style",
      options: [
        { text: "Clean lines and minimal details", scores: { "minimalist": 0.9, "sophisticated": 0.6 } },
        { text: "Rich textures and patterns", scores: { "bohemian": 0.8, "romantic": 0.6 } },
        { text: "Classic and timeless pieces", scores: { "classic": 0.9, "preppy": 0.6 } },
        { text: "Bold and statement pieces", scores: { "edgy": 0.8, "streetwear": 0.6 } }
      ]
    }
  ];

  for (const answer of answers) {
    try {
      const question = quizQuestions.find(q => q.id === answer.question_id);
      if (!question) continue;

      const selectedOption = question.options.find(o => 
        o.text.toLowerCase() === answer.selected_option.toLowerCase()
      );
      if (!selectedOption) continue;

      // Update scores based on question category
      if (question.category === "aesthetic") {
        for (const [style, score] of Object.entries(selectedOption.scores)) {
          aestheticScores[style] = (aestheticScores[style] || 0) + score;
        }
      } else if (question.category === "color") {
        for (const [season, score] of Object.entries(selectedOption.scores)) {
          colorScores[season] = (colorScores[season] || 0) + score;
        }
      } else if (question.category === "fit") {
        for (const [bodyType, score] of Object.entries(selectedOption.scores)) {
          bodyTypeScores[bodyType] = (bodyTypeScores[bodyType] || 0) + score;
        }
      } else if (question.category === "style") {
        for (const [style, score] of Object.entries(selectedOption.scores)) {
          styleScores[style] = (styleScores[style] || 0) + score;
        }
      }
    } catch (error) {
      console.error('Error processing answer:', answer, error);
      continue;
    }
  }

  // Normalize scores
  function normalizeScores(scores: Record<string, number>): Record<string, number> {
    const total = Object.values(scores).reduce((sum, score) => sum + score, 0);
    if (total === 0) return scores;
    return Object.fromEntries(
      Object.entries(scores).map(([key, value]) => [key, value / total])
    );
  }

  // Determine color season
  const colorSeason = Object.keys(colorScores).length > 0 
    ? Object.entries(colorScores).reduce((a, b) => a[1] > b[1] ? a : b)[0]
    : null;

  // Determine body type
  const bodyType = Object.keys(bodyTypeScores).length > 0
    ? Object.entries(bodyTypeScores).reduce((a, b) => a[1] > b[1] ? a : b)[0]
    : null;

  return {
    aesthetic_scores: normalizeScores(aestheticScores),
    color_season: colorSeason,
    body_type: bodyType,
    style_preferences: normalizeScores(styleScores)
  };
}

// Function to generate hybrid style name
function generateHybridStyleName(aestheticScores: Record<string, number>): string {
  const sortedAesthetics = Object.entries(aestheticScores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 2);

  if (sortedAesthetics.length >= 2) {
    const [primary, secondary] = sortedAesthetics;
    const primaryName = primary[0].charAt(0).toUpperCase() + primary[0].slice(1);
    const secondaryName = secondary[0].charAt(0).toUpperCase() + secondary[0].slice(1);
    return `${primaryName} ${secondaryName}`;
  } else if (sortedAesthetics.length === 1) {
    const styleName = sortedAesthetics[0][0].charAt(0).toUpperCase() + sortedAesthetics[0][0].slice(1);
    return styleName;
  }
  return 'Personal Style';
}

export async function POST(req: NextRequest) {
  // Initialize Firebase Admin only when needed
  initializeFirebaseAdmin();
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    // Get the ID token from the header
    const idToken = authHeader.split('Bearer ')[1];
    
    // Verify the token using Firebase Admin
    let decodedToken;
    try {
      const adminAuth = getAuth();
      if (!adminAuth) {
        throw new Error('Firebase Admin Auth not initialized');
      }
      decodedToken = await adminAuth.verifyIdToken(idToken);
    } catch (error) {
      console.error('Error verifying token:', error);
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'Invalid token'
        },
        { status: 401 }
      );
    }

    const submission = await req.json();
    const userId = submission.user_id;

    // Verify that the user ID in the submission matches the authenticated user
    if (userId !== decodedToken.uid) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'User ID mismatch'
        },
        { status: 401 }
      );
    }

    // Get Firestore instance
    const db = getFirestore();
    if (!db) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Database Error',
          details: 'Firestore is not initialized'
        },
        { status: 500 }
      );
    }

    // Calculate quiz results
    const quizResults = calculateQuizResults(submission.answers);
    
    // Generate hybrid style name
    const hybridStyleName = generateHybridStyleName(quizResults.aesthetic_scores);

    // Convert style preferences from scores object to array of top styles
    const topStyles = Object.entries(quizResults.style_preferences)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([style]) => style);

    console.log('Style Quiz Debug - User ID:', userId);
    console.log('Style Quiz Debug - Quiz Results:', quizResults);
    console.log('Style Quiz Debug - Hybrid Style Name:', hybridStyleName);
    console.log('Style Quiz Debug - Top Styles:', topStyles);

    // Save the comprehensive style profile to Firestore
    const userRef = db.collection('users').doc(userId);
    const saveData = {
      hybridStyleName: hybridStyleName,
      styleQuizResults: quizResults,
      aestheticScores: quizResults.aesthetic_scores,
      colorSeason: quizResults.color_season,
      bodyType: quizResults.body_type,
      stylePreferences: topStyles, // Save as array of strings instead of scores object
      quizAnswers: submission.answers,
      quizCompletedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    console.log('Style Quiz Debug - Saving to Firestore:', saveData);
    await userRef.set(saveData, { merge: true });
    console.log('Style Quiz Debug - Successfully saved to Firestore');

    // Also save to style discovery profiles collection for backend compatibility
    const profileRef = db.collection('style_discovery_profiles').doc(userId);
    await profileRef.set({
      user_id: userId,
      answers: submission.answers,
      quiz_results: quizResults,
      hybrid_style_name: hybridStyleName,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }, { merge: true });

    return NextResponse.json({ 
      success: true,
      message: 'Style profile analyzed and saved successfully',
      data: {
        hybridStyleName,
        quizResults
      }
    });
  } catch (error) {
    console.error('Error analyzing style profile:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to analyze style profile',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 