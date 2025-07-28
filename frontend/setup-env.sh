#!/bin/bash

echo "🚀 Setting up Frontend Environment Variables..."

# Create .env.local file
cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=https://acceptable-wisdom-production-ac06.up.railway.app
NEXT_PUBLIC_BACKEND_URL=https://acceptable-wisdom-production-ac06.up.railway.app

# Firebase Configuration (Public)
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDijqJ9NbtS959F3kn5IZt8Uk7J9iuSfPU
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=closetgptrenew.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=closetgptrenew
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=closetgptrenew.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX

# Environment
NODE_ENV=development
EOF

echo "✅ Environment variables created in .env.local"
echo "🔄 Restart your frontend server to apply changes"
echo "📝 Run: npm run dev" 