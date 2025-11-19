# Testing Guide - Prospecting Workflow

Complete step-by-step guide to test the prospecting workflow.

## 🚀 Quick Start Testing

### Prerequisites

1. **Backend Running**
   ```bash
   # From project root
   cd backend
   python -m uvicorn app:app --reload --port 3001
   ```

2. **Firebase Configured**
   - Environment variables set (or using Firebase credentials file)
   - Firestore database accessible

3. **Test User ID**
   - Use a test user ID for all requests (e.g., `test-user-123`)

---

## 📝 Phase 1: Test Manual Prospect Filtering

### Step 1: Upload Test Prospects

```bash
curl -X POST http://localhost:3001/api/prospects/upload \
  -H "Content-Type: application/json" \
  -d '{
    "prospects": [
      {
        "name": "Sarah Johnson",
        "job_title": "VP of Sales",
        "company": "TechCorp Inc",
        "email": "sarah@techcorp.com",
        "notes": "Met at conference, interested in automation",
        "source": "LinkedIn",
        "linkedin_url": "https://linkedin.com/in/sarahjohnson",
        "website": "https://techcorp.com"
      },
      {
        "name": "Mike Chen",
        "job_title": "Sales Director",
        "company": "StartupXYZ",
        "email": "mike@startupxyz.com",
        "notes": "Growing team, needs solutions",
        "source": "Email list"
      },
      {
        "name": "Emma Williams",
        "job_title": "CMO",
        "company": "EnterpriseCo",
        "email": "emma@enterpriseco.com",
        "notes": "Large enterprise, long sales cycle",
        "source": "LinkedIn"
      }
    ],
    "user_id": "test-user-123",
    "batch_name": "Test Batch 1"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "batch_id": "uuid-here",
  "prospects_stored": 3,
  "prospect_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Save the `prospect_ids` for next steps!**

### Step 2: Generate Analysis Prompt

```bash
curl -X POST http://localhost:3001/api/prospects/manual/prompts/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_ids": ["uuid1", "uuid2", "uuid3"],
    "user_id": "test-user-123",
    "audience_profile": {
      "brand_name": "Your Company",
      "brand_voice": "Professional and friendly",
      "target_pain_points": ["Manual processes are slow", "Need better automation"],
      "value_propositions": ["Saves time", "Improves efficiency", "ROI-focused"],
      "industry_focus": "SaaS",
      "custom_guidelines": "Focus on time savings and ROI"
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "mode": "manual",
  "prompt": {
    "system_message": "You are a B2B sales prospecting expert...",
    "user_prompt": "Analyze these prospects...",
    "full_prompt": "System: ...\n\nUser: ...",
    "expected_format": {...}
  },
  "instructions": "1. Copy the 'full_prompt'...",
  "prospects_count": 3
}
```

**Action:** Copy the `prompt.full_prompt` field and paste it into ChatGPT.

### Step 3: Get ChatGPT Response

After pasting into ChatGPT, you should get a JSON response like:

```json
{
  "prospects": [
    {
      "prospect_id": "uuid1",
      "summary": "VP of Sales at TechCorp Inc, focused on scaling...",
      "fit_likelihood": "High",
      "suggested_outreach_angle": "Focus on automation benefits and time savings",
      "reasoning": "Role aligns with target, company size fits, notes indicate interest",
      "confidence_score": 0.85
    },
    {
      "prospect_id": "uuid2",
      "summary": "Sales Director at StartupXYZ...",
      "fit_likelihood": "Medium",
      "suggested_outreach_angle": "Emphasize growth and efficiency",
      "reasoning": "...",
      "confidence_score": 0.75
    },
    {
      "prospect_id": "uuid3",
      "summary": "CMO at EnterpriseCo...",
      "fit_likelihood": "Low",
      "suggested_outreach_angle": "Long-term relationship building",
      "reasoning": "...",
      "confidence_score": 0.60
    }
  ]
}
```

### Step 4: Upload Analysis Results

```bash
curl -X POST http://localhost:3001/api/prospects/manual/upload-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "results": [
      {
        "prospect_id": "uuid1",
        "analysis": {
          "summary": "VP of Sales at TechCorp Inc, focused on scaling...",
          "fit_likelihood": "High",
          "suggested_outreach_angle": "Focus on automation benefits",
          "reasoning": "Role aligns with target",
          "confidence_score": 0.85
        }
      },
      {
        "prospect_id": "uuid2",
        "analysis": {
          "summary": "Sales Director at StartupXYZ...",
          "fit_likelihood": "Medium",
          "suggested_outreach_angle": "Emphasize growth",
          "reasoning": "...",
          "confidence_score": 0.75
        }
      },
      {
        "prospect_id": "uuid3",
        "analysis": {
          "summary": "CMO at EnterpriseCo...",
          "fit_likelihood": "Low",
          "suggested_outreach_angle": "Long-term relationship",
          "reasoning": "...",
          "confidence_score": 0.60
        }
      }
    ],
    "user_id": "test-user-123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "uploaded_count": 3,
  "total_count": 3,
  "errors": []
}
```

### Step 5: List Prospects to Verify

```bash
curl "http://localhost:3001/api/prospects/list?user_id=test-user-123&status=analyzed"
```

**Verify:** You should see all 3 prospects with their analysis fields populated.

### Step 6: Review & Approve Prospects

```bash
curl -X POST http://localhost:3001/api/prospects/review \
  -H "Content-Type: application/json" \
  -d '{
    "reviews": [
      {
        "prospect_id": "uuid1",
        "approved": true,
        "notes": "Great fit, proceed with outreach"
      },
      {
        "prospect_id": "uuid2",
        "approved": true,
        "notes": "Good fit, worth trying"
      },
      {
        "prospect_id": "uuid3",
        "approved": false,
        "notes": "Low fit, not worth pursuing right now"
      }
    ],
    "user_id": "test-user-123"
  }'
