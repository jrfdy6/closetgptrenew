# 🏗️ Semantic Filtering System - Complete Architecture Documentation

**Last Updated**: October 7, 2025  
**System Status**: ✅ Production Ready  
**Version**: 1.0

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Utility Functions](#utility-functions)
9. [Feature Flags](#feature-flags)
10. [Testing & Validation](#testing--validation)

---

## 1. System Overview

### Purpose
The Semantic Filtering System enables flexible outfit generation by understanding style compatibility rather than requiring exact matches. For example, a user searching for "Classic" style items will also see "Business Casual" items because they are semantically compatible.

### Key Features
- **Semantic Style Matching**: Understands compatibility between styles
- **Dual Mode Operation**: Toggle between traditional (exact match) and semantic (compatible match)
- **Debug Transparency**: Shows why items match or don't match
- **Feature Flag Control**: Easy rollback and gradual rollout
- **Data Normalization**: Consistent formatting for reliable matching

### Architecture Pattern
```
Frontend (Next.js/React) 
    ↓ API Request
Backend (FastAPI/Python)
    ↓ Query
Database (Firestore)
    ↓ Data
Filtering Service (Semantic/Traditional)
    ↓ Results
Frontend Display
```

---

## 2. Core Components

### Backend Components

#### 2.1 `semantic_compatibility.py`
**Location**: `backend/src/utils/semantic_compatibility.py`

**Purpose**: Core matching logic for styles, moods, and occasions

**Functions**:

##### `style_matches(requested_style: Optional[str], item_styles: List[str]) -> bool`
Checks if an item's styles match the requested style using semantic compatibility.

**Inputs**:
- `requested_style` (Optional[str]): The style the user is looking for (e.g., "Classic", "Business Casual")
  - Can be None (matches everything)
  - Case-insensitive
  - Spaces converted to underscores internally
  
- `item_styles` (List[str]): The styles tagged on the wardrobe item
  - Array of style strings
  - Can be empty (no filtering applied)
  - Case-insensitive

**Output**:
- `bool`: True if item matches (exact or semantic), False otherwise

**Logic**:
1. If no requested_style, return True (no filter)
2. Normalize requested_style: lowercase + spaces→underscores
3. Check for exact match in item_styles (normalized)
4. If no exact match, check STYLE_COMPATIBILITY matrix
5. Return True if any item style is in compatibility set

**Example**:
```python
# Exact match
style_matches("classic", ["Classic", "Modern"])  # True

# Semantic match
style_matches("classic", ["Business Casual"])  # True (compatible)

# No match
style_matches("classic", ["Athletic"])  # False (not compatible)

# No filter
style_matches(None, ["Anything"])  # True
```

---

##### `mood_matches(requested_mood: Optional[str], item_moods: List[str]) -> bool`
Checks if an item's moods match the requested mood using semantic compatibility.

**Inputs**:
- `requested_mood` (Optional[str]): The mood the user wants (e.g., "Professional", "Relaxed")
  - Can be None (matches everything)
  - Case-insensitive
  
- `item_moods` (List[str]): The moods tagged on the wardrobe item
  - Array of mood strings
  - Empty array treated as universal match
  - Case-insensitive

**Output**:
- `bool`: True if item matches (exact or semantic), False otherwise

**Compatibility Map**:
```python
{
    'bold': ['bold', 'confident', 'statement', 'vibrant', 'expressive'],
    'confident': ['confident', 'bold', 'statement', 'vibrant', 'expressive'],
    'relaxed': ['relaxed', 'calm', 'laidback', 'casual', 'neutral'],
    'calm': ['calm', 'relaxed', 'peaceful', 'serene', 'neutral'],
    'professional': ['professional', 'polished', 'sophisticated', 'elegant', 'refined'],
    'romantic': ['romantic', 'soft', 'elegant', 'feminine', 'delicate'],
    # ... more mappings
}
```

**Example**:
```python
mood_matches("professional", ["Polished"])  # True (compatible)
mood_matches("relaxed", ["Calm"])  # True (compatible)
mood_matches("bold", ["Relaxed"])  # False (not compatible)
```

---

##### `occasion_matches(requested_occasion: Optional[str], item_occasions: List[str]) -> bool`
Checks if an item's occasions match the requested occasion using semantic compatibility.

**Inputs**:
- `requested_occasion` (Optional[str]): The occasion (e.g., "Business", "Casual", "Athletic")
  - Can be None (matches everything)
  - Case-insensitive
  - Spaces converted to underscores
  
- `item_occasions` (List[str]): The occasions tagged on the item
  - Array of occasion strings
  - Case-insensitive

**Output**:
- `bool`: True if item matches (exact or fallback), False otherwise

**Fallback Map**:
```python
{
    'athletic': ['casual', 'everyday', 'sport', 'athletic', 'workout'],
    'casual': ['everyday', 'casual', 'relaxed', 'weekend'],
    'business': ['business', 'business_casual', 'formal', 'smart_casual'],
    'formal': ['formal', 'business', 'elegant', 'sophisticated'],
    'everyday': ['everyday', 'casual', 'relaxed', 'comfortable'],
    # ... more mappings
}
```

**Example**:
```python
occasion_matches("business", ["Business Casual"])  # True (fallback)
occasion_matches("casual", ["Everyday"])  # True (fallback)
occasion_matches("formal", ["Athletic"])  # False (no fallback)
```

---

#### 2.2 `style_compatibility_matrix.py`
**Location**: `backend/src/utils/style_compatibility_matrix.py`

**Purpose**: Defines which styles are compatible with each other

**Data Structure**: `STYLE_COMPATIBILITY: Dict[str, List[str]]`

**Format**:
```python
STYLE_COMPATIBILITY = {
    "style_name": ["compatible_style_1", "compatible_style_2", ...],
    ...
}
```

**Key Principles**:
1. **Canonical Format**: All lowercase, underscores for spaces
2. **Self-Inclusive**: Each style includes itself in its compatibility list
3. **Symmetric Relationships**: If A→B, then B→A (mostly)
4. **64 Styles Covered**: Comprehensive coverage of fashion styles

**Example Entries**:
```python
{
    "classic": [
        "classic", "casual", "smart_casual", "business_casual",
        "traditional", "preppy", "minimalist", "balanced"
    ],
    "business_casual": [
        "business_casual", "business", "smart_casual", "classic",
        "casual", "preppy"
    ],
    "athletic": [
        "athletic", "sporty", "activewear", "casual", "streetwear"
    ],
    # ... 61 more styles
}
```

**Usage**:
```python
from backend.src.utils.style_compatibility_matrix import STYLE_COMPATIBILITY

# Check if "business_casual" is compatible with "classic"
compatibles = STYLE_COMPATIBILITY.get("classic", [])
is_compatible = "business_casual" in compatibles  # True
```

---

#### 2.3 `semantic_normalization.py`
**Location**: `backend/src/utils/semantic_normalization.py`

**Purpose**: Normalize wardrobe item metadata for consistent matching

**Main Function**:

##### `normalize_item_metadata(item: Union[Dict, Any]) -> Dict[str, Any]`
Normalizes an item's metadata fields to ensure consistent matching.

**Inputs**:
- `item` (Union[Dict, Any]): A wardrobe item as dictionary or object
  - Can be a plain dict
  - Can be a Pydantic model or similar object with attributes
  - May have fields: style, occasion, mood, season, category, tags

**Output**:
- `Dict[str, Any]`: Normalized item metadata with these fields:
  - `style` (List[str]): Normalized style tags (lowercase, stripped)
  - `occasion` (List[str]): Normalized occasion tags
  - `mood` (List[str]): Normalized mood tags
  - `season` (List[str]): Normalized season tags
  - `category` (str): Normalized category (lowercase)
  - `tags` (List[str]): Normalized additional tags

**Normalization Process**:
1. **Extract Fields**: Get fields from dict or object attributes
2. **Convert to Arrays**: Ensure all fields are lists (convert strings/None)
3. **Lowercase**: Convert all strings to lowercase
4. **Strip Whitespace**: Remove leading/trailing spaces
5. **Remove Empty**: Filter out empty strings and None values
6. **Deduplicate**: Remove duplicate values

**Example**:
```python
# Input
item = {
    "id": "123",
    "name": "Blue Blazer",
    "style": "Classic",  # String, uppercase
    "occasion": ["Business", " Formal "],  # Mixed, extra spaces
    "mood": None,  # Missing field
    "season": ["Summer", "FALL"]  # Mixed case
}

# Output
normalized = normalize_item_metadata(item)
# {
#     "style": ["classic"],
#     "occasion": ["business", "formal"],
#     "mood": [],
#     "season": ["summer", "fall"],
#     "category": "",
#     "tags": []
# }
```

**Special Cases**:
- `None` values → empty list `[]`
- Single string → list with one item `["value"]`
- Empty strings removed from lists
- Preserves original item ID and name (doesn't normalize those)

---

#### 2.4 `robust_outfit_generation_service.py`
**Location**: `backend/src/services/robust_outfit_generation_service.py`

**Purpose**: Main service for filtering wardrobe items and generating outfits

**Key Class**: `RobustOutfitGenerationService`

**Main Method**:

##### `_filter_suitable_items_with_debug(context: GenerationContext, semantic_filtering: bool = None) -> Dict[str, Any]`
Filters wardrobe items based on context (style, occasion, mood, weather) and returns detailed debug information.

**Inputs**:
- `context` (GenerationContext): Request context containing:
  - `user_profile` (UserProfile): User information and preferences
  - `occasion` (str): Requested occasion (e.g., "business", "casual")
  - `style` (str): Requested style (e.g., "classic", "modern")
  - `mood` (str): Requested mood (e.g., "professional", "relaxed")
  - `weather` (WeatherData): Current/forecasted weather
  - `wardrobe` (List[ClothingItem]): User's wardrobe items
  - `body_type` (str): User's body type for fitting
  
- `semantic_filtering` (bool, optional): Force semantic (True) or traditional (False) mode
  - If None, uses feature flags to determine mode
  - If True, uses semantic compatibility matching
  - If False, uses exact case-insensitive matching

**Output**:
- `Dict[str, Any]` with these keys:
  - `valid_items` (List[ClothingItem]): Items that passed all filters
  - `debug_analysis` (List[Dict]): Detailed analysis of each item:
    - `id` (str): Item identifier
    - `name` (str): Item name
    - `valid` (bool): Whether item passed filters
    - `reasons` (List[str]): Rejection reasons if invalid
    - `semantic_match_info` (Dict): Semantic matching details
  - `debug_output` (Dict, optional): Summary statistics if debug enabled:
    - `filtering_mode` (str): "semantic" or "traditional"
    - `semantic_filtering_used` (bool): Whether semantic was active
    - `filtering_stats` (Dict): Item counts at each stage
    - `feature_flags` (Dict): Active feature flag values

**Filtering Logic**:

**Semantic Mode** (`semantic_filtering=True`):
```python
# For each item:
ok_occasion = occasion_matches(context.occasion, item.occasion)
ok_style = style_matches(context.style, item.style)
ok_mood = mood_matches(context.mood, item.mood)

if ok_occasion and ok_style and ok_mood:
    # Item passes semantic filter
    valid_items.append(item)
```

**Traditional Mode** (`semantic_filtering=False`):
```python
# For each item:
req_occasion = context.occasion.lower()
req_style = context.style.lower()
req_mood = context.mood.lower()

ok_occasion = req_occasion in [o.lower() for o in item.occasion]
ok_style = req_style in [s.lower() for s in item.style]
ok_mood = req_mood in [m.lower() for m in item.mood]

if ok_occasion and ok_style and ok_mood:
    # Item passes traditional filter
    valid_items.append(item)
```

**Weather Filtering** (Applied after semantic/traditional):
```python
# Additional temperature/weather suitability check
if context.weather:
    for item in valid_items:
        if not item_suitable_for_weather(item, context.weather):
            weather_rejected.append(item)
    
    valid_items = [i for i in valid_items if i not in weather_rejected]
```

**Example Usage**:
```python
service = RobustOutfitGenerationService()

context = GenerationContext(
    occasion="business",
    style="classic",
    mood="professional",
    wardrobe=[item1, item2, item3, ...]
)

# Semantic filtering
result = await service._filter_suitable_items_with_debug(
    context,
    semantic_filtering=True
)

print(result['valid_items'])  # Items that passed
print(result['debug_analysis'])  # Why each item passed/failed
```

**Rejection Reasons**:
- `"Occasion mismatch: item occasions [...]"`: Item occasions don't match request
- `"Style mismatch: item styles [...]"`: Item styles don't match request
- `"Mood mismatch: item moods [...]"`: Item moods don't match request
- `"Temperature unsuitability"`: Item not suitable for weather
- `"Weather conditions"`: Item not suitable for rain/snow/etc

---

### Frontend Components

#### 2.5 `/personalization-demo/page.tsx`
**Location**: `frontend/src/app/personalization-demo/page.tsx`

**Purpose**: User interface for testing semantic filtering with toggle and debug output

**Key State Variables**:

```typescript
// User's filter selections
const [occasion, setOccasion] = useState<string>('Athletic')
const [style, setStyle] = useState<string>('Classic')
const [mood, setMood] = useState<string>('Bold')

// Semantic toggle
const [semanticFlag, setSemanticFlag] = useState<boolean>(false)

// Results
const [outfit, setOutfit] = useState<any>(null)
const [debugAnalysis, setDebugAnalysis] = useState<any>(null)
```

**Key Functions**:

##### `handleGenerateOutfit()`
Generates outfit using the robust generation service.

**Inputs** (from state):
- `occasion`: Selected occasion
- `style`: Selected style
- `mood`: Selected mood
- `semanticFlag`: Whether to use semantic matching

**Process**:
1. Gets user's ID token for authentication
2. Calls `/api/outfits` endpoint with parameters
3. Receives generated outfit and metadata
4. Updates UI with results

**API Request**:
```typescript
const response = await fetch(`/api/outfits?semantic=${semanticFlag}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${idToken}`
  },
  body: JSON.stringify({
    occasion,
    style,
    mood,
    generator: 'robust'
  })
})
```

---

##### `handleDebugFilter()`
Shows detailed filtering analysis without generating outfit.

**Inputs** (from state):
- `occasion`, `style`, `mood`: Filter criteria
- `semanticFlag`: Filtering mode

**Process**:
1. Gets user's ID token
2. Calls `/api/outfits/debug-filter` endpoint
3. Receives item-by-item analysis
4. Displays in debug panel

**API Request**:
```typescript
const response = await fetch(`/api/outfits/debug-filter?semantic=${semanticFlag}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${idToken}`
  },
  body: JSON.stringify({
    occasion,
    style,
    mood
  })
})
```

**Debug Output Structure**:
```typescript
{
  success: boolean,
  debug: Array<{
    id: string,
    name: string,
    valid: boolean,
    reasons: string[],  // Rejection reasons
    semantic_match_info: {
      style_compatibility: any,
      occasion_compatibility: any,
      mood_compatibility: any
    }
  }>,
  semantic_mode: boolean,
  summary: {
    total_items: number,
    valid_items: number,
    rejected_items: number,
    filter_pass_rate: number
  }
}
```

---

**UI Components**:

##### Semantic Toggle
```tsx
<div className="semantic-toggle">
  <input
    type="radio"
    id="semantic-off"
    checked={!semanticFlag}
    onChange={() => setSemanticFlag(false)}
  />
  <label>Traditional (Exact Match)</label>
  
  <input
    type="radio"
    id="semantic-on"
    checked={semanticFlag}
    onChange={() => setSemanticFlag(true)}
  />
  <label>Semantic (Compatible Styles)</label>
</div>
```

##### Debug Panel
Shows item-by-item analysis:
- ✅ Green for valid items (passed filters)
- ❌ Red for rejected items (failed filters)
- Rejection reasons listed for each rejected item
- Summary statistics (pass rate, total items, etc.)

---

## 3. Data Flow

### Complete Request Flow

```
1. User selects filters in UI
   ├─ Occasion: "Business"
   ├─ Style: "Classic"
   ├─ Mood: "Professional"
   └─ Semantic Toggle: ON

2. Frontend sends API request
   POST /api/outfits?semantic=true
   {
     "occasion": "Business",
     "style": "Classic",
     "mood": "Professional",
     "generator": "robust"
   }

3. Backend receives request
   ├─ Authenticates user (Firebase token)
   ├─ Loads user's wardrobe from Firestore
   └─ Creates GenerationContext

4. Feature Flag Check
   if (semantic parameter == true):
       use_semantic = True
   elif (FEATURE_SEMANTIC_MATCH flag == true):
       use_semantic = True
   else:
       use_semantic = False

5. Item Filtering Loop
   For each item in wardrobe:
       ├─ Normalize metadata (lowercase, clean)
       ├─ Check occasion match (semantic or exact)
       ├─ Check style match (semantic or exact)
       ├─ Check mood match (semantic or exact)
       ├─ If all pass → add to valid_items
       └─ Record rejection reasons if failed

6. Weather Filtering (if weather data available)
   For each valid_item:
       ├─ Check temperature suitability
       ├─ Check weather condition suitability
       └─ Remove if unsuitable

7. Outfit Composition
   ├─ Select complementary items (top, bottom, shoes, etc.)
   ├─ Check visual harmony (colors, patterns)
   ├─ Validate dress code compliance
   └─ Generate outfit recommendation

8. Response Assembly
   {
     "outfits": [{...outfit details...}],
     "debug_analysis": [...item analysis...],
     "semantic_mode": true,
     "summary": {...statistics...}
   }

9. Frontend displays results
   ├─ Show generated outfit
   ├─ Display debug panel
   └─ Update statistics
```

---

## 4. Database Schema

### Firestore Collections

#### `wardrobe` Collection
**Document Structure**:
```typescript
{
  // Core Fields (Original)
  id: string,                    // Unique identifier
  userId: string,                // Owner's user ID
  name: string,                  // Item name
  category: string,              // "top", "bottom", "shoes", etc.
  color: string[],               // Color tags
  style: string[],               // Style tags (e.g., ["Classic", "Professional"])
  occasion: string[],            // Occasion tags (e.g., ["Business", "Formal"])
  mood: string[],                // Mood tags (e.g., ["Professional", "Confident"])
  season: string[],              // Season tags (e.g., ["Summer", "Fall"])
  imageUrl: string,              // URL to item image
  tags: string[],                // Additional tags
  metadata: {                    // Additional metadata
    brand: string,
    material: string,
    fit: string,
    ...
  },
  createdAt: Timestamp,
  updatedAt: Timestamp,
  
  // Normalized Fields (Added by backfill)
  normalized: {
    style: string[],             // Lowercase, cleaned style tags
    occasion: string[],          // Lowercase, cleaned occasion tags
    mood: string[],              // Lowercase, cleaned mood tags
    season: string[],            // Lowercase, cleaned season tags
    category: string,            // Lowercase category
    tags: string[],              // Lowercase tags
    normalized_at: string,       // ISO timestamp of normalization
    normalized_version: string   // Version for future migrations
  }
}
```

**Indexes**:
- `userId` - For querying user's wardrobe
- `category` - For filtering by category
- `normalized.style` - For semantic style queries (future)
- `normalized.occasion` - For semantic occasion queries (future)

---

## 5. API Endpoints

### Authentication
All endpoints except `/health` require Firebase authentication.

**Header Required**:
```
Authorization: Bearer <firebase_id_token>
```

---

### Outfit Generation Endpoints

#### `POST /api/outfits`
Generate outfit recommendations.

**Query Parameters**:
- `semantic` (boolean, optional): Force semantic mode
  - `true`: Use semantic matching
  - `false`: Use traditional matching
  - Default: Uses feature flag

**Request Body**:
```json
{
  "occasion": "business",
  "style": "classic",
  "mood": "professional",
  "weather": {
    "temperature": 72,
    "condition": "sunny"
  },
  "generator": "robust"
}
```

**Response**:
```json
{
  "success": true,
  "outfits": [{
    "id": "outfit_123",
    "items": [
      {
        "id": "item_1",
        "name": "Navy Blazer",
        "category": "top",
        "imageUrl": "https://...",
        "style": ["classic", "business_casual"],
        "reason": "Matches classic style request"
      },
      {...more items...}
    ],
    "confidence": 0.85,
    "personalization_score": 0.72,
    "validation": {
      "is_complete": true,
      "missing_categories": [],
      "meets_dress_code": true
    }
  }],
  "debug_output": {
    "filtering_mode": "semantic",
    "items_passed": 45,
    "items_rejected": 32,
    "filter_pass_rate": 0.58
  }
}
```

---

#### `POST /api/outfits/debug-filter`
Debug filtering without generating outfit.

**Query Parameters**:
- `semantic` (boolean): Filtering mode

**Request Body**:
```json
{
  "occasion": "business",
  "style": "classic",
  "mood": "professional",
  "wardrobe": [...]  // Optional: provide custom wardrobe for testing
}
```

**Response**:
```json
{
  "success": true,
  "debug": [
    {
      "id": "item_123",
      "name": "Blue Blazer",
      "valid": true,
      "reasons": [],
      "semantic_match_info": {
        "style_compatibility": "exact_match",
        "occasion_compatibility": "semantic_match",
        "mood_compatibility": "exact_match"
      }
    },
    {
      "id": "item_456",
      "name": "Athletic Shorts",
      "valid": false,
      "reasons": [
        "Style mismatch: item styles ['athletic']",
        "Occasion mismatch: item occasions ['sport', 'casual']"
      ],
      "semantic_match_info": null
    }
  ],
  "semantic_mode": true,
  "summary": {
    "total_items": 77,
    "valid_items": 45,
    "rejected_items": 32,
    "filter_pass_rate": 0.58,
    "semantic_mode_active": true
  },
  "filters_applied": {
    "occasion": "business",
    "style": "classic",
    "mood": "professional",
    "semantic_mode": true
  }
}
```

---

### Health & Status Endpoints

#### `GET /health`
System health check (no auth required).

**Response**:
```json
{
  "status": "healthy",
  "message": "Test simple router is working",
  "timestamp": "2025-10-07T10:25:00Z"
}
```

---

## 6. Feature Flags

### Configuration Files

**Location**: `backend/.env` or Railway environment variables

**Available Flags**:

#### `FEATURE_SEMANTIC_MATCH`
Controls whether semantic matching is enabled.

**Values**:
- `true`: Enable semantic compatibility matching
- `false`: Use traditional exact matching
- Default: `false`

**Impact**:
- When `true`: "Classic" matches "Business Casual", "Smart Casual", etc.
- When `false`: Only exact matches (case-insensitive)

---

#### `FEATURE_DEBUG_OUTPUT`
Controls whether debug output is included in responses.

**Values**:
- `true`: Include detailed debug information
- `false`: Return only essential data
- Default: `true` (for development)

**Impact**:
- When `true`: Responses include `debug_output` with filtering statistics
- When `false`: Minimal response (faster, less data transfer)

---

#### `FEATURE_FORCE_TRADITIONAL`
Emergency rollback flag to force traditional filtering.

**Values**:
- `true`: Override all settings, use traditional matching
- `false`: Normal operation
- Default: `false`

**Usage**: Set to `true` if semantic matching causes issues in production

---

### Feature Flag Precedence

```python
if FEATURE_FORCE_TRADITIONAL == true:
    use_semantic = False  # Override everything
elif semantic_parameter_in_request == true/false:
    use_semantic = semantic_parameter  # Explicit request wins
elif FEATURE_SEMANTIC_MATCH == true:
    use_semantic = True  # Feature flag default
else:
    use_semantic = False  # Safe default
```

---

## 7. Testing & Validation

### Test Files

#### `test_edge_cases_stress.py`
Comprehensive edge case and stress testing.

**Tests Included**:
1. Empty wardrobe
2. Null/missing fields
3. Malformed data types
4. Case sensitivity
5. Unicode and special characters
6. Very long strings (1000+ chars)
7. Semantic vs traditional comparison
8. All filters combined
9. Missing required fields
10. Boundary values
11. Large wardrobe (500 items)
12. Concurrent requests (20 parallel)
13. Rapid mode switching
14. Extreme style combinations

**Run Command**:
```bash
python3 test_edge_cases_stress.py
```

---

### Validation Results

**Current Status**: ✅ 24/24 tests passing (100%)

**Performance Benchmarks**:
- 50 items: ~200ms
- 100 items: ~230ms
- 500 items: ~430ms
- 20 concurrent: ~480ms total

---

## 8. Deployment

### Backend (Railway)

**URL**: https://closetgptrenew-backend-production.up.railway.app

**Environment Variables**:
```
FEATURE_SEMANTIC_MATCH=true
FEATURE_DEBUG_OUTPUT=true
FEATURE_FORCE_TRADITIONAL=false

FIREBASE_PROJECT_ID=...
FIREBASE_PRIVATE_KEY=...
FIREBASE_CLIENT_EMAIL=...
```

**Deployment Process**:
1. Push to `main` branch on GitHub
2. Railway automatically detects changes
3. Builds and deploys new version
4. Health check confirms deployment success

---

### Frontend (Vercel)

**URL**: https://closetgpt-frontend.vercel.app

**Demo Page**: https://closetgpt-frontend.vercel.app/personalization-demo

**Build Configuration**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs"
}
```

---

### Database (Firestore)

**Backfill Status**:
- ✅ 179 items normalized
- ✅ 100% success rate
- ✅ Zero errors

**Backfill Command**:
```bash
python3 LOCAL_BACKFILL_SCRIPT.py --environment production
```

---

## 9. Troubleshooting

### Common Issues

#### Issue: Items not matching with semantic mode
**Cause**: Style not in compatibility matrix or incorrectly formatted

**Solution**:
1. Check `style_compatibility_matrix.py`
2. Ensure style uses underscores (e.g., `business_casual` not `business casual`)
3. Verify item styles are normalized (lowercase)

---

#### Issue: All items being rejected
**Cause**: Filters too restrictive or mismatched occasion/mood

**Solution**:
1. Check debug output for rejection reasons
2. Verify occasion/mood tags on items
3. Try with semantic mode enabled
4. Check if items have empty occasion/mood arrays

---

#### Issue: Slow response times
**Cause**: Large wardrobe or complex filtering

**Solution**:
1. Optimize database queries (add indexes)
2. Implement caching for frequent requests
3. Reduce wardrobe size for testing
4. Check backend logs for bottlenecks

---

## 10. Future Enhancements

### Planned Features
1. **Machine Learning**: Learn compatibility from user behavior
2. **Personalized Matrix**: User-specific style preferences
3. **Confidence Scores**: Show match quality (80% semantic match vs 100% exact)
4. **Fallback Levels**: Multiple tiers of semantic matching
5. **Weather Integration**: Automatic seasonal filtering
6. **Analytics Dashboard**: Monitor semantic vs traditional usage
7. **A/B Testing**: Compare user satisfaction between modes

---

## Appendix A: Quick Reference

### Key File Locations
```
backend/
├── src/
│   ├── utils/
│   │   ├── semantic_compatibility.py      # Core matching logic
│   │   ├── style_compatibility_matrix.py  # 64-style matrix
│   │   └── semantic_normalization.py      # Data cleaning
│   ├── services/
│   │   └── robust_outfit_generation_service.py  # Main filtering
│   └── routes/
│       └── outfits/
│           └── main_hybrid.py             # API endpoints
├── .env                                   # Feature flags
└── app.py                                 # FastAPI app

frontend/
└── src/
    └── app/
        └── personalization-demo/
            └── page.tsx                   # UI with toggle

scripts/
├── backfill_normalize.py                  # Database migration
└── test_edge_cases_stress.py             # Testing suite
```

---

### Common Commands

```bash
# Run backend locally
cd backend && source venv/bin/activate && python main.py

# Run frontend locally  
cd frontend && npm run dev

# Run tests
python3 test_edge_cases_stress.py

# Database backfill
python3 LOCAL_BACKFILL_SCRIPT.py --environment production

# Check backend health
curl https://closetgptrenew-backend-production.up.railway.app/health

# Test semantic filtering
curl -X POST "https://closetgptrenew-backend-production.up.railway.app/api/outfits/debug-filter?semantic=true" \
  -H "Content-Type: application/json" \
  -d '{"style": "classic", "occasion": "business", "mood": "professional"}'
```

---

## Appendix B: Semantic Compatibility Examples

### Style Compatibility Chart

| Request Style | Matches (Semantic) |
|--------------|-------------------|
| Classic | Business Casual, Smart Casual, Preppy, Traditional, Minimalist |
| Business Casual | Classic, Smart Casual, Casual, Preppy, Professional |
| Athletic | Sporty, Activewear, Casual, Streetwear |
| Romantic | Feminine, Vintage, Bohemian, Soft, Delicate |
| Minimalist | Classic, Modern, Balanced, Clean, Simple |

### Mood Compatibility Chart

| Request Mood | Matches (Semantic) |
|-------------|-------------------|
| Professional | Polished, Sophisticated, Elegant, Refined |
| Relaxed | Calm, Laidback, Casual, Neutral |
| Bold | Confident, Statement, Vibrant, Expressive |
| Romantic | Soft, Elegant, Feminine, Delicate |

---

**Document Version**: 1.0  
**Last Updated**: October 7, 2025  
**Maintained By**: Development Team  
**Status**: ✅ Complete and Current

