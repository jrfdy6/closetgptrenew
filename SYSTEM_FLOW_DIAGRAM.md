# 📊 Semantic Filtering System - Visual Flow Diagrams

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                    (Next.js/React Frontend)                      │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Filter UI  │  │ Semantic     │  │  Debug Panel        │   │
│  │             │  │ Toggle       │  │                     │   │
│  │ • Occasion  │  │ ○ Traditional│  │  ✅ Valid Items     │   │
│  │ • Style     │  │ ● Semantic   │  │  ❌ Rejected Items  │   │
│  │ • Mood      │  │              │  │  📊 Statistics      │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└────────────────────────────┬──────────────────────────────────┘
                             │ HTTPS/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API (FastAPI)                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              /api/outfits/debug-filter                    │  │
│  │         (main_hybrid.py - API Endpoint)                   │  │
│  │                                                            │  │
│  │  Input: { occasion, style, mood, semantic: true/false }   │  │
│  └─────────────────────────┬────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      RobustOutfitGenerationService                        │  │
│  │  (_filter_suitable_items_with_debug)                      │  │
│  │                                                            │  │
│  │  ┌─────────────────┐      ┌──────────────────┐          │  │
│  │  │ Feature Flags   │      │  Normalization   │          │  │
│  │  │ Check           │─────▶│  Process         │          │  │
│  │  └─────────────────┘      └──────────────────┘          │  │
│  │                                    │                      │  │
│  │                                    ▼                      │  │
│  │            ┌─────────────────────────────────┐           │  │
│  │            │   FILTERING MODE DECISION       │           │  │
│  │            │                                 │           │  │
│  │            │  Semantic? ──Yes──▶ Use         │           │  │
│  │            │     │              Compatibility │           │  │
│  │            │     No               Matrix     │           │  │
│  │            │     │                           │           │  │
│  │            │     └──▶ Use Exact             │           │  │
│  │            │          Matching              │           │  │
│  │            └─────────────────────────────────┘           │  │
│  │                          │                                │  │
│  │                          ▼                                │  │
│  │            ┌──────────────────────────┐                  │  │
│  │            │  Item Filtering Loop     │                  │  │
│  │            │  (for each wardrobe item)│                  │  │
│  │            └──────────────────────────┘                  │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Response Assembly                            │  │
│  │  • valid_items[]                                          │  │
│  │  • debug_analysis[]                                       │  │
│  │  • summary statistics                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (Firestore)                        │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  wardrobe Collection                      │  │
│  │                                                            │  │
│  │  Document {                                               │  │
│  │    id, name, category, color,                            │  │
│  │    style: ["Classic", "Professional"],                   │  │
│  │    occasion: ["Business", "Formal"],                     │  │
│  │    mood: ["Professional"],                               │  │
│  │    normalized: {                                         │  │
│  │      style: ["classic", "professional"],                 │  │
│  │      occasion: ["business", "formal"],                   │  │
│  │      mood: ["professional"]                              │  │
│  │    }                                                      │  │
│  │  }                                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Filtering Flow

