# ⚡ Semantic Filtering System - Quick Reference Guide

**For**: Developers, maintainers, and stakeholders  
**Last Updated**: October 7, 2025

---

## 🎯 What Does This System Do?

Makes outfit recommendations **more flexible** by understanding that:
- "Classic" style items work with "Business Casual" items
- "Professional" mood matches "Polished" mood
- "Business" occasion works with "Work" occasion

**Result**: Users get **100%+ more outfit options** with semantic mode ON

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| **Test Pass Rate** | 100% (24/24 tests) |
| **Performance** | 500 items in 0.43s |
| **Database Items** | 179 normalized |
| **Styles Covered** | 64 styles |
| **Match Improvement** | 100-400% more matches |

---

## 🔑 Core Concepts (5-Minute Explanation)

### 1. Traditional Mode (Old Way)
```
User searches: "Classic"
System shows: Only items tagged "Classic"
Result: 10 items found
```

### 2. Semantic Mode (New Way)
```
User searches: "Classic"
System shows: Items tagged "Classic", "Business Casual", 
              "Smart Casual", "Preppy", etc.
Result: 40 items found (4x more!)
```

### 3. How It Works
```
Request: "Classic" style
  ↓
Check compatibility matrix
  ↓
Matrix says: "Classic" ≈ "Business Casual"
  ↓
Include Business Casual items ✅
```

---

## 🚀 Quick Start for Developers

### Running Locally

**Backend**:
```bash
cd backend
source venv/bin/activate
python main.py
# Runs on http://localhost:3001
```

**Frontend**:
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Testing

**Quick Test**:
```bash
curl -X POST "http://localhost:3001/api/outfits/debug-filter?semantic=true" \
  -H "Content-Type: application/json" \
  -d '{"style": "classic"}'
```

**Full Test Suite**:
```bash
python3 test_edge_cases_stress.py
```

---

## 📝 Essential Functions Reference

### 1. `style_matches(request, item_styles)`
**What**: Checks if item style matches request  
**Input**: Request style (string), Item styles (array)  
**Output**: True/False  
**Example**:
```python
style_matches("classic", ["Business Casual"])
# Semantic: True ✅
# Traditional: False ❌
```

---

### 2. `normalize_item_metadata(item)`
**What**: Cleans and standardizes item data  
**Input**: Item dict/object  
**Output**: Normalized dict  
**Example**:
```python
normalize_item_metadata({
    "style": "Business Casual",  # Mixed case, space
    "occasion": [" Formal "]     # Extra spaces
})
# Returns:
# {
#   "style": ["business_casual"],
#   "occasion": ["formal"]
# }
```

---

### 3. `_filter_suitable_items_with_debug(context, semantic_filtering)`
**What**: Main filtering function  
**Input**: Request context, semantic flag  
**Output**: Valid items + debug info  
**Example**:
```python
result = await service._filter_suitable_items_with_debug(
    context,
    semantic_filtering=True
)
# Returns:
# {
#   "valid_items": [...],
#   "debug_analysis": [...],
#   "summary": {...}
# }
```

---

## 🎨 Style Compatibility Quick Reference

### Most Common Compatibilities

**Classic** works with:
- Business Casual ✅
- Smart Casual ✅
- Preppy ✅
- Traditional ✅
- Minimalist ✅

**Business Casual** works with:
- Classic ✅
- Smart Casual ✅
- Casual ✅
- Professional ✅

**Athletic** works with:
- Sporty ✅
- Casual ✅
- Streetwear ✅
- Activewear ✅

**Romantic** works with:
- Feminine ✅
- Vintage ✅
- Bohemian ✅
- Soft ✅

---

## 🔧 Configuration

### Feature Flags (Environment Variables)

**`FEATURE_SEMANTIC_MATCH`**
- `true` = Semantic matching ON
- `false` = Traditional matching only
- **Current**: `true` (production)

**`FEATURE_DEBUG_OUTPUT`**
- `true` = Include debug info in responses
- `false` = Minimal responses
- **Current**: `true` (development)

**`FEATURE_FORCE_TRADITIONAL`**
- `true` = Emergency rollback (force traditional)
- `false` = Normal operation
- **Current**: `false`

### Where to Set
- **Local**: `backend/.env`
- **Production**: Railway dashboard → Environment Variables

---

## 🌐 API Endpoints Cheat Sheet

### Generate Outfit
```http
POST /api/outfits?semantic=true
Authorization: Bearer <token>
Content-Type: application/json

{
  "occasion": "business",
  "style": "classic",
  "mood": "professional"
}
```

### Debug Filtering
```http
POST /api/outfits/debug-filter?semantic=true
Authorization: Bearer <token>
Content-Type: application/json

{
  "style": "classic"
}
```

### Health Check
```http
GET /health
# No auth required
```

---

## 🐛 Troubleshooting

### Problem: No items matching
**Check**:
1. Are items normalized? (Check `normalized` field)
2. Is semantic mode ON? (Check `semantic=true`)
3. Do items have style/occasion/mood tags?

**Fix**:
```bash
# Re-run normalization
python3 LOCAL_BACKFILL_SCRIPT.py --environment production
```

---

### Problem: Too many items matching
**Check**:
1. Is traditional mode needed instead?
2. Are filters too broad?

**Fix**:
```bash
# Force traditional mode
export FEATURE_SEMANTIC_MATCH=false
```

---

