# 🚀 Quick Test Reference Card

## Test Wardrobe Upload in 3 Steps

### 1️⃣ Upload (2 min)
```
1. Go to: http://localhost:3000/wardrobe
2. Or production: https://easyoutfitapp.com/wardrobe
3. Click "Upload" button
4. Drop image → Click "Upload All with AI"
5. Wait for ✅ success notification
```

### 2️⃣ Check Display (1 min)
```
1. Click the uploaded item
2. Verify metadata shows:
   ✓ Name, type, color
   ✓ Style, season, occasion tags
   ✓ Visual attributes (material, fit, etc.)
```

### 3️⃣ Verify Storage (1 min)
```javascript
// Open browser console (F12), paste this:
(async function() {
  const user = firebase.auth().currentUser;
  const token = await user.getIdToken();
  const res = await fetch('/api/wardrobe', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await res.json();
  const latest = data.items.sort((a,b) => 
    new Date(b.createdAt) - new Date(a.createdAt)
  )[0];
  
  console.log('✅ Latest Item:', latest.name);
  console.log('📊 Metadata Check:');
  console.log('   Basic:', !!latest.name && !!latest.type && !!latest.color ? '✅' : '❌');
  console.log('   AI Analysis:', !!latest.analysis ? '✅' : '❌');
  console.log('   Style Tags:', latest.style?.length > 0 ? '✅' : '❌');
  console.log('   Seasons:', latest.season?.length > 0 ? '✅' : '❌');
  console.log('   Occasions:', latest.occasion?.length > 0 ? '✅' : '❌');
  console.log('   Image Hash:', !!latest.imageHash ? '✅' : '❌');
  console.log('   Metadata:', !!latest.metadata ? '✅' : '❌');
  
  console.log('\n📄 Full item:', latest);
})();
```

---

## ✅ Expected Fields Checklist

### Required (Must Have)
- [ ] `id` - Unique ID
- [ ] `userId` - User ID
- [ ] `name` - Item name
- [ ] `type` - Clothing type
- [ ] `color` - Primary color
- [ ] `imageUrl` - Storage URL
- [ ] `createdAt` - Timestamp

### AI Analysis (Should Have)
- [ ] `analysis` - AI data object
- [ ] `style` - Style tags array
- [ ] `season` - Season tags array
- [ ] `occasion` - Occasion tags array
- [ ] `dominantColors` - Color array
- [ ] `visualAttributes` - Material, fit, etc.

### Duplicate Detection (Should Have)
- [ ] `imageHash` - Image hash
- [ ] `metadata` - Dimensions, aspect ratio
- [ ] `fileSize` - File size

### Usage Tracking (Must Have)
- [ ] `favorite` - Boolean
- [ ] `wearCount` - Number
- [ ] `lastWorn` - Timestamp/null

---

## 🔧 Verification Tools

### Browser Console (Quick)
```
See: BROWSER_CONSOLE_TEST.md
- Script 1: Check latest item
- Script 2: Verify all fields
- Script 3: Before/after comparison
```

### Node.js Script (Detailed)
```bash
node test_wardrobe_upload.js verify      # Check recent items
node test_wardrobe_upload.js latest      # Show latest in detail
```

### Firebase Console (Manual)
```
1. console.firebase.google.com
2. Firestore Database → wardrobe
3. Sort by createdAt → Check latest
```

---

## 🐛 Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| Upload fails | Check console, verify image format |
| No metadata | Check `/analyze-image` in Network tab |
| Not in Firestore | Check auth token, backend logs |
| Duplicates allowed | Verify `imageHash` field exists |

---

## 📚 Full Documentation

- **Quick Summary**: `TEST_WARDROBE_UPLOAD_SUMMARY.md` ⭐ Start here
- **Comprehensive Guide**: `WARDROBE_UPLOAD_TESTING_GUIDE.md`
- **Browser Scripts**: `BROWSER_CONSOLE_TEST.md`
- **Node.js Tool**: `test_wardrobe_upload.js`

---

## ⚡ One-Liner Success Test

```javascript
// Paste in console after upload
(async()=>{const u=firebase.auth().currentUser,t=await u.getIdToken(),r=await fetch('/api/wardrobe',{headers:{Authorization:`Bearer ${t}`}}),d=await r.json(),i=d.items.sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt))[0];console.log('✅ Upload Success:',i.name,'\n📊 Metadata:',!!i.analysis?'✅':'❌','AI',!!i.style?'✅':'❌','Styles',!!i.imageHash?'✅':'❌','Hash');})();
```

---

**Ready? Start testing!** 🎯