```

### Step 7: Track Phase 1 Metrics

```bash
curl -X POST http://localhost:3001/api/phases/phase1/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "batch_id": "batch-uuid-from-step-1",
    "total_prospects": 3,
    "approved_prospects": 2,
    "rejected_prospects": 1,
    "manual_research_time_saved_minutes": 45.0,
    "phase_start_time": 1234567890.0,
    "phase_end_time": 1234568100.0,
    "notes": "Test run - AI filtering worked well"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "metrics": {
    "total_prospects": 3,
    "approved_prospects": 2,
    "rejected_prospects": 1,
    "approval_rate": 66.67,
    "time_saved_minutes": 45.0
  },
  "interpretation": {
    "high_quality_threshold": ">50% approval rate suggests good filtering",
    "time_savings": "45.0 minutes saved"
  }
}
```

### Step 8: Get Phase 1 Summary

```bash
curl "http://localhost:3001/api/phases/phase1/summary/test-user-123"
```

---

## 📧 Phase 2: Test Manual Outreach Generation

### Step 1: Get Approved Prospects

```bash
curl "http://localhost:3001/api/prospects/list?user_id=test-user-123&status=approved"
```

**Use one of the approved prospect IDs for next step.**

### Step 2: Generate Outreach Prompt

```bash
curl -X POST http://localhost:3001/api/outreach/manual/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_id": "uuid1",
    "user_id": "test-user-123",
    "audience_profile": {
      "brand_name": "Your Company",
      "brand_voice": "Professional and friendly",
      "target_pain_points": ["Manual processes are slow"],
      "value_propositions": ["Saves time", "Improves efficiency"],
      "industry_focus": "SaaS",
      "custom_guidelines": "Focus on ROI and time savings"
    },
    "preferred_tone": "professional",
    "include_social": true
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "mode": "manual",
  "prospect_id": "uuid1",
  "prompt": {
    "system_message": "You are an expert B2B email copywriter...",
    "user_prompt": "Generate 5 email draft options...",
    "full_prompt": "System: ...\n\nUser: ...",
    "expected_format": {...}
  },
  "instructions": "1. Copy the 'full_prompt'...",
  "include_social": true
}
```

**Action:** Copy `prompt.full_prompt` and paste into ChatGPT.

### Step 3: Get ChatGPT Response

After pasting into ChatGPT, you should get:

```json
{
  "emails": [
    {
      "variant": 1,
      "subject": "Quick question about TechCorp's growth",
      "body": "Hi Sarah,\n\nI noticed TechCorp has been scaling rapidly..."
    },
    {
      "variant": 2,
      "subject": "Helping sales teams like yours scale",
      "body": "..."
    }
  ],
  "social_posts": [
    {
      "variant": 1,
      "caption": "Excited to connect with sales leaders focused on growth...",
      "hashtags": ["#sales", "#growth", "#automation"]
    }
  ]
}
```

### Step 4: Upload Outreach Results

```bash
curl -X POST http://localhost:3001/api/outreach/manual/upload \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_id": "uuid1",
    "draft_id": "draft-uuid-123",
    "email_drafts": [
      {
        "variant": 1,
        "subject": "Quick question about TechCorp'\''s growth",
        "body": "Hi Sarah,\n\nI noticed TechCorp has been scaling rapidly..."
      },
      {
        "variant": 2,
        "subject": "Helping sales teams scale",
        "body": "Hi Sarah,\n\n..."
      }
    ],
    "social_drafts": [
      {
        "variant": 1,
        "caption": "Excited to connect with sales leaders...",
        "hashtags": ["#sales", "#growth"]
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "draft_id": "draft-uuid-123",
  "prospect_id": "uuid1",
  "email_drafts_count": 2,
  "social_drafts_count": 1
}
```

### Step 5: List Drafts

```bash
curl "http://localhost:3001/api/outreach/drafts?user_id=test-user-123"
```

### Step 6: Track Outreach Send

```bash
curl -X POST http://localhost:3001/api/tracking/outreach \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id": "draft-uuid-123",
    "prospect_id": "uuid1",
    "user_id": "test-user-123",
    "channel": "email",
    "variant_used": 1,
    "sent_at": 1234567890.0
  }'