### Problem: Slow responses
**Check**:
1. Wardrobe size (500+ items?)
2. Network latency
3. Database queries

**Fix**:
- Add database indexes
- Implement caching
- Optimize queries

---

## 📊 Monitoring

### Key Metrics to Watch

**Filter Pass Rate**:
- Good: 30-70%
- Too High (>80%): Filters too loose
- Too Low (<20%): Filters too strict

**Response Time**:
- Good: <500ms
- Acceptable: 500ms-1s
- Slow: >1s

**Zero Match Rate**:
- Good: <10%
- Warning: 10-20%
- Critical: >20%

### Where to Check
- **Production Logs**: Railway dashboard
- **Local Logs**: Terminal output
- **Test Results**: `test_edge_cases_stress.py`

---

## 🔄 Common Tasks

### Add New Style to Matrix
1. Open `backend/src/utils/style_compatibility_matrix.py`
2. Add new entry:
```python
"new_style": ["new_style", "compatible_style_1", "compatible_style_2"]
```
3. Update existing styles that should be compatible:
```python
"classic": ["classic", "business_casual", "new_style"]  # Add here
```
4. Test:
```bash
python3 test_edge_cases_stress.py
```

---

### Deploy Changes
```bash
# Commit and push (auto-deploys)
git add .
git commit -m "feat: your changes"
git push

# Backend auto-deploys via Railway
# Frontend auto-deploys via Vercel
```

---

### Rollback to Traditional Mode
```bash
# In Railway dashboard:
# Set FEATURE_SEMANTIC_MATCH=false

# Or emergency:
# Set FEATURE_FORCE_TRADITIONAL=true
```

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **SYSTEM_ARCHITECTURE_DOCUMENTATION.md** | Complete technical reference |
| **SYSTEM_FLOW_DIAGRAM.md** | Visual diagrams and flows |
| **QUICK_REFERENCE_GUIDE.md** | This document (quick lookup) |
| **ROLLOUT_PLAN.md** | Deployment strategy |
| **EDGE_CASE_STRESS_TEST_REPORT.md** | Test results |

---

## 🆘 Who to Ask

### Questions About...

**Semantic Logic**:
- Check: `semantic_compatibility.py`
- Test with: `test_edge_cases_stress.py`

**Style Matrix**:
- Check: `style_compatibility_matrix.py`
- Current size: 64 styles

**API Endpoints**:
- Check: `backend/src/routes/outfits/main_hybrid.py`
- Test with: `curl` commands above

**Frontend UI**:
- Check: `frontend/src/app/personalization-demo/page.tsx`
- Test at: https://closetgpt-frontend.vercel.app/personalization-demo

---

## ⚡ Common Code Snippets

### Check if Semantic Mode is Active
```python
from backend.src.config.feature_flags import is_semantic_match_enabled

if is_semantic_match_enabled():
    print("Semantic mode ON")
else:
    print("Traditional mode")
```

### Normalize an Item
```python
from backend.src.utils.semantic_normalization import normalize_item_metadata

normalized = normalize_item_metadata({
    "style": "Business Casual",
    "occasion": ["Work"]
})
# Returns lowercase, cleaned data
```

### Check Style Compatibility
```python
from backend.src.utils.semantic_compatibility import style_matches

matches = style_matches("classic", ["Business Casual"])
# True if compatible, False otherwise
```

### Get Compatibility List
```python
from backend.src.utils.style_compatibility_matrix import STYLE_COMPATIBILITY

compatible_styles = STYLE_COMPATIBILITY.get("classic", [])
# Returns: ["classic", "business_casual", "smart_casual", ...]
```

---

## 🎯 Success Criteria

### System is Working Well If:
- ✅ Filter pass rate: 30-70%
- ✅ Response time: <1 second
- ✅ Zero match rate: <10%
- ✅ All tests passing
- ✅ Users getting outfit recommendations

### System Needs Attention If:
- ⚠️ Filter pass rate: <20% or >80%
- ⚠️ Response time: >2 seconds
- ⚠️ Zero match rate: >20%
- ⚠️ Tests failing
- ⚠️ Users complaining about no matches

---

## 🔗 Quick Links

### Production URLs
- **Backend**: https://closetgptrenew-backend-production.up.railway.app
- **Frontend**: https://closetgpt-frontend.vercel.app
- **Demo Page**: https://closetgpt-frontend.vercel.app/personalization-demo

### Dashboards
- **Railway**: https://railway.app (backend monitoring)
- **Vercel**: https://vercel.com (frontend monitoring)
- **Firebase**: https://console.firebase.google.com (database)

### Code Repositories
- **GitHub**: https://github.com/jrfdy6/closetgptrenew

---

## 📞 Emergency Contacts

### Critical Issue?
1. Check system health: `curl https://closetgptrenew-backend-production.up.railway.app/health`
2. View Railway logs in dashboard
3. Set `FEATURE_FORCE_TRADITIONAL=true` to rollback
4. Check GitHub issues

### Need Help?
1. Read full documentation: `SYSTEM_ARCHITECTURE_DOCUMENTATION.md`
2. Check diagrams: `SYSTEM_FLOW_DIAGRAM.md`
3. Review test results: `EDGE_CASE_STRESS_TEST_REPORT.md`

---

**Version**: 1.0  
**Last Updated**: October 7, 2025  
**Status**: ✅ Complete and Current

---

💡 **Pro Tip**: Bookmark this page for quick reference during development!

