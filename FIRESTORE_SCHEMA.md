# Firestore Schema Documentation & Versioning

## Schema Versioning
- **Current Schema Version:** 1.0.0
- Each document includes a `schema_version` field (string, e.g., "1.0.0").
- Version history is tracked in this file and optionally in a Firestore `schema_versions` collection.

---

## 1. wardrobe (Collection)
- **Purpose:** Stores user wardrobe items with rich metadata and embeddings.
- **Document ID:** Unique item ID (string)
- **Fields:**
  - `user_id` (string, required)
  - `name` (string, required)
  - `type` (string, required, e.g., "shirt", "pants")
  - `image_url` (string, optional)
  - `created_at` (timestamp/int/string, required)
  - `metadata` (map/object, required):
    - `brand` (string, optional)
    - `fit` (string, e.g., "slim", "regular", "loose")
    - `silhouette` (string, e.g., "A-line", "straight")
    - `style` (array of string, e.g., ["minimalist", "classic"])
    - `color_harmony` (string, e.g., "analogous", "complementary")
    - `pattern` (string, e.g., "solid", "striped")
    - `material` (string, e.g., "cotton", "wool")
    - `visualAttributes` (object):
      - `color` (string or array)
      - `dominant_color` (string)
      - `secondary_color` (string)
      - `accent_color` (string)
      - `length` (string, e.g., "short", "long")
      - `sleeveLength` (string, e.g., "short", "long")
      - `fit` (string)
      - `pattern` (string)
      - `silhouette` (string)
  - `clip_embedding` (array of float, required, normalized)
  - `embedding_version` (string, e.g., "clip_v1")
  - `schema_version` (string, e.g., "1.0.0")

---

## 2. outfits (Collection)
- **Purpose:** Stores generated outfits and their composition.
- **Document ID:** Unique outfit ID (string)
- **Fields:**
  - `user_id` (string, required)
  - `occasion` (string, required)
  - `mood` (string, required)
  - `style` (string, required)
  - `items` (array of map/object, required):
    - `id` (string, required)
    - `name` (string, required)
    - `type` (string, required)
    - `image_url` (string, optional)
    - `metadata` (object, optional)
  - `description` (string, optional)
  - `created_at` (timestamp/int/string, required)
  - `feedback_summary` (array of map/object):
    - `feedback_type` (string)
    - `timestamp` (string/timestamp)
    - `user_id` (string)
  - `generation_method` (string, e.g., "refined_pipeline", optional)
  - `schema_version` (string, e.g., "1.0.0")

---

## 3. outfit_feedback (Collection)
- **Purpose:** Stores user feedback on outfits.
- **Document ID:** Unique feedback ID (string)
- **Fields:**
  - `user_id` (string, required)
  - `outfit_id` (string, required)
  - `feedback_type` (string, "like" | "dislike" | "issue")
  - `issue_category` (string, optional)
  - `issue_description` (string, optional)
  - `rating` (int, 1-5, optional)
  - `context_data` (object, optional):
    - `user_agent` (string)
    - `platform` (string)
    - `location` (string)
    - `session_data` (object)
  - `outfit_context` (object):
    - `occasion` (string)
    - `mood` (string)
    - `style` (string)
    - `items_count` (int)
    - `items_types` (array of string)
    - `created_at` (timestamp/int/string)
    - `generation_method` (string)
  - `user_context` (object):
    - `user_id` (string)
    - `user_email` (string)
    - `user_preferences` (object)
    - `feedback_timestamp` (string/timestamp)
    - `session_data` (object)
  - `analytics_data` (object):
    - `feedback_timestamp` (string/timestamp)
    - `feedback_category` (string)
    - `data_source` (string)
    - `metadata` (object)
  - `schema_version` (string, e.g., "1.0.0")

---

## 4. analytics_events (Collection)
- **Purpose:** Stores analytics events for data lake and ML.
- **Document ID:** Unique event ID (string)
- **Fields:**
  - `event_type` (string, e.g., "outfit_feedback")
  - `event_data` (object, see above)
  - `timestamp` (string/timestamp)
  - `user_id` (string)
  - `outfit_id` (string)
  - `feedback_type` (string)
  - `rating` (int, optional)
  - `issue_category` (string, optional)
  - `metadata` (object):
    - `source` (string)
    - `version` (string)
    - `processed` (bool)
  - `schema_version` (string, e.g., "1.0.0")

---

## Version History
- **1.0.0** — Initial production schema with versioning, robust metadata, and normalized embeddings.

---

## Notes
- All timestamps can be stored as Firestore `Timestamp`, Unix epoch, or ISO string (be consistent per environment).
- All arrays and objects/maps should be non-null and default to empty if missing.
- All new/updated documents should include `schema_version`.
- For any schema changes, increment the version and update this file. 