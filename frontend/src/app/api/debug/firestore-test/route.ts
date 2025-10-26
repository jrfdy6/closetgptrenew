import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    // Get the auth token from header
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    // Import Firebase dynamically to avoid initialization issues
    const { db } = await import('@/lib/firebase/config');
    const { collection, query, where, getDocs, getDocsFromServer } = await import('firebase/firestore');
    const { auth } = await import('@/lib/firebase/config');
    
    // Get current user from token
    const currentUser = auth.currentUser;
    
    if (!currentUser) {
      return NextResponse.json(
        { 
          success: false,
          error: 'User not authenticated in Firebase',
          details: 'auth.currentUser is null'
        },
        { status: 401 }
      );
    }

    const userId = currentUser.uid;
    
    // Test query to outfit_history collection
    const historyRef = collection(db, 'outfit_history');
    const historyQuery = query(
      historyRef,
      where('user_id', '==', userId)
    );
    
    console.log('🧪 Testing Firestore query for user:', userId);
    
    // Try both cached and fresh queries
    const cachedSnapshot = await getDocs(historyQuery);
    const freshSnapshot = await getDocsFromServer(historyQuery);
    
    const cachedCount = cachedSnapshot.size;
    const freshCount = freshSnapshot.size;
    
    // Get sample entries
    const sampleEntries: any[] = [];
    freshSnapshot.forEach((doc) => {
      const data = doc.data();
      sampleEntries.push({
        id: doc.id,
        outfit_name: data.outfit_name,
        date_worn: data.date_worn,
        created_at: data.created_at
      });
    });

    return NextResponse.json({
      success: true,
      test_results: {
        user_id: userId,
        user_email: currentUser.email,
        cached_count: cachedCount,
        fresh_count: freshCount,
        sample_entries: sampleEntries.slice(0, 5), // Show first 5
        timestamp: new Date().toISOString()
      }
    });

  } catch (error: any) {
    console.error('Error testing Firestore:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Firestore test failed',
        details: error.message,
        stack: error.stack
      },
      { status: 500 }
    );
  }
}