```
START: User Requests "Classic" Style Outfit
│
├─▶ STEP 1: Load User's Wardrobe from Firestore
│   │
│   └─▶ Items: [Item1, Item2, Item3, ..., ItemN]
│
├─▶ STEP 2: Feature Flag Check
│   │
│   ├─ FEATURE_FORCE_TRADITIONAL? ──Yes──▶ mode = "traditional"
│   │                              │
│   │                              No
│   │                              │
│   ├─ semantic parameter? ─────Yes──▶ mode = request parameter
│   │                        │
│   │                        No
│   │                        │
│   └─ FEATURE_SEMANTIC_MATCH? ──Yes──▶ mode = "semantic"
│                                 │
│                                 No
│                                 │
│                                 └──▶ mode = "traditional"
│
├─▶ STEP 3: For Each Item in Wardrobe
│   │
│   ├─▶ NORMALIZE metadata
│   │   │
│   │   ├─ style: ["Business Casual"] → ["business_casual"]
│   │   ├─ occasion: ["Work"] → ["work"]
│   │   └─ mood: ["Professional"] → ["professional"]
│   │
│   ├─▶ CHECK FILTERS (based on mode)
│   │
│   ├─── MODE: SEMANTIC ───────────────────────────┐
│   │                                               │
│   │   ┌─────────────────────────────────────┐   │
│   │   │ style_matches("classic",            │   │
│   │   │   ["business_casual"])              │   │
│   │   │                                     │   │
│   │   │ 1. Normalize: "classic" → "classic"│   │
│   │   │              "Business Casual" →   │   │
│   │   │              "business_casual"     │   │
│   │   │                                     │   │
│   │   │ 2. Check exact match: No           │   │
│   │   │                                     │   │
│   │   │ 3. Load compatibility matrix:      │   │
│   │   │    STYLE_COMPATIBILITY["classic"]  │   │
│   │   │    = ["classic", "business_casual",│   │
│   │   │       "smart_casual", ...]         │   │
│   │   │                                     │   │
│   │   │ 4. Check if "business_casual"      │   │
│   │   │    in compatibility list: YES! ✅  │   │
│   │   │                                     │   │
│   │   │ 5. Return: True (MATCH)            │   │
│   │   └─────────────────────────────────────┘   │
│   │                                               │
│   │   Same process for occasion_matches()        │
│   │   and mood_matches()                         │
│   │                                               │
│   └───────────────────────────────────────────────┘
│   │
│   ├─── MODE: TRADITIONAL ─────────────────────────┐
│   │                                               │
│   │   ┌─────────────────────────────────────┐   │
│   │   │ Check exact match (case-insensitive)│   │
│   │   │                                     │   │
│   │   │ request: "classic"                 │   │
│   │   │ item: ["business_casual"]          │   │
│   │   │                                     │   │
│   │   │ "classic".lower() in               │   │
│   │   │   ["business_casual".lower()]      │   │
│   │   │                                     │   │
│   │   │ Result: No match ❌                │   │
│   │   │                                     │   │
│   │   │ Return: False (NO MATCH)            │   │
│   │   └─────────────────────────────────────┘   │
│   │                                               │
│   └───────────────────────────────────────────────┘
│   │
│   ├─▶ IF all filters pass (style AND occasion AND mood)
│   │   │
│   │   └──▶ Add to valid_items[] ✅
│   │
│   └─▶ ELSE
│       │
│       └──▶ Add to rejected_items[] ❌
│            Record rejection reasons:
│            • "Style mismatch: item styles ['...']"
│            • "Occasion mismatch: item occasions ['...']"
│            • "Mood mismatch: item moods ['...']"
│
├─▶ STEP 4: Weather Filtering (if weather provided)
│   │
│   └─▶ For each item in valid_items:
│       │
│       ├─ Temperature suitable? ─No─▶ Remove
│       │                        │
│       │                        Yes
│       │                        │
│       └─ Weather suitable? ──No──▶ Remove
│                             │
│                             Yes
│                             │
│                             Keep ✅
│
└─▶ STEP 5: Return Results
    │
    └─▶ Response {
          valid_items: [...items that passed...],
          debug_analysis: [
            {
              id: "item1",
              name: "Classic Blazer",
              valid: true,
              reasons: []
            },
            {
              id: "item2",
              name: "Business Casual Chinos",
              valid: true (semantic) / false (traditional),
              reasons: [] / ["Style mismatch"]
            },
            {
              id: "item3",
              name: "Athletic Shorts",
              valid: false,
              reasons: ["Style mismatch", "Occasion mismatch"]
            }
          ],
          summary: {
            total_items: 77,
            valid_items: 45 (semantic) / 12 (traditional),
            rejected_items: 32 (semantic) / 65 (traditional),
            filter_pass_rate: 0.58 (semantic) / 0.16 (traditional)
          }
        }

END
```

---

## 3. Semantic vs Traditional Comparison

