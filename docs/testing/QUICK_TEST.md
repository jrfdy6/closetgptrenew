# Quick Test Guide

## 🚀 Start Backend

```bash
cd backend
python3 -m uvicorn app:app --reload --port 3001
```

Or if you have a virtual environment:
```bash
cd backend
source venv/bin/activate  # or your venv path
python -m uvicorn app:app --reload --port 3001
```

## 🧪 Run Test Script

In a new terminal:
```bash
./test_endpoints.sh
```

## 📋 Manual Test Steps

### 1. Test Health Check
```bash
curl http://localhost:3001/health
```

### 2. Upload Test Prospect
```bash
curl -X POST http://localhost:3001/api/prospects/upload \
  -H "Content-Type: application/json" \
  -d '{
    "prospects": [{
      "name": "Test User",
      "job_title": "VP Sales",
      "company": "TestCorp",
      "email": "test@testcorp.com"
    }],
    "user_id": "test-user-123",
    "batch_name": "Quick Test"
  }'
```

**Save the `prospect_ids` from the response!**

### 3. Generate Analysis Prompt
```bash
# Replace PROSPECT_ID_HERE with actual ID from step 2
curl -X POST http://localhost:3001/api/prospects/manual/prompts/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_ids": ["PROSPECT_ID_HERE"],
    "user_id": "test-user-123",
    "audience_profile": {
      "brand_name": "My Company",
      "brand_voice": "Professional"
    }
  }'
```

**Copy the `prompt.full_prompt` field and paste into ChatGPT!**

### 4. Upload ChatGPT Results
After getting ChatGPT response, format it and upload:

```bash
curl -X POST http://localhost:3001/api/prospects/manual/upload-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "results": [{
      "prospect_id": "PROSPECT_ID_HERE",
      "analysis": {
        "summary": "VP of Sales at TestCorp...",
        "fit_likelihood": "High",
        "suggested_outreach_angle": "Focus on automation",
        "reasoning": "Role aligns with target",
        "confidence_score": 0.85
      }
    }],
    "user_id": "test-user-123"
  }'
```

### 5. Verify Results
```bash
curl "http://localhost:3001/api/prospects/list?user_id=test-user-123"
```

### 6. Test Phase Status
```bash
curl "http://localhost:3001/api/phases/phase-status/test-user-123"
```

## ✅ Expected Results

- ✅ Health endpoint returns `{"status": "healthy"}` or similar
- ✅ Upload returns `{"success": true, "prospect_ids": [...]}`
- ✅ Prompt generation returns formatted prompt
- ✅ List shows uploaded prospects
- ✅ Phase status shows current phase (defaults to Phase 1)

## 🐛 Troubleshooting

### Backend Won't Start
- Check Python version: `python3 --version` (should be 3.8+)
- Install dependencies: `pip install -r backend/requirements.txt`
- Check port 3001 is available

### Import Errors
- Make sure you're in the backend directory
- Check Python path includes backend directory
- Verify all route files exist

### Firebase Errors
- Check environment variables are set
- Or Firebase credentials file exists
- Errors are logged but won't stop route registration

### Endpoint Not Found (404)
- Check routes are mounted in `app.py`
- Verify route paths match exactly
- Check backend logs for registration messages

## 📝 All Endpoints to Test

**Prospect Management:**
- `POST /api/prospects/upload` ✅
- `POST /api/prospects/manual/prompts/analyze` ✅
- `POST /api/prospects/manual/upload-analysis` ✅
- `POST /api/prospects/review` ✅
- `GET /api/prospects/list` ✅

**Outreach:**
- `POST /api/outreach/manual/prompts/generate` ✅
- `POST /api/outreach/manual/upload` ✅
- `GET /api/outreach/drafts` ✅

**Phases:**
- `GET /api/phases/phase-status/{user_id}` ✅
- `POST /api/phases/phase1/metrics` ✅
- `POST /api/phases/phase2/metrics` ✅
- `GET /api/phases/phase1/summary/{user_id}` ✅

**Tracking:**
- `POST /api/tracking/outreach` ✅
- `POST /api/phases/phase2/engagement` ✅
