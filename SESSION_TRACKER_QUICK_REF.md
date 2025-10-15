# Session Tracker - Quick Reference Card

## 🎯 What It Does
Prevents the **same items** from appearing in multiple outfits **within the same generation session** (30 minutes).

---

## 🔑 Key Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **Session** | Unique generation instance | User generates 3 gym outfits in a row |
| **Session ID** | Hash of user_id + timestamp | `a1b2c3d4e5f6...` |
| **Session Penalty** | Score reduction for seen items | `-1.5` points |
| **TTL** | Session expiry time | `30 minutes` |

---

## 📊 How Scoring Works

```
Final Score = Base Score + Soft Penalty + Session Penalty
                                          ^^^^^^^^^^^^^^
                                          -1.5 if seen in session
                                           0.0 if new to session
```

### Example:

**First Outfit in Session:**
```
Blue T-Shirt:  2.5 + 0.0 + 0.0  = 2.5 ✅ SELECTED
White Shirt:   2.3 + 0.0 + 0.0  = 2.3
```

**Second Outfit in Same Session:**
```
Blue T-Shirt:  2.5 + 0.0 + (-1.5) = 1.0  🔴 PENALIZED
White Shirt:   2.3 + 0.0 + 0.0    = 2.3 ✅ SELECTED
```

---

## 🔍 What to Look For in Logs

### Success Indicators:
```bash
✅ SESSION TRACKER: Real service loaded
📍 Session ID created: a1b2c3d4... for within-session diversity
🏆 Top 3 scored items (with diversity + session penalties):
  1. White Shirt: 2.30 (div: 1.00, session: +0.00)
  2. Blue T-Shirt: 1.00 (div: 1.00, session: -1.50) 🔴
📍 Marking 5 items as seen in session a1b2c3d4...
✅ Session tracking complete - items marked as seen
```

### Warning Signs:
```bash
⚠️ SessionTrackerService import failed: ...
🔧 SESSION TRACKER: Using mock service
```

---

## ⚙️ Configuration

### Change Session Duration:
```python
# File: backend/src/services/session_tracker_service.py
SESSION_TTL_SECONDS = 30 * 60  # 30 minutes (default)
```

### Change Penalty Strength:
```python
# File: backend/src/services/session_tracker_service.py
# In get_diversity_penalty method:
return -1.5  # Default penalty
```

### Enable Firestore (multi-instance):
```python
# File: backend/src/services/robust_outfit_generation_service.py
session_tracker = SessionTrackerService(use_firestore=True)
```

---

## 🧪 Quick Test

### Test Item Variety:
```bash
# Generate 5 outfits rapidly
for i in {1..5}; do
  curl -X POST http://localhost:8000/outfits/generate \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"occasion": "gym", "style": "athletic", "mood": "energetic"}'
done

# Expected: Different items in each outfit (within 30 min)
```

### Test Session Expiry:
```bash
# Generate outfit
curl -X POST .../outfits/generate -d '...'

# Wait 31 minutes

# Generate again
curl -X POST .../outfits/generate -d '...'

# Expected: Items CAN repeat (new session)
```

---

## 📈 Monitoring

### Check Active Sessions:
```python
from backend.src.services.session_tracker_service import session_tracker
print(session_tracker.get_active_session_count())
```

### View Session Details:
```python
stats = session_tracker.get_session_stats(session_id)
print(f"Items seen: {stats['item_count']}")
print(f"Expires in: {stats['expires_in_seconds']}s")
```

### Manual Cleanup:
```python
session_tracker.clear_session(session_id)  # Clear specific
session_tracker._cleanup_expired_sessions()  # Clear all expired
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Items still repeating | Check session ID is created (see logs) |
| Session penalties not applying | Verify "SESSION TRACKER: Real service loaded" |
| Memory growing | Auto-cleans every 30 min (or manual cleanup) |
| Want stronger penalties | Change `-1.5` to `-2.0` or `-3.0` |

---

## 🎯 Penalty Impact Calculator

| Base Score | Session Penalty | Final Score | Rank Change |
|------------|-----------------|-------------|-------------|
| 3.0 | -1.5 | 1.5 | ⬇️ Drops significantly |
| 2.5 | -1.5 | 1.0 | ⬇️ Below most items |
| 2.0 | -1.5 | 0.5 | ⬇️⬇️ Near bottom |
| 1.5 | -1.5 | 0.0 | ⬇️⬇️⬇️ Last choice |

**Rule of Thumb:** Session penalty drops items ~3-5 positions in ranking

---

## 🚀 Files Modified

1. ✅ **Created:** `backend/src/services/session_tracker_service.py`
2. ✅ **Modified:** `backend/src/services/robust_outfit_generation_service.py`
3. ✅ **Fixed:** `backend/src/routes/outfits/routes.py` (indentation)
4. ✅ **Fixed:** PerformanceMetrics class (missing fields)

---

## 📞 Quick Commands

### View Logs:
```bash
# Railway
railway logs --tail

# Local
tail -f logs/outfit_generation.log | grep -E "SESSION|📍|🔴"
```

### Check Service Status:
```bash
curl http://localhost:8000/outfits/debug
```

### Test Generation:
```bash
curl -X POST http://localhost:8000/outfits/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "occasion": "gym",
    "style": "athletic",
    "mood": "energetic",
    "weather": {"temperature": 75}
  }'
```

---

## ✨ Key Benefits

- 🎯 **Within-session diversity:** No item repetition in same session
- 🔄 **Works with global diversity:** Complements existing system
- 🚀 **Lightweight:** In-memory, auto-cleanup
- 📊 **Transparent:** Clear logging of penalties
- ⚙️ **Configurable:** Easy to adjust TTL and penalties

---

**Ready to Use!** The session tracker is now active in your outfit generation service. 🎉