```
┌───────────────────────────────────────────────────────────────┐
│              REQUEST: "Classic" Style                          │
└───────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │  TRADITIONAL MODE    │    │   SEMANTIC MODE      │
    │  (Exact Match Only)  │    │  (Compatibility)     │
    └──────────────────────┘    └──────────────────────┘
                │                           │
                ▼                           ▼

Item: "Classic Blazer"       Item: "Classic Blazer"
Style: ["Classic"]           Style: ["Classic"]
                                     
Match Check:                 Match Check:
"classic" == "classic"       "classic" == "classic"
✅ PASS                      ✅ PASS (Exact)

────────────────────────────────────────────────────

Item: "Business Casual       Item: "Business Casual
       Chinos"                     Chinos"
Style: ["Business Casual"]   Style: ["Business Casual"]

Match Check:                 Match Check:
"classic" == "business_      1. "classic" == "business_
            casual"                      casual"? No
❌ FAIL                      2. Check matrix:
                                STYLE_COMPATIBILITY
                                  ["classic"] contains
                                  "business_casual"? Yes
                             ✅ PASS (Semantic)

────────────────────────────────────────────────────

Item: "Smart Casual Shirt"   Item: "Smart Casual Shirt"
Style: ["Smart Casual"]      Style: ["Smart Casual"]

Match Check:                 Match Check:
"classic" == "smart_casual"  1. Exact? No
❌ FAIL                      2. Matrix? Yes
                             ✅ PASS (Semantic)

────────────────────────────────────────────────────

Item: "Preppy Vest"          Item: "Preppy Vest"
Style: ["Preppy"]            Style: ["Preppy"]

Match Check:                 Match Check:
"classic" == "preppy"        1. Exact? No
❌ FAIL                      2. Matrix? Yes
                             ✅ PASS (Semantic)

────────────────────────────────────────────────────

Item: "Athletic Shorts"      Item: "Athletic Shorts"
Style: ["Athletic"]          Style: ["Athletic"]

Match Check:                 Match Check:
"classic" == "athletic"      1. Exact? No
❌ FAIL                      2. Matrix? No
                             ❌ FAIL (No compatibility)

────────────────────────────────────────────────────

RESULTS:                     RESULTS:

Traditional Mode:            Semantic Mode:
✅ 1 item matched           ✅ 4 items matched
❌ 4 items rejected         ❌ 1 item rejected
📊 20% pass rate            📊 80% pass rate

Limited outfit options       More outfit options
Strict requirements          Flexible matching
```

---

## 4. Data Normalization Process

```
┌─────────────────────────────────────────────────────────────┐
│                    RAW ITEM DATA                             │
│                   (From Database)                            │
│                                                               │
│  {                                                           │
│    id: "item_123",                                          │
│    name: "Blue Blazer",                                     │
│    style: "Business Casual",      ← String (not array)      │
│    occasion: ["Business", " Formal "],  ← Extra spaces      │
│    mood: None,                    ← Missing field           │
│    season: ["Summer", "FALL"]     ← Mixed case              │
│  }                                                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  normalize_item_metadata()    │
        └───────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌─────────────────┐           ┌─────────────────┐
│ STEP 1:         │           │ STEP 2:         │
│ Convert to      │           │ Lowercase       │
│ Arrays          │           │ All Strings     │
│                 │           │                 │
│ "Business       │           │ ["Business      │
│  Casual"        │           │  Casual"]       │
│    ↓            │           │    ↓            │
│ ["Business      │           │ ["business      │
│  Casual"]       │           │  casual"]       │
└────────┬────────┘           └────────┬────────┘
         │                             │
         └──────────┬──────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │ STEP 3: Strip Whitespace      │
        │                               │
        │ [" Formal "] → ["formal"]     │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │ STEP 4: Remove Empty/None     │
        │                               │
        │ [None, "", "text"] → ["text"] │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │ STEP 5: Deduplicate           │
        │                               │
        │ ["a", "b", "a"] → ["a", "b"]  │
        └───────────────┬───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 NORMALIZED ITEM DATA                         │
│                (Ready for Matching)                          │
│                                                               │
│  {                                                           │
│    style: ["business_casual"],        ✅ Normalized         │
│    occasion: ["business", "formal"],  ✅ Cleaned            │
│    mood: [],                          ✅ Empty array        │
│    season: ["summer", "fall"]         ✅ Lowercase          │
│  }                                                           │
│                                                               │
│  This data is now ready for:                                │
│  • Exact matching (traditional mode)                        │
│  • Semantic matching (compatibility matrix)                 │
│  • Consistent comparison                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Style Compatibility Matrix Structure

```
┌─────────────────────────────────────────────────────────────┐
│          STYLE_COMPATIBILITY MATRIX (64 Styles)              │
│                                                               │
│  Dictionary structure:                                       │
│  {                                                           │
│    "style_name": ["compatible_style_1", "compatible_2", ...]│
│  }                                                           │
└─────────────────────────────────────────────────────────────┘

Examples:

