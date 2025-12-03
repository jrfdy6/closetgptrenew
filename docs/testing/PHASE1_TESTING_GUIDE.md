# Phase 1 Testing Guide 🧪

Complete guide to testing all Phase 1 features locally and in production.

---

## Prerequisites

**Backend:**
- Backend server running on port 3001 [[memory:7132129]]
- Firebase credentials configured
- Python environment activated

**Frontend:**
- Frontend server running (local or Vercel)
- User account with authentication

---

## Quick Start Testing

### Start Servers

**Terminal 1 - Backend:**
```bash
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew
cd backend
source venv/bin/activate  # If using venv
python start_backend.py
# Should see: Server running on port 3001
```

**Terminal 2 - Frontend:**
```bash
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew
cd frontend
npm run dev
# Should see: Ready on http://localhost:3000
```

**Or use Production URL:**
- Production: https://my-app.vercel.app [[memory:7283786]]

---

## Test 1: Progressive Onboarding Flow

### What to Test
New users are guided to upload 5 items immediately after the style quiz.

### Steps

1. **Start Fresh Session**
   ```bash
   # Open incognito window or clear cookies
   # Go to: http://localhost:3000/onboarding
   # Or: https://my-app.vercel.app/onboarding
   ```

2. **Complete Style Quiz**
   - Answer all quiz questions
   - Select your gender, body type, skin tone
   - Choose style preferences
   - Submit quiz

3. **Should See: Guided Upload Wizard** ✅
   - Large heading: "Let's Build Your Digital Wardrobe!"
   - "We need 5 items to start creating amazing outfits"
   - Personalized suggestions based on your style persona
   - Three value prop cards (AI-Powered, Smart Suggestions, Quick & Easy)
   - "Start Adding Items" button

4. **Click "Start Adding Items"**
   - Should see progress indicator: "0 / 5"
   - Batch upload interface appears
   - Encouragement message: "Let's get started!"

5. **Upload Items**
   - Drag and drop 5 clothing images
   - Or click to browse
   - Watch progress: "1 of 5", "2 of 5", etc.
   - Messages update: "Great start! Keep going."

6. **Complete Upload**
   - After 5 items: "🎉 Amazing! Your wardrobe is ready!"
   - Celebration screen appears
   - Message: "Our AI is now ready to generate personalized outfits!"
   - Auto-redirects to style persona page after 2 seconds

### Expected Results

✅ **Success Criteria:**
- Guided upload wizard appears after quiz
- Progress tracked correctly (0/5 → 5/5)
- Personalized suggestions match style persona
- Celebration appears on completion
- Redirects to `/style-persona?from=quiz`

❌ **If Something's Wrong:**
- Check: Quiz completed successfully?
- Check: User authenticated?
- Check: Browser console for errors (F12)
- Check: Backend logs for upload errors

### Test Variations

**Test with Different Personas:**
- "Architect" persona → Should suggest neutral basics
- "Innovator" persona → Should suggest statement pieces
- "Rebel" persona → Should suggest bold items

**Test Edge Cases:**
- Upload only 3 items → Should still show progress, allow continuing
- Skip upload → Currently not supported (good!)
- Upload 10 items → Should complete at 5, but accept all

---

## Test 2: Wardrobe Insights Dashboard

### What to Test
Enhanced dashboard with weekly summary, utilization tracking, and style insights.

### Steps

1. **Navigate to Dashboard**
   ```bash
   # Go to: http://localhost:3000/dashboard
   # Or: https://my-app.vercel.app/dashboard
   # Must be signed in
   ```

2. **Scroll to Wardrobe Insights Card**
   - Should appear after the 4 stat cards (Total items, Favorites, Goals, This week)
   - Has purple border
   - Title: "Wardrobe Insights" with sparkle icon

