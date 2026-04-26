# Easy Outfit Backend

This is the backend API for Easy Outfit, providing AI-powered clothing analysis and outfit recommendations.

## Features

- **Image Analysis**: Analyze clothing items using GPT-4 Vision and CLIP
- **Style Detection**: Identify clothing types, colors, and styles
- **Recommendations**: Generate outfit suggestions based on user preferences
- **Weather Integration**: Consider weather conditions for outfit recommendations

## Quick Start

1. **Create a Python 3.11 virtual environment**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   cp env.example .env
   # Fill in Firebase and API credentials
   ```

4. **Run locally**:
   ```bash
   python run.py
   ```
   The backend listens on port `8080`.

5. **Deploy to Railway**:
   ```bash
   railway up --project 97ed14e7-f7a6-4f86-b919-94f133ed478e --environment production --service closetgptrenew-backend
   ```

6. **Deploy the background worker**:
   ```bash
   cd worker
   railway up --project 97ed14e7-f7a6-4f86-b919-94f133ed478e --environment production --service background-processor
   ```

## API Endpoints

- `GET /health` - Health check
- `POST /api/analyze-image` - Analyze clothing image
- `POST /api/outfits` - Generate outfit recommendations

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for GPT-4 Vision
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `FIREBASE_STORAGE_BUCKET` - Firebase Storage bucket name
- `PORT` - Server port (default: 8080)

## Deployment

The backend is configured to deploy to Railway with the correct app entry point. # Clean deployment
# Railway deployment trigger - Tue Aug 12 06:47:16 EDT 2025
# Force deployment Mon Sep  8 06:28:18 EDT 2025
# Trigger Railway deployment
# Trigger Railway deployment
# Simple debug endpoint added