┌──────────────────┬─────────────────────────────────────────┐
│ "classic"        │ ["classic", "casual", "smart_casual",   │
│                  │  "business_casual", "traditional",      │
│                  │  "preppy", "minimalist", "balanced"]    │
└──────────────────┴─────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│"business_    │  │"smart_       │  │"preppy"      │
│ casual"      │  │ casual"      │  │              │
│              │  │              │  │              │
│["business_   │  │["smart_      │  │["preppy",    │
│ casual",     │  │ casual",     │  │ "classic",   │
│ "classic",   │  │ "classic",   │  │ "traditional"│
│ "casual",    │  │ "business_   │  │ "polished",  │
│ "preppy"]    │  │  casual",    │  │ "old_money"] │
│              │  │ "casual"]    │  │              │
└──────────────┘  └──────────────┘  └──────────────┘

Bidirectional relationships ensure consistent matching!

┌──────────────────┬─────────────────────────────────────────┐
│ "athletic"       │ ["athletic", "sporty", "activewear",    │
│                  │  "casual", "streetwear"]                │
└──────────────────┴─────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│"sporty"      │  │"activewear"  │  │"casual"      │
│              │  │              │  │              │
│["sporty",    │  │["activewear",│  │["casual",    │
│ "athletic",  │  │ "athletic",  │  │ "classic",   │
│ "energetic", │  │ "sporty",    │  │ "relaxed",   │
│ "active"]    │  │ "fitness"]   │  │ "athletic"]  │
└──────────────┘  └──────────────┘  └──────────────┘

Key features:
• Self-inclusive (each style includes itself)
• Lowercase with underscores
• Symmetric relationships (mostly)
• Covers 64 distinct styles
• Extensible for new styles
```

---

## 6. Frontend UI Component Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│         /personalization-demo Page Component                 │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Header & Description                       │ │
│  │  "Safe testing environment - won't affect your app"    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Filter Controls Section                       │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │ │
│  │  │ Occasion     │  │ Style        │  │ Mood        │  │ │
│  │  │ Dropdown     │  │ Dropdown     │  │ Dropdown    │  │ │
│  │  │              │  │              │  │             │  │ │
│  │  │ • Athletic   │  │ • Classic    │  │ • Bold      │  │ │
│  │  │ • Business   │  │ • Casual     │  │ • Relaxed   │  │ │
│  │  │ • Casual     │  │ • Modern     │  │ • Prof.     │  │ │
│  │  │ • Formal     │  │ • Romantic   │  │ • Romantic  │  │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Semantic Matching Toggle                       │ │
│  │                                                          │ │
│  │  🧠 Semantic Matching (Experimental)                   │ │
│  │                                                          │ │
│  │  ○ Traditional (Exact Match)                           │ │
│  │  ● Semantic (Compatible Styles)                        │ │
│  │                                                          │ │
│  │  Info: "Semantic: Compatible styles                    │ │
│  │         (e.g., Classic ≈ Business Casual)"             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Action Buttons                             │ │
│  │                                                          │ │
│  │  [Generate Outfit]  [Debug Item Filtering]             │ │
│  │                                                          │ │
│  │  onClick: handleGenerateOutfit()                       │ │
│  │  onClick: handleDebugFilter()                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Results Section                            │ │
│  │                                                          │ │
│  │  {outfit ? (                                           │ │
│  │    <OutfitDisplay outfit={outfit} />                   │ │
│  │  ) : null}                                             │ │
│  │                                                          │ │
│  │  {debugAnalysis ? (                                    │ │
│  │    <DebugPanel analysis={debugAnalysis} />             │ │
│  │  ) : null}                                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Debug Panel (Expandable)                   │ │
│  │                                                          │ │
│  │  📊 Filter Pass Rate: 58% (45/77 items)               │ │
│  │  🚩 Semantic Mode: Active                             │ │
│  │                                                          │ │
│  │  Items:                                                │ │
│  │  ✅ Classic Blazer - MATCHED                          │ │
│  │  ✅ Business Casual Pants - MATCHED (semantic)        │ │
│  │  ❌ Athletic Shorts - REJECTED                        │ │
│  │     Reasons:                                           │ │
│  │     • Style mismatch: ['athletic']                    │ │
│  │     • Occasion mismatch: ['sport']                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

**Document**: Visual Flow Diagrams  
**Version**: 1.0  
**Last Updated**: October 7, 2025  
**Companion To**: SYSTEM_ARCHITECTURE_DOCUMENTATION.md