```

### Step 7: Track Engagement (Manual)

```bash
curl -X POST http://localhost:3001/api/phases/phase2/engagement \
  -H "Content-Type: application/json" \
  -d '{
    "outreach_id": "draft-uuid-123_1234567890",
    "user_id": "test-user-123",
    "responses": 1,
    "clicks": 2,
    "likes": 0,
    "shares": 0,
    "comments": 0,
    "meetings_booked": 0,
    "positive_responses": 1,
    "negative_responses": 0,
    "no_response": 0
  }'
```

### Step 8: Track Phase 2 Metrics

```bash
curl -X POST http://localhost:3001/api/phases/phase2/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "outreach_count": 1,
    "email_sent": 1,
    "social_posts_sent": 0,
    "manual_drafting_time_saved_minutes": 30.0,
    "phase_start_time": 1234567890.0,
    "phase_end_time": 1234568100.0
  }'
```

---

## 🔧 Phase 3: Test Knowledge Base

### Step 1: Save Prompt Refinement

```bash
curl -X POST http://localhost:3001/api/phases/phase3/prompt-refinement \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "prompt_type": "prospect_analysis",
    "original_prompt_version": "v1.0",
    "adjustments": {
      "added_context": "Focus more on company size",
      "modified_tone": "More consultative"
    },
    "reasoning": "High approval rate but missed some key prospects",
    "test_results": {
      "approval_rate_before": 60.0,
      "approval_rate_after": 75.0
    }
  }'
```

### Step 2: Add Knowledge Entry

```bash
curl -X POST "http://localhost:3001/api/phases/phase3/knowledge?user_id=test-user-123&entry_type=success_pattern" \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "pattern": "Short emails work better",
      "evidence": "65% vs 25% response rate",
      "context": "B2B SaaS industry"
    },
    "context": "Based on 50 outreach attempts"
  }'
```

### Step 3: Get Knowledge Base

```bash
curl "http://localhost:3001/api/phases/phase3/knowledge?user_id=test-user-123"
```

---

## 📊 Phase Status Testing

### Step 1: Get Current Phase

```bash
curl "http://localhost:3001/api/phases/phase-status/test-user-123"
```

### Step 2: Update Phase Status

```bash
curl -X POST http://localhost:3001/api/phases/phase-status \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "current_phase": 1,
    "phase_1_completed": false,
    "phase_2_completed": false,
    "phase_3_completed": false,
    "phase_4_completed": false,
    "automation_enabled": false
  }'
