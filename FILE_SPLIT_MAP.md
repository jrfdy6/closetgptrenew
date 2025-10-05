# File Split Map: outfits.py → Modular Architecture

## 📊 **Current File Analysis**
- **File**: `backend/src/routes/outfits.py`
- **Total Lines**: 6,941 lines
- **Functions**: 25+ functions
- **Classes**: 3 main classes
- **Router Endpoints**: 3+ endpoints

---

## 🎯 **Proposed File Split Map**

### **1. Models & Schemas** → `models.py`
**Lines**: 332-395 (63 lines)
**Responsibilities**:
- Pydantic model definitions
- Request/response schemas
- Data validation

**Functions/Classes**:
- `OutfitRequest` (line 332)
- `CreateOutfitRequest` (line 357) 
- `OutfitResponse` (line 366)

**Imports Needed**:
```python
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
```

---

### **2. Utility Functions** → `utils.py`
**Lines**: 122-227 (105 lines)
**Responsibilities**:
- Helper functions
- Data transformation
- Logging utilities

**Functions**:
- `safe_get_metadata()` (line 122)
- `log_generation_strategy()` (line 129)
- `normalize_ts()` (line 195)
- `clean_for_firestore()` (line 227)

**Imports Needed**:
```python
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
```

---

### **3. Validation Logic** → `validation.py`
**Lines**: 21-122 (101 lines) + 1523-1738 (215 lines)
**Responsibilities**:
- Outfit completeness validation
- Semantic appropriateness checks
- Style-gender compatibility

**Functions**:
- `validate_outfit_completeness()` (line 21)
- `_is_semantically_appropriate()` (line 38)
- `validate_style_gender_compatibility()` (line 1477)
- `validate_outfit_composition()` (line 1523)
- `validate_layering_rules()` (line 1666)
- `validate_color_material_harmony()` (line 1738)

**Imports Needed**:
```python
from typing import List, Dict, Any, Optional
from .models import OutfitRequest
```

---

### **4. Style & Filtering Logic** → `styling.py`
**Lines**: 395-670 (275 lines)
**Responsibilities**:
- Style-based filtering
- Hard exclusions
- Style appropriateness scoring

**Functions**:
- `filter_items_by_style()` (line 395)
- `get_hard_style_exclusions()` (line 479)
- `calculate_style_appropriateness_score()` (line 611)
- `ensure_base_item_included()` (line 670)

**Imports Needed**:
```python
from typing import List, Dict, Any, Optional
import logging
```

---

### **5. Weather Integration** → `weather.py`
**Lines**: 736-786 (50 lines)
**Responsibilities**:
- Weather appropriateness checks
- Weather context attachment

**Functions**:
- `check_item_weather_appropriateness()` (line 736)
- `attach_weather_context_to_items()` (line 786)

**Imports Needed**:
```python
from typing import List, Dict, Any
import logging
```

---

### **6. Core Generation Logic** → `generation.py`
**Lines**: 917-1477 (560 lines)
**Responsibilities**:
- Main outfit generation orchestration
- Service coordination
- Error handling

**Functions**:
- `generate_outfit_logic()` (line 917) - **MAIN FUNCTION**

**Imports Needed**:
```python
from typing import Dict, Any
from .models import OutfitRequest
from ..services.robust_outfit_generation_service import RobustOutfitGenerationService
from ..auth.auth_service import get_current_user
from ..config.firebase import db
```

---

### **7. Rule-Based Generation** → `rule_engine.py`
**Lines**: 2714-3750 (1036 lines)
**Responsibilities**:
- Rule-based outfit generation
- Fallback strategies
- Debug utilities

**Functions**:
- `debug_rule_engine()` (line 2714)
- `generate_rule_based_outfit()` (line 2734)
- `generate_fallback_outfit()` (line 3456)
- `generate_weather_aware_fallback_reasoning()` (line 3750)

**Imports Needed**:
```python
from typing import List, Dict, Any
from .models import OutfitRequest
import logging
```

---

### **8. Router Endpoints** → `routes.py`
**Lines**: 4274-6941 (2667 lines)
**Responsibilities**:
- FastAPI route handlers
- Request/response handling
- Authentication

**Functions**:
- `@router.get("/health")` (line 4274)
- `@router.get("/debug")` (line 4287)
- `@router.get("/debug/base-item-fix")` (line 4300)
- Main generation endpoint

**Imports Needed**:
```python
from fastapi import APIRouter, HTTPException, Depends
from .models import OutfitRequest, OutfitResponse
from .generation import generate_outfit_logic
from ..auth.auth_service import get_current_user_id
```

---

## 📋 **Import Dependency Map**

### **Core Dependencies**:
```
models.py ← (no dependencies)
utils.py ← models.py
validation.py ← models.py
styling.py ← models.py
weather.py ← models.py
generation.py ← models.py, utils.py, validation.py, styling.py, weather.py
rule_engine.py ← models.py, utils.py, validation.py, styling.py, weather.py
routes.py ← models.py, generation.py, rule_engine.py
```

### **External Dependencies**:
- `fastapi` → routes.py
- `pydantic` → models.py
- `logging` → all files
- `firebase` → generation.py
- `auth_service` → routes.py, generation.py

---

## 🎯 **Extraction Priority**

### **Phase 1: Foundation** (Low Risk)
1. ✅ **models.py** - Already completed
2. ✅ **utils.py** - Already completed  
3. ✅ **validation.py** - Already completed
4. ✅ **styling.py** - Already completed
5. ✅ **weather.py** - Already completed

### **Phase 2: Core Logic** (Medium Risk)
6. **generation.py** - Extract `generate_outfit_logic()` (560 lines)
7. **rule_engine.py** - Extract rule-based functions (1036 lines)

### **Phase 3: Router** (High Risk)
8. **routes.py** - Extract router endpoints (2667 lines)

---

## ⚠️ **Critical Considerations**

### **Large Functions to Extract**:
- `generate_outfit_logic()` - 560 lines (lines 917-1477)
- Rule-based generation functions - 1036 lines (lines 2714-3750)
- Router endpoints - 2667 lines (lines 4274-6941)

### **Import Dependencies**:
- All files need access to `models.py`
- `generation.py` needs access to all validation/styling/weather modules
- `routes.py` needs access to generation modules

### **Error Handling**:
- Preserve all try/catch blocks
- Maintain debug logging
- Keep error propagation logic

---

## 🚀 **Next Steps**

1. **Extract remaining large functions** from original file
2. **Update import statements** to use new modular structure
3. **Test each module** independently
4. **Remove original large file**
5. **Deploy and verify** functionality

This map provides a clear roadmap for completing the modular refactoring while preserving all original functionality and behavior.
