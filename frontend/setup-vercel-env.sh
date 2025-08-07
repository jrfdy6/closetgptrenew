#!/bin/bash

echo "🚀 Setting up Vercel Environment Variables..."

# Remove existing variables first
echo "🗑️  Removing existing environment variables..."
vercel env rm NEXT_PUBLIC_API_URL --yes
vercel env rm NEXT_PUBLIC_BACKEND_URL --yes
vercel env rm NEXT_PUBLIC_FIREBASE_API_KEY --yes
vercel env rm NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN --yes
vercel env rm NEXT_PUBLIC_FIREBASE_PROJECT_ID --yes
vercel env rm NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET --yes
vercel env rm NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID --yes
vercel env rm NEXT_PUBLIC_FIREBASE_APP_ID --yes
vercel env rm NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID --yes

echo "✅ Environment variables removed"

echo "📝 Adding new environment variables..."

# Add the correct environment variables
echo "https://acceptable-wisdom-production-ac06.up.railway.app" | vercel env add NEXT_PUBLIC_API_URL production
echo "https://acceptable-wisdom-production-ac06.up.railway.app" | vercel env add NEXT_PUBLIC_BACKEND_URL production
echo "AIzaSyDijqJ9NbtS959F3kn5IZt8Uk7J9iuSfPU" | vercel env add NEXT_PUBLIC_FIREBASE_API_KEY production
echo "closetgptrenew.firebaseapp.com" | vercel env add NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN production
echo "closetgptrenew" | vercel env add NEXT_PUBLIC_FIREBASE_PROJECT_ID production
echo "closetgptrenew.appspot.com" | vercel env add NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET production
echo "123456789" | vercel env add NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID production
echo "1:123456789:web:abcdef123456" | vercel env add NEXT_PUBLIC_FIREBASE_APP_ID production
echo "G-XXXXXXXXXX" | vercel env add NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID production

echo "✅ Environment variables added successfully!"
echo "🔄 Redeploying to apply changes..."
vercel --prod 