# Comprehensive Mood & Style Semantic Expansion Plan

Based on your wardrobe audit, here's the expansion plan for moods and styles:

---

## 📊 Current Style Distribution (from audit)
1. Casual: 102 items
2. Classic: 82 items
3. Business Casual: 71 items
4. Preppy: 56 items
5. Formal: 47 items
6. Minimalist: 40 items
7. Sporty: 36 items
8. Athleisure: 32 items
9. Modern: 32 items
10. Streetwear: 28 items
11. Business: 24 items
12. Professional: 20 items
13. Dark Academia: 20 items
14. Urban: 19 items
15. Old Money: 19 items
16. Trendy: 18 items
17. Y2K: 18 items
18. Smart Casual: 17 items
19. Edgy: 16 items
20. Techwear: 15 items

---

## 🎨 MOOD EXPANSION PLAN

### Current Moods (limited)
- Bold, Confident, Relaxed, Calm, Professional, Polished, Romantic, Soft, Casual, Neutral, Comfortable

### New Moods to Add
**Energetic & Active:**
- energetic, lively, dynamic, playful, fun, spirited

**Sophisticated & Elegant:**
- sophisticated, elegant, refined, chic, luxurious, classy

**Creative & Artistic:**
- creative, artistic, expressive, unique, individual, eclectic

**Edgy & Bold:**
- edgy, rebellious, daring, fierce, powerful, dramatic

**Minimal & Simple:**
- minimal, simple, understated, clean, effortless, basic

**Cozy & Warm:**
- cozy, warm, inviting, comfortable, homey, snug

**Fresh & Modern:**
- fresh, modern, contemporary, sleek, polished, crisp

**Adventurous & Outdoorsy:**
- adventurous, outdoorsy, rugged, practical, functional

---

## 🎯 STYLE EXPANSION LOGIC

### Professional Styles
**Classic** should match:
- business, business_casual, smart_casual, preppy, traditional, minimalist, timeless, formal

**Business** should match:
- business_casual, professional, classic, formal, smart_casual, preppy, polished

**Business Casual** should match:
- business, smart_casual, classic, casual, preppy, professional

**Professional** should match:
- business, business_casual, classic, formal, smart_casual

**Smart Casual** should match:
- business_casual, business, classic, casual, preppy, modern

**Preppy** should match:
- classic, business_casual, traditional, smart_casual, old_money

**Formal** should match:
- business, elegant, classic, sophisticated, professional

---

### Casual Styles
**Casual** should match:
- relaxed, everyday, comfortable, streetwear, athleisure, minimalist, modern

**Relaxed** should match:
- casual, comfortable, everyday, athleisure, cozy

**Comfortable** should match:
- casual, relaxed, athleisure, cozy, everyday

**Minimalist** should match:
- modern, simple, clean, classic, casual, contemporary

---

### Urban & Street Styles
**Streetwear** should match:
- urban, edgy, trendy, casual, y2k, grunge, modern

**Urban** should match:
- streetwear, modern, edgy, contemporary, techwear

**Edgy** should match:
- streetwear, urban, grunge, punk, alternative, bold

**Trendy** should match:
- modern, streetwear, y2k, fashion_forward, contemporary

**Y2K** should match:
- trendy, retro, streetwear, edgy, bold

---

### Athletic & Active Styles
**Sporty** should match:
- athletic, athleisure, active, casual, comfortable, techwear

**Athleisure** should match:
- athletic, sporty, casual, comfortable, modern, techwear

**Athletic** should match:
- sporty, athleisure, active, workout, techwear

**Techwear** should match:
- athletic, urban, modern, functional, sporty, futuristic

---

### Sophisticated & Elegant Styles
**Elegant** should match:
- sophisticated, formal, classic, romantic, refined, chic

**Sophisticated** should match:
- elegant, refined, classic, formal, luxurious, polished

**Old Money** should match:
- classic, preppy, traditional, sophisticated, timeless, elegant

**Dark Academia** should match:
- classic, vintage, academic, traditional, sophisticated, preppy

---

### Modern & Contemporary Styles
**Modern** should match:
- contemporary, minimalist, sleek, trendy, clean, casual

**Contemporary** should match:
- modern, minimalist, clean, trendy, sophisticated

---

### Vintage & Retro Styles
**Vintage** should match:
- retro, classic, timeless, old_money, traditional, dark_academia

**Retro** should match:
- vintage, y2k, classic, nostalgic

---

## 🎯 Implementation Strategy

1. **Expand MOOD_COMPAT** to 30+ moods (currently 11)
2. **Verify STYLE_COMPATIBILITY** covers all 20+ major styles
3. **Add bidirectional matching** (if A matches B, then B matches A)
4. **Maintain separation** between incompatible styles (e.g., formal ≠ athleisure)
5. **Test with real wardrobe data**

---

## 📝 Notes

- Mood expansion increases from 11 → 30+ moods
- Style matrix already has 50+ styles but may need verification
- All expansions maintain logical relationships
- No inappropriate matching (e.g., formal ≠ sporty)

