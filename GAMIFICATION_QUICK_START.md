# Gamification Quick Start Guide

## 🚀 5-Minute Setup

### 1. Deploy Firestore Indexes (Required First!)

```bash
cd backend
firebase deploy --only firestore:indexes
```

⏰ **Wait 10-15 minutes for indexes to build.**

Check status: Firebase Console → Firestore → Indexes tab

---

### 2. Initialize Existing Users (One-Time)

Create `backend/scripts/init_gamification.py`:

```python
from src.config.firebase import db

def init_users():
    """Add gamification fields to existing users"""
    users = db.collection('users').stream()
    count = 0
    
    for user_doc in users:
        user_data = user_doc.to_dict()
        
        updates = {}
        if 'xp' not in user_data:
            updates['xp'] = 0
        if 'level' not in user_data:
            updates['level'] = 1
        if 'ai_fit_score' not in user_data:
            updates['ai_fit_score'] = 0.0
        if 'badges' not in user_data:
            updates['badges'] = []
        if 'spending_ranges' not in user_data:
            updates['spending_ranges'] = {
                "annual_total": "unknown",
                "shoes": "unknown",
                "jackets": "unknown",
                "pants": "unknown",
                "tops": "unknown",
                "dresses": "unknown",
                "accessories": "unknown"
            }
        
        if updates:
            user_doc.reference.update(updates)
            count += 1
    
    print(f"✅ Initialized {count} users")

if __name__ == "__main__":
    init_users()
```

Run it:
```bash
python scripts/init_gamification.py
```

---

### 3. Deploy Backend

```bash
git add .
git commit -m "feat: Add gamification system"
git push origin main
```

Railway auto-deploys. Check logs:
```bash
railway logs --tail
```

Look for:
- ✅ "Successfully mounted router src.routes.gamification"
- ✅ "Successfully mounted router src.routes.challenges"
- ✅ "Successfully mounted router src.routes.shuffle"

---

### 4. Deploy Frontend

Frontend auto-deploys with same `git push` (Vercel).

Check deployment: https://easyoutfitapp.vercel.app

---

### 5. Test the System

#### Test 1: New User Flow
1. Sign up as new user
2. Complete onboarding
3. **Verify:** Spending questions appear
4. Upload 10 items
5. **Verify:** "Starter Closet" badge unlocked

#### Test 2: XP on Feedback
1. Generate outfit
2. Rate it (thumbs up)
3. **Verify:** "+5 XP" notification appears
4. Go to dashboard
5. **Verify:** XP shown in gamification card

#### Test 3: Challenge Flow
1. Go to `/challenges`
2. Click "Start Challenge" on Hidden Gem Hunter
3. Log outfit with one of the challenge items
4. **Verify:** Progress shows "1/2"
5. Log outfit with second item
6. **Verify:** "+75 XP! Badge unlocked!"

#### Test 4: CPW Display
1. Go to dashboard
2. Scroll to "Your Progress" section
3. **Verify:** CPW card shows average
4. Log a few outfits
5. **Verify:** CPW decreases, trend shows green

#### Test 5: Shuffle
1. Click "Dress Me" button on dashboard
2. **Verify:** Outfit generates
3. **Verify:** "+2 XP" notification

---

## 🐛 Troubleshooting

### "Index required" error
**Problem:** Firestore indexes not ready  
**Fix:** Wait longer or check Firebase Console → Indexes

### "+5 XP" not showing
**Problem:** Gamification service import failed  
**Fix:** Check Railway logs for import errors, restart backend

### CPW shows "null"
**Problem:** User missing spending_ranges  
**Fix:** Have user update in settings or re-onboard

### Challenges not loading
**Problem:** user_challenges collection doesn't exist  
**Fix:** Start a challenge to create the subcollection

---

## ✅ Success Criteria

System is working if:
- ✅ Spending questions appear in onboarding
- ✅ XP notifications show on feedback
- ✅ Dashboard shows 3 gamification cards
- ✅ `/challenges` page loads with challenges
- ✅ Shuffle button generates outfits
- ✅ No errors in Railway or Vercel logs

---

## 📞 Need Help?

Check these files:
- `GAMIFICATION_README.md` - Full feature documentation
- `GAMIFICATION_COMPLETE_SUMMARY.md` - Implementation details
- `GAMIFICATION_DEPLOYMENT_GUIDE.md` - Detailed deployment steps

All services have comprehensive logging. Check:
- Railway logs for backend
- Browser console for frontend
- Firestore console for data

---

**You're ready to go! Push to main and watch the gamification magic happen!** ✨

