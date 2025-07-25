import { NextRequest, NextResponse } from 'next/server';
import { getFirebaseIdToken } from '@/lib/utils/auth';

export async function GET(request: NextRequest) {
  try {
    console.log('🧪 Test Gender API: Starting...');
    
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:3001';
    
    // Get user's gender from their profile
    let userGender = null;
    let authHeaders = {};
    
    try {
      console.log('🧪 Test Gender API: Getting Firebase token...');
      const token = await getFirebaseIdToken();
      console.log('🧪 Test Gender API: Token received:', token ? 'YES' : 'NO');
      
      if (token) {
        authHeaders = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        };
        
        // Get user profile to determine gender
        console.log('🧪 Test Gender API: Fetching user profile...');
        const profileResponse = await fetch(`${backendUrl}/api/user/profile`, {
          method: 'GET',
          headers: authHeaders,
        });
        
        console.log('🧪 Test Gender API: Profile response status:', profileResponse.status);
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          console.log('🧪 Test Gender API: Profile data:', JSON.stringify(profileData, null, 2));
          userGender = profileData.data?.gender;
          console.log('🧪 Test Gender API: Extracted gender:', userGender);
        } else {
          console.log('❌ Test Gender API: Profile fetch failed:', profileResponse.status, profileResponse.statusText);
          const errorText = await profileResponse.text();
          console.log('❌ Test Gender API: Error response:', errorText);
        }
      } else {
        console.log('❌ Test Gender API: No Firebase token available');
      }
    } catch (error) {
      console.log('❌ Test Gender API: Error getting user gender:', error);
    }
    
    return NextResponse.json({
      success: true,
      userGender,
      message: userGender ? `Gender found: ${userGender}` : 'No gender found'
    });
  } catch (error) {
    console.error("❌ Test Gender API: Error:", error);
    return NextResponse.json(
      { 
        error: "Failed to test gender retrieval",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
} 