# 🎯 METADATA-FIRST FILTERING RULES

## Priority Order (STRICT - Top to Bottom)

```
┌─────────────────────────────────────────┐
│ 1. metadata.visualAttributes (PRIMARY) │ ← Check FIRST
├─────────────────────────────────────────┤
│ 2. item.occasion tags (SECONDARY)      │ ← Check SECOND
├─────────────────────────────────────────┤
│ 3. item.type (TERTIARY)                │ ← Check THIRD
├─────────────────────────────────────────┤
│ 4. item.name (FALLBACK ONLY)           │ ← Check LAST (if all above missing)
└─────────────────────────────────────────┘
```

## Core Principles

### ✅ DO:
1. **Check metadata FIRST** - If `metadata.visualAttributes` exists, use it exclusively
2. **Trust metadata over name** - If metadata says "athletic" but name says "dress", trust metadata
3. **Use occasion tags second** - `item.occasion = ['gym', 'athletic']` overrides item type
4. **Only use name as absolute fallback** - When ALL metadata fields are empty/null

### ❌ DON'T:
1. Don't check item name if metadata exists
2. Don't mix name-based and metadata-based checks
3. Don't use name keywords like "jogger" or "dress" if metadata has `waistbandType`
4. Don't trust item names over structured metadata

---

## Validation Checklist

### For PANTS (Gym):

```python
# ✅ CORRECT ORDER:
1. Check metadata.visualAttributes.waistbandType
   - elastic/drawstring → ALLOW
   - button_zip/belt_loops → BLOCK
   
2. Check metadata.visualAttributes.material
   - polyester/nylon/spandex → ALLOW
   - wool/denim/cotton twill → BLOCK

3. Check item.occasion tags
   - 'athletic'/'gym'/'workout' → ALLOW
   - 'formal'/'business' → BLOCK

4. Check item.type
   - 'pants' with no metadata → Check name (fallback)

5. Check item.name (ONLY if steps 1-4 empty)
   - 'jogger'/'sweatpants' → ALLOW
   - 'jeans'/'chinos' → BLOCK
```

### For SHIRTS (Gym):

```python
# ✅ CORRECT ORDER:
1. Check metadata.visualAttributes.neckline
   - 'crew'/'v-neck'/'round' → ALLOW
   - 'collar'/'polo collar' → BLOCK

2. Check metadata.visualAttributes.sleeveLength
   - 'short'/'sleeveless'/'tank' → ALLOW
   - 'long' + formalLevel='business' → BLOCK

3. Check item.occasion tags
   - 'athletic'/'gym'/'sport' → ALLOW
   - 'formal'/'business' → BLOCK

4. Check item.type
   - 'shirt'/'top' → Check name (fallback)

5. Check item.name (ONLY if steps 1-4 empty)
   - 't-shirt'/'tank'/'jersey' → ALLOW
   - 'polo'/'button-up'/'henley' → BLOCK
```

### For SHOES (Gym):

```python
# ✅ CORRECT ORDER:
1. Check metadata.visualAttributes.shoeType
   - 'sneaker'/'athletic'/'running' → ALLOW
   - 'oxford'/'loafer'/'dress' → BLOCK

2. Check metadata.visualAttributes.material
   - 'mesh'/'synthetic' → ALLOW
   - 'leather' (without athletic shoeType) → BLOCK

3. Check item.occasion tags
   - 'athletic'/'gym'/'sport'/'running' → ALLOW
   - 'formal'/'business' → BLOCK

4. Check item.type
   - 'shoes' → Check name (fallback)

5. Check item.name (ONLY if steps 1-4 empty)
   - 'sneaker'/'running shoes' → ALLOW
   - 'oxford'/'loafers' → BLOCK
```

---

## Implementation Example (Gym Pants Filter)

### ❌ WRONG (Name-First):
```python
if 'jogger' in item.name or 'sweatpants' in item.name:
    allow = True
elif 'jeans' in item.name or 'chinos' in item.name:
    allow = False
```

### ✅ CORRECT (Metadata-First):
```python
allow = False

# Step 1: Check waistband type (MOST RELIABLE)
waistband = item.metadata.get('visualAttributes', {}).get('waistbandType')
if waistband:
    if waistband in ['elastic', 'drawstring']:
        allow = True  # DONE - don't check name
        return allow
    elif waistband in ['button_zip', 'belt_loops']:
        allow = False  # DONE - don't check name
        return allow

# Step 2: Check material
material = item.metadata.get('visualAttributes', {}).get('material')
if material:
    if material in ['polyester', 'nylon', 'spandex']:
        allow = True
        return allow
    elif material in ['denim', 'wool', 'cotton twill']:
        allow = False
        return allow

# Step 3: Check occasion tags
if 'athletic' in item.occasion or 'gym' in item.occasion:
    allow = True
    return allow
if 'formal' in item.occasion or 'business' in item.occasion:
    allow = False
    return allow

# Step 4: Check type
if item.type == 'shorts':
    allow = True  # Shorts are usually OK
    return allow

# Step 5: ONLY NOW check name (fallback)
if 'jogger' in item.name or 'sweatpants' in item.name:
    allow = True
elif 'jeans' in item.name or 'chinos' in item.name:
    allow = False

return allow
```

---

## Debugging Checklist

When an inappropriate item passes the filter:

1. ✅ **Does the item have metadata?**
   - Log: `logger.info(f"Metadata exists: {item.metadata is not None}")`
   
2. ✅ **What are the metadata values?**
   - Log: `logger.info(f"waistband={waistband}, material={material}, formalLevel={formal_level}")`
   
3. ✅ **Was metadata checked BEFORE name?**
   - Add early return statements after metadata checks
   
4. ✅ **Are you mixing name and metadata checks?**
   - Never do: `if 'jogger' in name OR waistband=='elastic'`
   - Always prioritize metadata exclusively

5. ✅ **Is the logic short-circuiting correctly?**
   - Use `return` immediately after metadata decision
   - Don't let code continue to name-based checks

---

## Expected Behavior

### Cargo Pants Example:
- **Name:** "pants cargo khaki"
- **Metadata:** `waistbandType='button_zip'`, `material='cotton twill'`
- **Result:** ❌ BLOCKED at Step 1 (button_zip waistband)
- **Never reaches:** Name check ("cargo")

### Athletic Shorts Example:
- **Name:** "shorts athletic blue by rams"
- **Metadata:** `waistbandType='elastic'`, `material='polyester'`
- **Result:** ✅ ALLOWED at Step 1 (elastic waistband)
- **Never reaches:** Name check ("athletic")

### Jeans Example:
- **Name:** "pants jeans light blue by levis"
- **Metadata:** `material='denim'`, `waistbandType='button_zip'`
- **Result:** ❌ BLOCKED at Step 1 (button_zip) or Step 2 (denim)
- **Never reaches:** Name check ("jeans")

---

## Summary

**The Golden Rule:** 
> If metadata exists, USE ONLY metadata. The item name becomes irrelevant.

**The Test:**
> Can I delete the item's name and still make the correct decision using only metadata?
> - If YES → Your code is metadata-first ✅
> - If NO → You're relying on name checking ❌

