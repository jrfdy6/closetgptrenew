import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('Authorization');
  
  if (!authHeader) {
    return NextResponse.json({ error: 'No Authorization header' }, { status: 401 });
  }
  
  if (!authHeader.startsWith('Bearer ')) {
    return NextResponse.json({ error: 'Invalid Authorization header format' }, { status: 401 });
  }
  
  const token = authHeader.split(' ')[1];
  
  return NextResponse.json({ 
    message: 'Authentication header received',
    hasToken: !!token,
    tokenLength: token?.length || 0
  });
} 