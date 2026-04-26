#!/bin/bash

echo "🚀 Adding environment variables to frontend project..."

: "${NEXT_PUBLIC_API_URL:?Set NEXT_PUBLIC_API_URL before running this script}"
: "${NEXT_PUBLIC_BACKEND_URL:?Set NEXT_PUBLIC_BACKEND_URL before running this script}"
: "${NEXT_PUBLIC_FIREBASE_API_KEY:?Set NEXT_PUBLIC_FIREBASE_API_KEY before running this script}"
: "${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:?Set NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN before running this script}"
: "${NEXT_PUBLIC_FIREBASE_PROJECT_ID:?Set NEXT_PUBLIC_FIREBASE_PROJECT_ID before running this script}"
: "${NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET:?Set NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET before running this script}"
: "${NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID:?Set NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID before running this script}"
: "${NEXT_PUBLIC_FIREBASE_APP_ID:?Set NEXT_PUBLIC_FIREBASE_APP_ID before running this script}"
: "${NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID:?Set NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID before running this script}"

# Function to add env var with correct value
add_env_var() {
    local var_name=$1
    local var_value=$2
    
    echo "Adding $var_name..."
    echo "$var_value" | vercel env add "$var_name" production
}

# Add all environment variables with correct values
add_env_var "NEXT_PUBLIC_API_URL" "$NEXT_PUBLIC_API_URL"
add_env_var "NEXT_PUBLIC_BACKEND_URL" "$NEXT_PUBLIC_BACKEND_URL"
add_env_var "NEXT_PUBLIC_FIREBASE_API_KEY" "$NEXT_PUBLIC_FIREBASE_API_KEY"
add_env_var "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" "$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN"
add_env_var "NEXT_PUBLIC_FIREBASE_PROJECT_ID" "$NEXT_PUBLIC_FIREBASE_PROJECT_ID"
add_env_var "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" "$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET"
add_env_var "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" "$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID"
add_env_var "NEXT_PUBLIC_FIREBASE_APP_ID" "$NEXT_PUBLIC_FIREBASE_APP_ID"
add_env_var "NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID" "$NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID"

echo "✅ Environment variables added successfully!"
echo "🔄 Deploying to production..."
vercel --prod 
