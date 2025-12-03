# Weekly Outfits Diagnostic Guide

## Issue
User reports that "Outfits This Week" count is not working properly in the frontend analytics/dashboard.

## How The System Works

### Data Flow:

```
Frontend Dashboard
    ↓
/api/outfits/analytics/worn-this-week (Next.js API route)
    ↓
Backend: /outfits/analytics/worn-this-week (FastAPI endpoint)
    ↓
Firestore: outfit_history collection
    ↓
Count records where:
  - user_id == current user
  - date_worn >= week_start (Sunday 00:00 UTC)
```

### Week Definition:
- **Week starts**: Sunday at 00:00:00 UTC
- **Week ends**: Saturday at 23:59:59 UTC
- Current week calculated from today back to last Sunday

### Data Sources:

**Primary**: `outfit_history` collection
- Each "mark as worn" creates a new document
- Fields: `user_id`, `outfit_id`, `date_worn`, `outfit_name`
- Count = number of wear events this week

**Fallback**: `outfits` collection (if outfit_history is empty)
- Uses `lastWorn` timestamp field
- Only counts unique outfits (not multiple wears)

---

## Common Issues & Solutions

### Issue 1: Shows 0 When You've Worn Outfits ❌

**Possible Causes**:
1. `outfit_history` collection is empty
2. `date_worn` timestamps are incorrect format
3. Week calculation is off (timezone issues)
4. User authentication mismatch

**Debug Steps**:
```bash
# Check if outfit_history exists for your user
1. Go to Firebase Console → outfit_history collection
2. Look for documents with your user_id
3. Check if date_worn timestamps are present and recent
4. Verify date_worn format (should be milliseconds timestamp)
```

**Fix**:
If outfit_history is empty, outfits aren't being logged when you click "Mark as Worn"

---

### Issue 2: Shows Wrong Number ⚠️

**Possible Causes**:
1. Counting duplicate wear events
2. Week boundaries incorrect
3. Timezone conversion issues
4. Cache serving stale data

**Debug Steps**:
```bash
# Check backend logs
1. Look for: "📊 Counting outfits worn since..."
2. Look for: "✅ Found X outfits worn this week"
3. Look for: "📅 Wear event {id} this week: {date}"
```

**Fix**:
Check if backend logs show correct count but frontend shows different

---

### Issue 3: Not Updating After Wearing Outfit 🔄

**Possible Causes**:
1. Frontend caching old data
2. "Mark as Worn" not saving to outfit_history
3. API cache not being invalidated

**Debug Steps**:
```bash
# Check if mark as worn is working
1. Click "Mark as Worn" on an outfit
2. Check browser network tab for POST to /outfits/{id}/worn
3. Check if response is successful
4. Check Firebase Console for new outfit_history document
5. Refresh dashboard and check if count updates
```

**Fix**:
Frontend has aggressive cache-busting (timestamp + random ID), so if it's still cached, there's a deeper issue

---

## Diagnostic Queries

### 1. Check outfit_history Collection (Firebase Console):

```javascript
// Filter:
user_id == "your-user-id"
date_worn >= [timestamp for last Sunday]

// Count: This should match "Outfits This Week"
```

### 2. Check Backend Endpoint (Browser DevTools):

```bash
# Network tab, find request to:
GET /api/outfits/analytics/worn-this-week?t=...

# Response should be:
{
  "success": true,
  "outfits_worn_this_week": X,  // This number should match your actual wears
  "source": "outfit_history_individual_events",
  "week_start": "2025-10-XX...",
  "calculated_at": "2025-10-20..."
}
```

### 3. Check Frontend Data Flow (Browser Console):

```javascript
// Look for these logs:
"🔍 DEBUG: Worn outfits analytics response: {outfits_worn_this_week: X}"
"🔍 DEBUG: Simple analytics returned: X outfits worn this week"
"🔍 DEBUG: - outfitsThisWeek: X"
```

---

## Specific Debugging Prompts

### What I Need to Help Troubleshoot:

1. **What number is showing?**
   - Showing 0 when it should be higher?
   - Showing a number but it's wrong?
   - Not updating after wearing outfits?

2. **Have you marked any outfits as worn this week?**
   - Where: Outfit detail page → "Mark as Worn" button
   - When: What days this week?
   - How many: How many times total?

3. **What do you see in browser console?**
   - Any errors?
   - What does the API response show?
   - Check: `🔍 DEBUG: Simple analytics returned: X`

4. **Backend logs** (if you have access):
   - Check Railway/Vercel logs
   - Look for: "✅ Found X outfits worn this week"
   - Any errors in calculation?

---

## Quick Test

To test if the system is working:

1. **Generate a new outfit** (or pick an existing one)
2. **Click "Mark as Worn"**
3. **Check if it appears in outfit_history** (Firebase Console)
4. **Refresh dashboard** (Ctrl+F5 to bypass cache)
5. **Check if count increased**

If count doesn't increase → There's an issue with either:
- Mark as worn functionality (not saving)
- Week calculation (wrong week boundaries)
- Query logic (not finding the records)

---

## Next Steps

Please share:
- What number is currently showing?
- What number should it be showing?
- Have you marked any outfits as worn this week?
- Any errors in browser console?

With this info, I can pinpoint the exact issue and fix it!

