import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';

// For now, let's use a simple approach that returns a placeholder URL
// This will be replaced with proper Firebase Storage once we resolve the Admin SDK issues

export async function POST(request: Request) {
  try {
    console.log('🚀 Starting image upload...');
    
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const userId = formData.get('userId') as string;
    const category = (formData.get('category') as string) || 'clothing';
    const name = (formData.get('name') as string) || 'upload';

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    if (!userId) {
      return NextResponse.json({ error: 'No user ID provided' }, { status: 400 });
    }

    console.log('📁 File details:', {
      name: file.name,
      size: file.size,
      type: file.type
    });

    // For now, return a placeholder URL
    // TODO: Implement proper Firebase Storage upload
    const placeholderUrl = `https://picsum.photos/400/400?random=${Date.now()}`;
    
    console.log('🔗 Placeholder URL generated:', placeholderUrl);

    return NextResponse.json({
      success: true,
      image_url: placeholderUrl,
      path: `wardrobe/${userId}/${uuidv4()}`,
      item_id: uuidv4(),
      name,
      category,
    });

  } catch (error) {
    console.error('❌ Image upload error:', error);
    return NextResponse.json(
      { error: 'Upload failed', details: String(error) },
      { status: 500 }
    );
  }
}
