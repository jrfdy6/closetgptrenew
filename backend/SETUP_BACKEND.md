# 🚀 ClosetGPT Backend Setup Guide

This guide will help you set up the real backend with AI-powered image analysis.

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **Railway CLI** installed: `npm install -g @railway/cli`
3. **OpenAI API Key** (for GPT-4 Vision analysis)
4. **Firebase Service Account** (for authentication)

## 🔧 Local Development Setup

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements-full.txt
```

### Step 2: Set Environment Variables
Create a `.env` file in the backend directory:
```bash
# OpenAI API Key (required for image analysis)
OPENAI_API_KEY=your_openai_api_key_here

# Firebase Configuration
FIREBASE_PROJECT_ID=closetgptrenew
FIREBASE_CLIENT_EMAIL=your_service_account_email
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# Environment
ENVIRONMENT=development
PORT=8080

# CORS Origins
ALLOWED_ORIGINS=http://localhost:3000,https://closetgpt-frontend.vercel.app
```

### Step 3: Test Locally
```bash
# Start the backend
python start_local.py

# In another terminal, test the endpoints
python test_backend_local.py
```

## 🚀 Railway Deployment

### Step 1: Deploy to Railway
```bash
cd backend
./deploy_backend.sh
```

### Step 2: Set Railway Environment Variables
In the Railway dashboard, set these variables:
- `OPENAI_API_KEY`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`
- `ENVIRONMENT=production`
- `PORT=8080`

### Step 3: Get the Backend URL
After deployment, Railway will provide a URL like:
`https://your-backend-name.railway.app`

## 🔗 Update Frontend

Once the backend is deployed, update the frontend to use the real backend:

### Step 1: Update Frontend Environment
In your Vercel dashboard, set:
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend-name.railway.app
```

### Step 2: Update API Routes
Uncomment the real backend calls in:
- `frontend/src/app/api/analyze-image/route.ts`
- `frontend/src/app/api/analyze/route.ts`

### Step 3: Deploy Frontend
```bash
cd frontend
git add -A
git commit -m "Update to use real backend"
git push
```

## 🧪 Testing

### Test the Backend
```bash
# Health check
curl https://your-backend-name.railway.app/health

# Image analysis
curl -X POST https://your-backend-name.railway.app/api/analyze-image \
  -H "Content-Type: application/json" \
  -d '{"image":"https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop&crop=center"}'
```

### Test the Frontend
1. Go to your Vercel deployment
2. Upload an image
3. Check that real AI analysis is working

## 🔍 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements-full.txt
   ```

2. **OpenAI API Key Issues**
   - Verify your API key is correct
   - Check you have credits in your OpenAI account

3. **Firebase Issues**
   - Verify service account credentials
   - Check Firebase project ID

4. **CORS Issues**
   - Update `ALLOWED_ORIGINS` in Railway environment variables

### Debug Commands
```bash
# Check Railway logs
railway logs

# Test backend locally
python test_backend_local.py

# Check environment variables
railway variables
```

## 🎯 Expected Results

With the real backend, you should see:
- ✅ **Accurate color detection** based on the actual image
- ✅ **Style analysis** using CLIP
- ✅ **Detailed clothing type** identification
- ✅ **Season and occasion** recommendations
- ✅ **Brand detection** (if visible)

## 📞 Support

If you encounter issues:
1. Check Railway logs: `railway logs`
2. Test locally first: `python start_local.py`
3. Verify environment variables are set correctly
4. Check OpenAI API key and credits

---

**Next Steps**: Once the backend is deployed and working, the frontend will automatically use real AI analysis instead of mock data! 🎉 