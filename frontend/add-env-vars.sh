#!/bin/bash

echo "🚀 Adding environment variables to frontend project..."

# Function to add env var with correct value
add_env_var() {
    local var_name=$1
    local var_value=$2
    
    echo "Adding $var_name..."
    echo "$var_value" | vercel env add "$var_name" production
}

# Add all environment variables with correct values
add_env_var "NEXT_PUBLIC_API_URL" "https://acceptable-wisdom-production-ac06.up.railway.app"
add_env_var "NEXT_PUBLIC_BACKEND_URL" "https://acceptable-wisdom-production-ac06.up.railway.app"
add_env_var "NEXT_PUBLIC_FIREBASE_API_KEY" "AIzaSyDijqJ9NbtS959F3kn5IZt8Uk7J9iuSfPU"
add_env_var "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" "closetgptrenew.firebaseapp.com"
add_env_var "NEXT_PUBLIC_FIREBASE_PROJECT_ID" "closetgptrenew"
add_env_var "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" "closetgptrenew.appspot.com"
add_env_var "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" "123456789"
add_env_var "NEXT_PUBLIC_FIREBASE_APP_ID" "1:123456789:web:abcdef123456"
add_env_var "NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID" "G-XXXXXXXXXX"

echo "✅ Environment variables added successfully!"
echo "🔄 Deploying to production..."
vercel --prod 