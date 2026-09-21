"""Build narrow Firestore updates for user-editable wardrobe fields.

Use field paths for nested metadata so an edit cannot replace an entire metadata
map or overwrite unrelated changes made by an image worker.
"""

import math
from typing import Any, Dict

STRING_FIELDS = frozenset({'name', 'type', 'color', 'brand', 'size'})
LIST_FIELDS = frozenset({'style', 'season', 'occasion'})
VISUAL_STRING_FIELDS = frozenset({
    'material', 'sleeveLength', 'fit', 'neckline', 'length', 'transparency',
    'collarType', 'embellishments', 'printSpecificity', 'rise', 'legOpening',
    'heelHeight',
})
EDITABLE_FIELDS = STRING_FIELDS | LIST_FIELDS | {'purchasePrice', 'favorite', 'metadata'}


def _require_string(field: str, value: Any) -> None:
    if not isinstance(value, str):
        raise ValueError(f'{field} must be text')


def _require_number(field: str, value: Any, maximum=None) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0
            or (maximum is not None and value > maximum)):
        raise ValueError(f'{field} must be a valid non-negative number'
                         + (f' no greater than {maximum}' if maximum is not None else ''))


def build_wardrobe_update(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate editable values and return only their explicitly requested leaves.

    Omitted fields are untouched. Empty strings/lists intentionally clear an
    editable leaf. Empty metadata maps are no-ops, never whole-map replacement.
    Identity, owner, processing, wear history, and timestamp fields are not editable
    through this route; their existing dedicated operations remain authoritative.
    """
    unsupported = set(item_data) - EDITABLE_FIELDS
    if unsupported:
        raise ValueError('Unsupported wardrobe update fields: ' + ', '.join(sorted(unsupported)))

    updates = {}
    for field, value in item_data.items():
        if field in STRING_FIELDS:
            _require_string(field, value)
            updates[field] = value
        elif field in LIST_FIELDS:
            if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
                raise ValueError(f'{field} must be a list of text values')
            updates[field] = value
        elif field == 'favorite':
            if not isinstance(value, bool):
                raise ValueError('favorite must be a boolean')
            updates[field] = value
        elif field == 'purchasePrice':
            _require_number(field, value)
            updates[field] = value
        elif field == 'metadata':
            if not isinstance(value, dict):
                raise ValueError('metadata must be an object')
            if set(value) - {'naturalDescription', 'visualAttributes'}:
                raise ValueError('Unsupported metadata update fields')
            if 'naturalDescription' in value:
                _require_string('naturalDescription', value['naturalDescription'])
                updates['metadata.naturalDescription'] = value['naturalDescription']
            if 'visualAttributes' in value:
                attributes = value['visualAttributes']
                if not isinstance(attributes, dict):
                    raise ValueError('visualAttributes must be an object')
                if set(attributes) - VISUAL_STRING_FIELDS - {'statementLevel'}:
                    raise ValueError('Unsupported visual attribute update fields')
                for attribute, attribute_value in attributes.items():
                    if attribute == 'statementLevel':
                        _require_number(attribute, attribute_value, maximum=10)
                    else:
                        _require_string(attribute, attribute_value)
                    updates[f'metadata.visualAttributes.{attribute}'] = attribute_value
    return updates