3. **Check Weekly Summary (4 stat cards)**
   - **Outfits Worn:** Blue gradient card, shirt icon
   - **Items Used:** Purple gradient card, target icon
   - **Created:** Pink gradient card, sparkles icon
   - **Utilization:** Orange gradient card, chart icon

4. **Check Utilization Progress Bar**
   - Shows percentage (0-100%)
   - Color changes based on utilization:
     - Green: 70%+ (Excellent!)
     - Yellow: 40-69% (Good progress!)
     - Red: <40% (Let's unlock more!)
   - Message below bar matches color

5. **Check Style Insights Section**
   - "Your Go-To Styles"
   - Lists top 3 styles with percentages
   - Colored dots (purple, blue, pink)

6. **Check Color Palette Section**
   - "Color Palette"
   - Shows top 5 colors as colored boxes
   - Each with percentage below

7. **Check Underutilized Items Alert** (if applicable)
   - Yellow alert box appears if items haven't been worn
   - Shows count: "You have X items not worn recently"
   - "View Forgotten Items" button

### Test Data Scenarios

**Scenario A: New User (Empty Wardrobe)**
```
Expected:
- All stats show 0
- Utilization: 0%
- Message: "Let's unlock more outfit potential!"
- No style/color insights (empty arrays)
```

**Scenario B: Active User (Used Wardrobe)**
```
Expected:
- Outfits worn: 5+
- Items used: 3+
- Utilization: 40%+
- Style insights populated
- Color palette shows actual colors
```

**Scenario C: Power User (Highly Utilized)**
```
Expected:
- Utilization: 70%+
- Green progress bar
- Message: "Excellent! You're maximizing your wardrobe."
- Trend badge: "+15%" with up arrow
```

### Expected Results

✅ **Success Criteria:**
- Card appears on dashboard
- All 4 stat cards render correctly
- Utilization percentage calculates correctly
- Progress bar color matches percentage
- Style and color insights populate from user data

❌ **Troubleshooting:**
- Card not appearing → Check: User authenticated?
- Stats showing 0 → Check: User has wardrobe items?
- Colors not showing → Check: Items have color metadata?
- Console error → Check: Backend API responding?

---

## Test 3: Enhanced Feedback Loop

### What to Test
Real-time learning from outfit feedback with personalized confirmation messages.

### Steps

1. **Generate an Outfit**
   ```bash
   # Go to: http://localhost:3000/outfits
   # Or: https://my-app.vercel.app/outfits
   # Click "Generate Outfit"
   ```

2. **Submit Positive Feedback**
   - Find the feedback section (thumbs up/down)
   - Click "Like" or "Love"
   - **Should see personalized message:**
     - "✓ Learned: You love Casual outfits! We'll show you more like this."
     - Or: "✓ Got it! We'll prioritize Casual looks for you."
     - Message appears in toast/notification

3. **Submit Negative Feedback**
   - Generate another outfit
   - Click "Dislike" or "Never"
   - Select reason (if prompted)
   - **Should see:**
     - "✓ Understood: We'll avoid [reason] in future suggestions."
     - Or: "✓ Got it: We'll adjust our suggestions based on your feedback."

4. **Check Personalization Status**
   ```bash
   # API test (with your auth token):
   curl -X GET "http://localhost:3001/api/feedback/personalization-status" \
     -H "Authorization: Bearer YOUR_TOKEN"
   
   # Should return:
   {
     "success": true,
     "status": {
       "personalization_level": "beginner",  // or "intermediate" or "advanced"
       "total_interactions": 5,
       "progress_percentage": 50,
       "next_milestone": 10,
       "message": "Rate 5 more outfits to reach Intermediate level!",
       "top_styles": ["Casual", "Business Casual"],
       "top_colors": ["Blue", "Black"]
     }
   }
   ```

5. **Verify Learning in Database**
   ```bash
   # Check Firestore:
   # Collection: user_preferences
   # Document ID: {your_user_id}
   
   # Should contain:
   {
     "user_id": "...",
     "style_preferences": {
       "Casual": 20,      // Increased after "like"
       "Formal": 0
     },
     "color_preferences": {
       "Blue": 15,
       "Black": 10
     },
     "occasion_preferences": {
       "Work": 10
     },
     "avoid_combinations": [
       // Items you disliked
     ],
     "total_interactions": 5,
     "personalization_level": "beginner",
     "last_updated": "..."
   }
   ```

### Test Learning Progression

**Test Beginner → Intermediate:**
1. Start with new user (0 interactions)
2. Rate 10 outfits (mix of likes/dislikes)
3. Check status: Should be "intermediate"
4. Verify preferences updated in Firestore

**Test Intermediate → Advanced:**
1. Continue rating (need 50 total)
2. Check status at 50: Should be "advanced"
3. Message changes to: "Your AI is fully trained!"

### Test Preference Boosting

**Scenario: Like a Casual outfit 3 times**
```
Initial: style_preferences.Casual = 0
After 1st like: Casual = 10
After 2nd like: Casual = 20
After 3rd like: Casual = 30

Future casual outfit suggestions should rank higher
```

**Scenario: Dislike a Formal outfit**
```
style_preferences.Formal = 20 (was positive)
After dislike: Formal = 0 (reduced)
After "never": Formal = -20 (strong penalty)

Future formal outfits should be avoided
```

### Expected Results

✅ **Success Criteria:**
- Feedback submits successfully
- Personalized confirmation message appears
- Preferences update in Firestore immediately
- Total interactions increment
- Personalization level progresses (10 → intermediate, 50 → advanced)
- Future outfit suggestions reflect preferences

❌ **Troubleshooting:**
- No confirmation message → Check: Backend processing service running?
- Preferences not updating → Check: Firestore rules allow writes?
- Status endpoint fails → Check: feedback_processing_service.py imported correctly?
- Console errors → Check: Backend logs for Python errors

---

## Test 4: Error Handling

### What to Test
Smart error recovery with context-aware messages and helpful actions.

### Scenario A: Insufficient Items Error

1. **Setup:**
   - Create test user with only 2 items in wardrobe
   - Or delete items to get below 5

2. **Trigger Error:**
   ```bash
   # Go to: http://localhost:3000/outfits
   # Try to generate an outfit
   ```

3. **Expected Error Recovery Screen:**
   ```
   Title: "Need More Items"
   Icon: Upload icon (orange/red circle)
   
   Message: "You have 2 items, but we need at least 5 to generate this outfit."
   
   Primary Button: "Add More Items" (purple/pink gradient)
   → Clicks to: /wardrobe?action=upload
   
   Secondary Buttons:
   - "Try Simpler Outfit" → Retries with adjusted params
   - "View Saved Outfits" → /outfits?view=saved
   
   Help Tip: "We recommend having at least 10-15 items (2-3 tops, 2-3 bottoms, outerwear, shoes)"
   ```

### Scenario B: Network Error

1. **Trigger:**
   - Stop backend server
   - Try to generate outfit
   - Or: Disconnect internet temporarily

2. **Expected:**
   ```
   Title: "Connection Issue"
   Icon: Refresh icon
   
   Message: "We couldn't reach our servers. Please check your internet connection."
   
   Primary: "Try Again" → Retries request
   Secondary: "Go to Dashboard"
   
   Tip: "If this persists, try refreshing the page or clearing your browser cache."
   ```

### Scenario C: AI Generation Error

1. **Trigger:**
   - Create conflicting preferences (very rare)
   - Or: Backend returns generation error

2. **Expected:**
   ```
   Title: "Outfit Generation Failed"
   Icon: Sparkles icon
   
   Message: "We encountered an issue generating your outfit. This could be due to conflicting preferences."
   
   Primary: "Try Different Style"
   Secondaries: "View Previous Outfits", "Browse Wardrobe"
   
   Tip: "Try adjusting your occasion or style preferences, or add more variety."
   ```

### Test Error Component Directly

**Import and use in any page:**
```typescript
import ErrorRecovery from '@/components/ErrorRecovery';

// In your component:
<ErrorRecovery
  error={new Error("Insufficient items in wardrobe")}
  context={{
    action: "generate_outfit",
    itemCount: 3,
    minRequired: 5
  }}
  onRetry={() => console.log("Retry clicked")}
  onGoBack={() => console.log("Go back clicked")}
/>
```

### Expected Results

✅ **Success Criteria:**
- Error recovery screen appears instead of generic error
- Title and message match error type
- Primary action button is prominent
- Secondary actions provide alternatives
- Help tip is relevant to error type
- Technical details in collapsible section

❌ **Troubleshooting:**
- Generic error shown → Check: ErrorRecovery component imported?
- Wrong error type detected → Check: Error message keywords
- Actions don't work → Check: onClick handlers

---

## Integration Testing

### Full User Journey Test

**Complete flow from onboarding to outfit generation:**

1. **Onboarding** (10 min)
   - Sign up as new user
   - Complete style quiz
   - Upload 5 items via guided wizard
   - Verify redirect to persona page

2. **Dashboard** (2 min)
   - Navigate to dashboard
   - Verify insights card shows data
   - Check all stats populated

3. **Generate Outfit** (3 min)
   - Click "Generate today's fit"
   - Verify outfit generated successfully
   - Submit feedback (like)
   - Verify confirmation message

4. **Check Learning** (2 min)
   - Generate another outfit
   - Should reflect previous feedback
   - Submit different feedback
   - Verify preferences updating

5. **Error Handling** (2 min)
   - Try action that would fail
   - Verify error recovery screen
   - Follow recovery action
   - Verify successful recovery

**Total Time:** ~20 minutes for complete flow

---

## API Testing with cURL

### Test Feedback Processing

**Submit Outfit Feedback:**
```bash
# Get your auth token from browser (F12 → Application → Cookies → token)

curl -X POST "http://localhost:3001/api/feedback/outfit" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_id": "test_outfit_123",
    "feedback_type": "like",
    "rating": 5
  }'

# Expected response:
{
  "success": true,
  "message": "✓ Learned: You love Casual outfits! We'll show you more like this.",
  "feedback_id": "abc123..."
}
```

**Get Personalization Status:**
```bash
curl -X GET "http://localhost:3001/api/feedback/personalization-status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected response:
{
  "success": true,
  "status": {
    "personalization_level": "intermediate",
    "total_interactions": 15,
    "progress_percentage": 30,
    "next_milestone": 50,
    "message": "You're 35 ratings away from Advanced personalization!",
    "top_styles": ["Casual", "Business Casual", "Smart Casual"],
    "top_colors": ["Blue", "Black", "White"]
  }
}
```

---

## Browser Console Testing

### Check Real-Time Updates

**Open Browser Console (F12) and watch for:**

```javascript
// After submitting feedback:
console.log("Feedback processed:", {
  message: "✓ Learned: You love Casual outfits!",
  preferences_updated: true,
  new_level: "intermediate"
});

// After uploading item:
console.log("Upload progress:", {
  uploaded: 3,
  target: 5,
  percentage: 60
});

// On error:
console.error("Error:", {
  type: "insufficient_items",
  recovery_options: ["add_items", "try_simpler", "view_saved"]
});
```

---

## Automated Testing (Optional)

### Cypress E2E Tests

**Create test file:**
```javascript
// cypress/e2e/phase1.cy.ts
describe('Phase 1 Features', () => {
  it('completes guided onboarding', () => {
    cy.visit('/onboarding');
    // Complete quiz
    cy.get('[data-test="quiz-submit"]').click();
    // Should see upload wizard
    cy.contains('Let\'s Build Your Digital Wardrobe!');
    cy.get('[data-test="start-upload"]').click();
    // Upload 5 items
    for (let i = 0; i < 5; i++) {
      cy.get('[data-test="file-input"]').selectFile(`test-image-${i}.jpg`);
    }
    // Should see celebration
    cy.contains('Your wardrobe is ready!');
  });

  it('shows wardrobe insights', () => {
    cy.visit('/dashboard');
    cy.contains('Wardrobe Insights');
    cy.get('[data-test="utilization-percentage"]').should('exist');
  });

  it('processes feedback', () => {
    cy.visit('/outfits');
    cy.get('[data-test="generate-outfit"]').click();
    cy.get('[data-test="like-button"]').click();
    cy.contains('Learned:'); // Confirmation message
  });
});
```

---

## Performance Testing

### Check Loading Times

**Use Chrome DevTools (F12 → Network):**

1. **Onboarding Flow:**
   - Quiz submission: < 2 seconds
   - Upload wizard render: < 500ms
   - Item upload: < 10 seconds per item

2. **Dashboard Load:**
   - Full page load: < 2 seconds
   - Insights card render: < 500ms
   - Data fetch: < 1 second

3. **Feedback Processing:**
   - Feedback submission: < 1 second
   - Confirmation message: Immediate
   - Preference update: < 500ms

---

## Production Testing

### Vercel Deployment

**Test on production URL:** https://my-app.vercel.app [[memory:7283786]]

```bash
# Same tests as local, but using production URL
# No need for local servers

# Check deployment:
# 1. Git push to main
# 2. Wait 2-3 minutes for auto-deploy
# 3. Test production URL
```

### Railway Backend

**Backend URL:** closetgptrenew-production.up.railway.app [[memory:6819383]]

```bash
# Test API:
curl -X GET "https://closetgptrenew-production.up.railway.app/api/feedback/personalization-status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Troubleshooting Common Issues

### Issue: Upload wizard doesn't appear

**Solutions:**
1. Check: Did quiz complete successfully?
2. Check: User authenticated?
3. Check: `uploadPhase` state set to true?
4. Console: Look for React errors

### Issue: Insights card shows all zeros

**Solutions:**
1. Check: User has items in wardrobe?
2. Check: Backend API returning data?
3. Check: Dashboard service connected?
4. Console: Check `dashboardData` object

### Issue: Feedback doesn't update preferences

**Solutions:**
1. Check: Backend running on port 3001?
2. Check: Firestore rules allow writes?
3. Check: `feedback_processing_service.py` imported?
4. Logs: Check backend console for Python errors

### Issue: Error recovery doesn't show

**Solutions:**
1. Check: ErrorRecovery component imported?
2. Check: Error passed correctly?
3. Check: Context object provided?
4. Console: Verify error object structure

---

## Success Checklist

Before marking Phase 1 complete, verify:

- [ ] ✅ Guided onboarding appears after quiz
- [ ] ✅ 5 items can be uploaded successfully
- [ ] ✅ Celebration appears and redirects
- [ ] ✅ Insights card shows on dashboard
- [ ] ✅ All 4 stat cards populated
- [ ] ✅ Utilization percentage calculates
- [ ] ✅ Feedback submits and shows confirmation
- [ ] ✅ Preferences update in Firestore
- [ ] ✅ Personalization level progresses
- [ ] ✅ Error recovery shows for failures
- [ ] ✅ Recovery actions work correctly
- [ ] ✅ No console errors in production

**All checked?** Phase 1 is production-ready! 🎉

---

## Need Help?

**Check these resources:**
- Strategic Plan: `AI_WARDROBE_STRATEGIC_ENGAGEMENT_PLAN.md`
- Implementation Summary: `PHASE1_IMPLEMENTATION_COMPLETE.md`
- Backend logs: Check Railway dashboard
- Frontend logs: Browser console (F12)

**Still stuck?**
- Review component code in `/frontend/src/components/`
- Check service code in `/backend/src/services/`
- Verify Firestore data structure
- Test API endpoints with cURL

