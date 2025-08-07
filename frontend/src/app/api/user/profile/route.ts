import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: User profile API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // For now, return a default profile structure
    // In a real implementation, you would fetch this from your backend
    return NextResponse.json({
      success: true,
      profile: {
        id: 'default-profile',
        userId: 'user-id-from-token',
        name: 'New User',
        email: 'user@example.com',
        onboardingCompleted: false,
        stylePreferences: {
          gender: 'unisex',
          style: 'casual',
          colors: ['blue', 'black', 'white'],
          brands: []
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('🔍 DEBUG: Error fetching user profile:', error);
    return NextResponse.json(
      { error: 'Failed to fetch user profile', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Creating user profile');
    
    const body = await request.json();
    console.log('🔍 DEBUG: Profile data:', body);
    
    // For now, return success
    // In a real implementation, you would save this to your backend
    return NextResponse.json({
      success: true,
      profile: {
        id: 'new-profile-id',
        ...body,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('🔍 DEBUG: Error creating user profile:', error);
    return NextResponse.json(
      { error: 'Failed to create user profile', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 