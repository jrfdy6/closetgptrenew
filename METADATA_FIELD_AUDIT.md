# 🔍 Metadata Field Usage Audit

## Available Metadata Fields (from VisualAttributes model)

### Currently Used: ✅
1. `material` - Fabric type (polyester, wool, cotton, etc.)
2. `pattern` - Pattern type (solid, striped, floral, etc.)
3. `fit` - Fit type (loose, slim, tailored, etc.)
4. `neckline` - Neckline type (collar, crew, v-neck, etc.)
5. `waistbandType` - Waistband type (elastic, belt_loops, etc.)

### NOT Used (But Available): ❌
6. `textureStyle` - Texture description (smooth, ribbed, etc.)
7. `fabricWeight` - Weight of fabric (light, medium, heavy)
8. `silhouette` - Overall silhouette (fitted, loose, oversized)
9. `length` - Item length (short, long, midi, maxi, cropped)
10. `sleeveLength` - Sleeve length (short, long, sleeveless, 3/4)
11. `formalLevel` - Formality level (casual, business casual, formal, etc.)
12. `wearLayer` - Layer type (base, mid, outer)
13. `layerLevel` - Numeric layer level
14. `warmthFactor` - Warmth level (light, medium, heavy)
15. `coreCategory` - Core category classification

### Complex Nested Fields:
16. `temperatureCompatibility` - Temperature range compatibility
17. `materialCompatibility` - Compatible materials for pairing
18. `bodyTypeCompatibility` - Body type recommendations
19. `skinToneCompatibility` - Skin tone color matching
20. `outfitScoring` - Pre-computed outfit scores

---

## Missing Metadata Usage by Clothing Type

### 👕 TOPS (Shirts, T-shirts, Blouses)

**Currently Using:**
- ✅ neckline (collar detection)
- ✅ material (gym: performance fabrics, formal: wool/silk)
- ✅ fit (gym: loose/athletic, formal: tailored)
- ✅ pattern (gym: solid/striped preferred)

**MISSING:**
- ❌ `sleeveLength` - **CRITICAL for gym!**
  - Gym: sleeveless/short sleeves = +boost
  - Formal: long sleeves = +boost
  - Winter: short sleeves = penalty
- ❌ `fabricWeight` - **Weather-dependent!**
  - Summer: heavy = penalty
  - Winter: light = penalty
- ❌ `formalLevel` - **Direct occasion matching!**
  - Gym: casual = boost, formal = block
  - Business: formal = boost, casual = penalty
- ❌ `warmthFactor` - **Weather-dependent!**
  - Cold weather: heavy warmth = boost
  - Hot weather: heavy warmth = penalty

---

### 👖 BOTTOMS (Pants, Shorts, Skirts)

**Currently Using:**
- ✅ material (gym: performance, formal: wool)
- ✅ fit (gym: athletic, formal: tailored)
- ✅ waistbandType (gym: elastic, formal: belt loops)
- ✅ occasion tags

**MISSING:**
- ❌ `length` - **CRITICAL for occasion matching!**
  - Gym: short = boost (shorts preferred)
  - Formal: long = boost (no shorts!)
  - Loungewear: any length OK
- ❌ `formalLevel` - **Direct occasion matching!**
  - Same as tops
- ❌ `silhouette` - **Important for fit analysis!**
  - Gym: relaxed/straight = boost
  - Formal: tailored = boost

---

### 👟 SHOES

**Currently Using:**
- ✅ material (leather = formal, mesh = athletic)
- ✅ occasion tags

**MISSING:**
- ❌ `shoeType` - **We check for it but it's not in the model!**
  - Should be added to VisualAttributes
- ❌ `formalLevel` - **Direct occasion matching!**
  - Formal: formal = boost
  - Gym: casual = boost

---

### 🧥 OUTERWEAR (Jackets, Coats, Blazers)

**Currently Using:**
- ❌ **NOTHING!** Outerwear uses NO metadata currently!

**MISSING:**
- ❌ `material` - **CRITICAL!**
  - Wool coat vs mesh windbreaker
- ❌ `warmthFactor` - **Weather-dependent!**
  - Cold: heavy warmth = boost
  - Mild: light warmth = boost
- ❌ `layerLevel` / `wearLayer` - **Layering logic!**
  - Which layer (base, mid, outer)
- ❌ `formalLevel` - **Occasion matching!**
  - Business: blazer (formal) = boost
  - Gym: windbreaker (casual) = boost
- ❌ `length` - **Important!**
  - Winter: long coat = boost
  - Fall: cropped jacket = boost

---

### 🎩 ACCESSORIES (Belts, Hats, Scarves, etc.)

**Currently Using:**
- ❌ **NOTHING!** Only name-based blocking

**MISSING:**
- ❌ `formalLevel` - **Occasion matching!**
  - Gym: block all formal accessories
  - Business: allow formal accessories
- ❌ `material` - **Quality/occasion indicator!**
  - Leather belt = formal
  - Fabric belt = casual
- ❌ `warmthFactor` - **For scarves/hats!**
  - Cold weather: warm scarf = boost

---

## Recommended Next Fixes

### Priority 1: CRITICAL Fields
1. **`sleeveLength`** for tops - Affects gym/formal/weather
2. **`length`** for bottoms - Distinguishes shorts from pants
3. **`formalLevel`** for all items - Direct occasion matching
4. **`warmthFactor`** for outerwear - Weather matching

### Priority 2: Important Fields
5. **`fabricWeight`** for tops/bottoms - Weather matching
6. **`silhouette`** for bottoms - Fit analysis
7. **`wearLayer`** for outerwear - Layering logic

### Priority 3: Nice-to-Have
8. **`textureStyle`** for all items - Aesthetic matching
9. **Complex nested fields** (temperatureCompatibility, bodyTypeCompatibility)

---

## Implementation Estimate

**Adding Priority 1 fields:**
- 4 metadata fields × 3 occasions (gym, formal, loungewear) = ~12 new checks
- Estimated: +200 lines of code
- Impact: **MAJOR improvement** in filtering accuracy

**Full implementation (all fields):**
- 15+ metadata fields × 5 clothing types × 4 occasions = 300+ checks
- Estimated: +500-800 lines of code
- Impact: **Complete metadata-driven outfit generation**

---

## Question for You:

Should I:
1. **Add Priority 1 fields only** (~200 lines, critical improvements)
2. **Add Priority 1 + 2 fields** (~400 lines, comprehensive)
3. **Full implementation** (~800 lines, complete metadata coverage)
4. **Let me audit the actual Firestore data first** to see which fields are populated?