```

---

## 🧪 Quick Test Script

Save this as `test_prospecting.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:3001"
USER_ID="test-user-123"

echo "=== Phase 1: Test Prospect Filtering ==="

# 1. Upload prospects
echo "1. Uploading prospects..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/prospects/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "prospects": [
      {
        "name": "Test Prospect",
        "job_title": "VP Sales",
        "company": "TestCorp",
        "email": "test@testcorp.com"
      }
    ],
    "user_id": "'$USER_ID'",
    "batch_name": "Quick Test"
  }')

echo "Upload Response: $UPLOAD_RESPONSE"

# Extract prospect IDs (you'll need to parse JSON properly in real script)
# PROSPECT_IDS=$(echo $UPLOAD_RESPONSE | jq -r '.prospect_ids[]')

# 2. Generate prompt
echo "2. Generating analysis prompt..."
PROMPT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/prospects/manual/prompts/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_ids": ["prospect-id-here"],
    "user_id": "'$USER_ID'",
    "audience_profile": {
      "brand_name": "Test Company",
      "brand_voice": "Professional"
    }
  }')

echo "Prompt Response: $PROMPT_RESPONSE"

echo "=== Test Complete ==="
echo "Copy the prompt.full_prompt from above and paste into ChatGPT"
```

Make it executable:
```bash
chmod +x test_prospecting.sh
./test_prospecting.sh
```

---

## ✅ Testing Checklist

### Phase 1 Tests
- [ ] Upload prospects works
- [ ] Generate prompt returns formatted prompt
- [ ] Prompt format is correct (can paste into ChatGPT)
- [ ] Upload analysis results works
- [ ] Prospects show analysis in list
- [ ] Review/approve works
- [ ] Phase 1 metrics track correctly
- [ ] Phase 1 summary shows correct data

### Phase 2 Tests
- [ ] Generate outreach prompt works
- [ ] Prompt includes all prospect/audience data
- [ ] Upload outreach drafts works
- [ ] List drafts shows uploaded drafts
- [ ] Track outreach send works
- [ ] Track engagement works
- [ ] Phase 2 metrics track correctly

### Phase 3 Tests
- [ ] Save prompt refinement works
- [ ] Add knowledge entry works
- [ ] Get knowledge base returns entries
- [ ] Knowledge entries are stored correctly

### General Tests
- [ ] All endpoints return proper error messages
- [ ] User ID validation works (can't access other users' data)
- [ ] Phase status tracking works
- [ ] Get next steps shows correct guidance

---

## 🐛 Troubleshooting

### Backend Not Running
```bash
# Check if running
curl http://localhost:3001/health

# Start backend
cd backend
python -m uvicorn app:app --reload --port 3001
```

### Firebase Errors
- Check environment variables are set
- Verify Firestore is accessible
- Check Firebase credentials

### JSON Parsing Errors
- Make sure to escape quotes in JSON
- Use `jq` for parsing: `echo $RESPONSE | jq`
- Validate JSON before sending

### Prospect Not Found
- Make sure prospect IDs match from upload response
- Check user_id is correct
- Verify prospects were actually stored

---

## 📝 Next Steps After Testing

1. **Validate Results**: Check that AI outputs make sense
2. **Tune Prompts**: Adjust audience_profile based on results
3. **Track Metrics**: Monitor approval rates and engagement
4. **Refine**: Use Phase 3 to improve prompts
5. **Scale**: Once validated, move to automation

---

## 🔗 Quick Reference

**Base URL**: `http://localhost:3001`

**Key Endpoints**:
- Upload: `POST /api/prospects/upload`
- Get Prompt: `POST /api/prospects/manual/prompts/analyze`
- Upload Results: `POST /api/prospects/manual/upload-analysis`
- Review: `POST /api/prospects/review`
- Metrics: `POST /api/phases/phase1/metrics`

For full API reference, see `PROSPECTING_WORKFLOW.md` and `MANUAL_WORKFLOW_GUIDE.md`.


