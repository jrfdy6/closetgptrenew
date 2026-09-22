"""Small, provider-free admission rules for generated (not manually saved) looks."""
from collections.abc import Mapping
import re


class InvalidGeneratedOutfit(ValueError):
    pass


CATEGORY_ALIASES = {
    'one-piece': {'cocktail dress', 'dresses', 'overalls', 'dress', 'shirtdress', 'shirt dress', 'romper', 'maxi dress', 'sundress', 'mini dress', 'onepiece', 'jumpsuit', 'one piece', 'jumpsuits', 'rompers'},
    'layer': {'vest', 'coat', 'layer', 'jackets', 'blazer', 'cardigan', 'coats', 'outerwear', 'cardigans', 'blazers', 'jacket', 'vests'},
    'shoes': {'sandals', 'shoe', 'boots', 'dress shoes', 'flat', 'oxford', 'loafers', 'oxfords', 'footwear', 'flats', 'boot', 'heels', 'loafer', 'sandal', 'sneaker', 'heel', 'shoes', 'sneakers'},
    'bottom': {'dress pants', 'mini skirt', 'midi skirt', 'pants', 'slacks', 'maxi skirt', 'jeans', 'bottom', 'leggings', 'shorts', 'chinos', 'skirt', 'trousers', 'joggers', 'sweatpants', 'skirts', 'bottoms', 'pencil skirt'},
    'top': {'blouse', 'shirts', 'tshirts', 'shirt', 'crop top', 'tank top', 'top', 't shirt', 'polo', 'hoodie', 'tank', 'sweatshirt', 'tee', 'knitwear', 'sweater', 'hoodies', 'blouses', 't shirts', 'sweatshirts', 'sweaters', 'dress shirt', 'tshirt', 'tops'},
    'accessory': {'scarves', 'jewelry', 'bags', 'belts', 'sunglasses', 'bag', 'tie', 'accessory', 'belt', 'scarf', 'hat', 'watch', 'accessories', 'hats'},
}


def classify_garment(item):
    analysis = item.get('analysis') or {}
    if not isinstance(analysis, Mapping):
        analysis = {}
    for value in (item.get('type'), item.get('category'), analysis.get('type'), analysis.get('category')):
        token = re.sub(r'[-_\s]+', ' ', str(value or '').lower().removeprefix('clothingtype.')).strip()
        for category, aliases in CATEGORY_ALIASES.items():
            if token in aliases:
                return category
    return 'unknown'


def has_complete_combination(items):
    categories = {classify_garment(item) for item in items}
    return 'shoes' in categories and ('one-piece' in categories or {'top', 'bottom'} <= categories)


def owns_garment(item, user_id):
    owners = [item.get(key) for key in ('userId', 'user_id') if item.get(key) is not None]
    return bool(owners) and all(owner == user_id for owner in owners)


def usable_garment(item):
    if item.get('deleted') is True or item.get('isDeleted') is True or item.get('deletedAt'):
        return False
    return any(isinstance(item.get(key), str) and item[key].strip()
               for key in ('imageUrl', 'image_url', 'originalImageUrl'))


def load_owned_wardrobe(db, supplied_items, user_id):
    """Trust request IDs, never request-supplied ownership, categories or images."""
    ids = list(dict.fromkeys(str(item.get('id') or '').strip() for item in supplied_items or []))
    if not ids or any(not item_id or '/' in item_id for item_id in ids):
        raise InvalidGeneratedOutfit('Add saved wardrobe items before generating an outfit.')
    references = [db.collection('wardrobe').document(item_id) for item_id in ids]
    snapshots = {snapshot.id: snapshot for snapshot in db.get_all(references)}
    items = []
    for item_id in ids:
        snapshot = snapshots.get(item_id)
        stored = snapshot.to_dict() if snapshot and snapshot.exists else None
        if not stored or not owns_garment(stored, user_id):
            raise InvalidGeneratedOutfit('Some selected garments are no longer available in your wardrobe. Refresh and try again.')
        # The request is a candidate pool. Old incomplete records must not block
        # a complete combination from the remaining saved garments.
        if usable_garment(stored) and classify_garment(stored) != 'unknown':
            items.append({**stored, 'id': item_id})
    if not has_complete_combination(items):
        raise InvalidGeneratedOutfit('Add a top, bottom and shoes, or a one-piece and shoes, to generate a complete outfit.')
    return items


def validate_generated_items(items, wardrobe, required_item_id=None):
    """Return authoritative items, rejecting unknown IDs, duplicates and missing essentials."""
    owned_by_id = {str(item['id']): item for item in wardrobe}
    ids = [str(item.get('id') or '').strip() for item in items or []]
    if not ids or len(set(ids)) != len(ids) or any(item_id not in owned_by_id for item_id in ids):
        raise InvalidGeneratedOutfit('We could not create a complete outfit from your saved garments. Try another configuration.')
    if required_item_id and required_item_id not in ids:
        raise InvalidGeneratedOutfit('The outfit is missing your required garment. Try again.')
    authoritative_items = [dict(owned_by_id[item_id]) for item_id in ids]
    if not has_complete_combination(authoritative_items):
        raise InvalidGeneratedOutfit('We could not match a complete outfit for these settings. Try another configuration or add the missing essentials.')
    return authoritative_items


def normalize_stored_garment(item, allowed_types):
    """Adapt legacy persisted shapes to ClothingItem without trusting client fields."""
    from datetime import datetime, timezone

    from src.utils.garment_metadata import normalize_garment_metadata

    normalized = normalize_garment_metadata(item)
    raw_type = str(item.get('type') or '').lower().removeprefix('clothingtype.')
    canonical_type = re.sub(r'[-\s]+', '_', raw_type).strip('_')
    category_defaults = {'top': 'shirt', 'bottom': 'pants', 'one-piece': 'dress',
                         'shoes': 'shoes', 'layer': 'jacket', 'accessory': 'accessory', 'unknown': 'other'}
    normalized['type'] = raw_type if raw_type in allowed_types else canonical_type if canonical_type in allowed_types else category_defaults[classify_garment(item)]
    normalized['name'] = str(item.get('name') or 'Saved garment')
    normalized['color'] = str(item.get('color') or 'unknown')
    normalized['imageUrl'] = next((item[key] for key in ('imageUrl', 'image_url', 'originalImageUrl') if item.get(key)), '')
    normalized['userId'] = item.get('userId') or item.get('user_id')
    for key in ('season', 'style', 'occasion', 'tags'):
        value = item.get(key)
        values = [value] if isinstance(value, str) else value if isinstance(value, list) else []
        normalized[key] = [entry.strip() for entry in values if isinstance(entry, str) and entry.strip()]
    if not normalized['season']:
        normalized['season'] = ['all']
    if isinstance(item.get('material'), list):
        normalized['material'] = ', '.join(str(entry) for entry in item['material']) or None
    for key in ('createdAt', 'updatedAt', 'lastWorn'):
        value = item.get(key)
        if isinstance(value, str):
            try:
                normalized[key] = int(value)
            except ValueError:
                try:
                    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    normalized[key] = int(parsed.timestamp() * 1000)
                except ValueError:
                    normalized[key] = None
        elif hasattr(value, 'timestamp'):
            normalized[key] = int(value.timestamp() * 1000)
    return normalized
