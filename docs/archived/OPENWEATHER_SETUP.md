# 🌤️ OpenWeather API Setup Guide

## Step 1: Get OpenWeather API Key (FREE)

1. **Go to OpenWeatherMap**: https://openweathermap.org/api
2. **Click "Get API Key"** or **"Sign Up"**
3. **Create Account** (free tier includes 1,000 calls/day)
4. **Verify Email** and log in
5. **Go to API Keys**: https://home.openweathermap.org/api_keys
6. **Copy your API Key** (looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

## Step 2: Configure Backend Environment Variable

Since you're using Railway for deployment, you need to set the environment variable there:

### Option A: Railway Dashboard (Recommended)
1. Go to your Railway project dashboard
2. Select your backend service
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Set:
   - **Name**: `OPENWEATHER_API_KEY`
   - **Value**: Your API key from Step 1
6. Click **Add**
7. Your service will automatically redeploy

### Option B: Railway CLI
```bash
# Install Railway CLI if not installed
npm install -g @railway/cli

# Login to Railway
railway login

# Set the environment variable
railway variables set OPENWEATHER_API_KEY=your_api_key_here
```

## Step 3: Test the Configuration

After setting the environment variable, wait ~2-3 minutes for deployment, then test:

```bash
# Test with city name (should now work)
curl -X POST https://closetgptrenew-backend-production.up.railway.app/api/weather \
  -H "Content-Type: application/json" \
  -d '{"location": "New York, NY"}'

# Should return real weather data like:
# {"temperature": 65.2, "condition": "Clear", "humidity": 58, "wind_speed": 3.2, "location": "New York", "precipitation": 0}
```

## Step 4: Verify Frontend Integration

1. Go to `http://localhost:3000/dashboard`
2. Weather should show real data (not fallback)
3. Try different locations in Location Settings
4. Generate outfits - should use real weather

## Troubleshooting

### If API Key Doesn't Work:
1. **Check API Key**: Make sure it's copied correctly
2. **Wait for Activation**: New API keys take 10-60 minutes to activate
3. **Check Quotas**: Free tier = 1,000 calls/day
4. **Verify Account**: Email must be verified

### If Still Getting Fallback Data:
1. **Check Railway Variables**: Make sure `OPENWEATHER_API_KEY` is set
2. **Check Deployment**: Wait 2-3 minutes after setting variable
3. **Check Logs**: Look at Railway deployment logs for errors

## API Key Security ✅

- ✅ **Stored securely**: Environment variables on Railway
- ✅ **Not in code**: Never committed to git
- ✅ **Backend only**: Frontend never sees the API key
- ✅ **Rate limited**: OpenWeather has built-in limits

## Cost Information 💰

- **Free Tier**: 1,000 calls/day (plenty for testing)
- **Paid Plans**: Start at $40/month for 100,000 calls/day
- **Current Usage**: ~10-50 calls/day (very low)

## Next Steps After Setup

Once configured, your weather integration will be **100% functional** with:
- ✅ Real weather data for all locations
- ✅ Accurate outfit recommendations
- ✅ No more fallback data indicators
- ✅ Production-ready weather system

---

**Need help?** The system works perfectly with fallback data too, but real weather data provides the best user experience!
