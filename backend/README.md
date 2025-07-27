# ClosetGPT Backend

This is the backend API for ClosetGPT, providing AI-powered clothing analysis and outfit recommendations.

## Features

- **Image Analysis**: Analyze clothing items using GPT-4 Vision and CLIP
- **Style Detection**: Identify clothing types, colors, and styles
- **Recommendations**: Generate outfit suggestions based on user preferences
- **Weather Integration**: Consider weather conditions for outfit recommendations

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements-full.txt
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export FIREBASE_PROJECT_ID="your-firebase-project-id"
   ```

3. **Run locally**:
   ```bash
   python -m uvicorn src.app:app --host 0.0.0.0 --port 8080 --reload
   ```

4. **Deploy to Railway**:
   ```bash
   railway up
   ```

## API Endpoints

- `GET /health` - Health check
- `POST /api/analyze-image` - Analyze clothing image
- `POST /api/outfits` - Generate outfit recommendations

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for GPT-4 Vision
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `PORT` - Server port (default: 8080)

## Deployment

The backend is configured to deploy to Railway with the correct app entry point. 