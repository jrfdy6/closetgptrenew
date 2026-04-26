#!/bin/bash

echo "🚀 Setting up Vercel Environment Variables..."

: "${NEXT_PUBLIC_API_URL:?Set NEXT_PUBLIC_API_URL before running this script}"
: "${NEXT_PUBLIC_BACKEND_URL:?Set NEXT_PUBLIC_BACKEND_URL before running this script}"
: "${NEXT_PUBLIC_FIREBASE_API_KEY:?Set NEXT_PUBLIC_FIREBASE_API_KEY before running this script}"
: "${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:?Set NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN before running this script}"
: "${NEXT_PUBLIC_FIREBASE_PROJECT_ID:?Set NEXT_PUBLIC_FIREBASE_PROJECT_ID before running this script}"
: "${NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET:?Set NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET before running this script}"
: "${NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID:?Set NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID before running this script}"
: "${NEXT_PUBLIC_FIREBASE_APP_ID:?Set NEXT_PUBLIC_FIREBASE_APP_ID before running this script}"
: "${NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID:?Set NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID before running this script}"

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
echo "$NEXT_PUBLIC_API_URL" | vercel env add NEXT_PUBLIC_API_URL production
echo "$NEXT_PUBLIC_BACKEND_URL" | vercel env add NEXT_PUBLIC_BACKEND_URL production
echo "$NEXT_PUBLIC_FIREBASE_API_KEY" | vercel env add NEXT_PUBLIC_FIREBASE_API_KEY production
echo "$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" | vercel env add NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN production
echo "$NEXT_PUBLIC_FIREBASE_PROJECT_ID" | vercel env add NEXT_PUBLIC_FIREBASE_PROJECT_ID production
echo "$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" | vercel env add NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET production
echo "$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" | vercel env add NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID production
echo "$NEXT_PUBLIC_FIREBASE_APP_ID" | vercel env add NEXT_PUBLIC_FIREBASE_APP_ID production
echo "$NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID" | vercel env add NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID production

echo "✅ Environment variables added successfully!"
echo "🔄 Redeploying to apply changes..."
vercel --prod 
