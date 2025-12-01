# Outfit Generation Debug Playbook

Follow these steps whenever you want to diagnose how the robust pipeline behaves for a specific occasion/style/mood combination.

---

## 1. Generate the Outfit in the App
1. Open the standard outfit generator (production site).
2. Set the **occasion**, **style**, and **mood** you want to analyze.
3. Click **Generate Outfit** (ensure robust mode is active).  
   - Copy the outfit ID from the network response or success toast; you’ll need it later.

---

## 2. Run the Debug Filter Endpoint
1. Visit `/personalization-demo`.
2. Choose the same occasion/style/mood.
3. Click **Run Debug Filtering** (not “Generate Outfit”).  
   - This hits `/api/outfits/debug-filter` and prints a table/log showing which items passed or failed `_filter_suitable_items_with_debug`.
   - Look for:
     - `heuristics` (e.g. `name_lounge_keyword`)
     - `reasons` for rejections
     - Whether the emergency fallback was triggered

---

## 3. Pull the Firestore Outfit Document
Use the Firebase Admin SDK to inspect the saved outfit’s metadata.

```bash
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew
backend/venv/bin/python - <<'PY'
import os, json
from firebase_admin import credentials, firestore, initialize_app

root = os.getcwd()
cred_path = os.path.join(root, "backend", "service-account-key.json")
if not os.path.exists(cred_path):
    raise SystemExit("service-account-key.json missing")

initialize_app(credentials.Certificate(cred_path))
db = firestore.client()

OUTFIT_ID = "outfit_XXXXXXXXXXXX"  # ← replace with real ID
doc = db.collection("outfits").document(OUTFIT_ID).get()
if not doc.exists:
    raise SystemExit(f"Outfit {OUTFIT_ID} not found")

data = doc.to_dict()
print(json.dumps({
    "id": OUTFIT_ID,
    "name": data.get("name"),
    "style": data.get("style"),
    "occasion": data.get("occasion"),
    "metadata": data.get("metadata")
}, indent=2, default=str))
PY
```

Check the output for:
- `metadata.metadata_notes.lounge_heuristics` (or equivalent heuristics)
- `compatibility_skip_reason`
- `top_candidates`, `unique_items_count`, and any warnings

---

## 4. Inspect Logs (Optional)
In Railway, filter the backend logs by user ID or outfit ID. Confirm that:
- Metadata compatibility ran (no “skipping” log).
- The strategy selector and cohesive composition phases occurred.
- No emergency fallback messages appear.

---

## 5. Synthetic CLI Test (Optional)
For quick verification before looping through the UI, feed a synthetic wardrobe into the filter:

```bash
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew
backend/venv/bin/python - <<'PY'
import os, sys, asyncio
root = os.getcwd()
sys.path.insert(0, os.path.join(root, "backend"))
sys.path.insert(0, os.path.join(root, "backend", "src"))

from src.services.robust_outfit_generation_service import RobustOutfitGenerationService, GenerationContext
from src.custom_types.wardrobe import ClothingItem

service = RobustOutfitGenerationService()

def make_item(item_id, name, type_, metadata):
    return ClothingItem(
        id=item_id,
        name=name,
        type=type_,
        color="gray",
        season=["all"],
        style=[],
        occasion=[],
        metadata=metadata
    )

wardrobe = [
    make_item("item1", "Soft Knit Joggers", "pants", {"visualAttributes": {"waistbandType": "elastic", "formalLevel": "casual", "coreCategory": "bottom"}}),
    make_item("item2", "Cozy Fleece Hoodie", "sweater", {"visualAttributes": {"formalLevel": "relaxed", "coreCategory": "top"}}),
    make_item("item3", "Slip-On Slippers", "shoes", {"visualAttributes": {"formalLevel": "casual", "coreCategory": "shoes"}}),
]

context = GenerationContext(
    user_id="debug_user",
    occasion="Loungewear",
    style="Loungewear",
    mood="Subtle",
    weather={"temperature": 60},
    wardrobe=wardrobe,
    user_profile={"gender": "male"}
)

async def run_test():
    result = await service._filter_suitable_items_with_debug(context, semantic_filtering=False)
    print("Valid items:", len(result["valid_items"]))
    print("Heuristics:", context.metadata_notes.get("lounge_heuristics"))
    for entry in result["debug_analysis"]:
        status = "PASSED" if entry.get("valid") else "FAILED"
        print(status, entry["name"], entry.get("heuristics"), entry.get("reasons"))

asyncio.run(run_test())
PY
```

This confirms the heuristics fire and the emergency fallback is avoided.

---

## 6. Document Findings
- Record which heuristics fired and which items still failed (for future wardrobe tagging or scoring tweaks).
- If the outfit is still off, adjust wardrobe metadata or strategy rules accordingly and repeat.

---

### Shortcut Command
Once you have the outfit ID, you can re-run the Firestore/CLI inspection by copy‑pasting the code block above, changing only `OUTFIT_ID`.








