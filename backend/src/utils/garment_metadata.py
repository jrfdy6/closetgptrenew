"""Preserve saved analysis while presenting corrected garment facts to ranking.

Uploads retain the analysis under ``analysis.metadata``; editing a garment writes
root fields. Root metadata can independently contain photo/file information.
Merge those sources without requiring analysis to be repeated or trusting an
outfit request's copy of the wardrobe.
"""
from collections.abc import Mapping
from copy import deepcopy


VISUAL_FIELDS = (
    'material', 'pattern', 'textureStyle', 'fabricWeight', 'fit', 'silhouette',
    'length', 'genderTarget', 'sleeveLength', 'neckline', 'hangerPresent',
    'backgroundRemoved', 'wearLayer', 'formalLevel', 'waistbandType',
    'layerLevel', 'warmthFactor', 'temperatureCompatibility', 'coreCategory', 'canLayer', 'maxLayers',
    'transparency', 'collarType', 'embellishments', 'printSpecificity', 'rise',
    'legOpening', 'heelHeight', 'statementLevel',
)


def _record(value):
    return dict(value) if isinstance(value, Mapping) else {}


def _populated(value):
    # Empty upload/editor defaults carry no fact. Explicit "unknown", False and
    # zero ARE facts and must not silently resurrect an older AI inference.
    return value is not None and value != '' and value != [] and value != {}


def _merge(base, override):
    result = deepcopy(_record(base))
    for key, value in _record(override).items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _visual(metadata):
    return _merge(metadata.get('visual_attributes'), metadata.get('visualAttributes'))


def normalize_garment_metadata(item):
    """Return a detached record; saved root corrections outrank AI analysis.

    Unknown attribute keys and raw analysis are retained. No inferred material,
    pattern, fit, or description is fabricated for an unanalysed garment.
    """
    result = deepcopy(dict(item))
    analysis = _record(item.get('analysis'))
    nested = _record(analysis.get('metadata'))
    root = _record(item.get('metadata'))
    metadata = _merge(nested, root)
    visual = _visual(nested)
    for key, value in _visual(root).items():
        if _populated(value):
            visual[key] = deepcopy(value)
    for key in VISUAL_FIELDS:
        if _populated(item.get(key)):
            visual[key] = deepcopy(item[key])
    if isinstance(visual.get('material'), list):
        visual['material'] = ', '.join(str(value) for value in visual['material'])
    if visual:
        metadata['visualAttributes'] = visual
    for source, target in (('style', 'styleTags'), ('occasion', 'occasionTags'),
                           ('brand', 'brand'), ('description', 'naturalDescription')):
        if _populated(item.get(source)):
            metadata[target] = deepcopy(item[source])
    if metadata or 'metadata' in item:
        result['metadata'] = metadata
    if isinstance(result.get('material'), list):
        result['material'] = ', '.join(str(value) for value in result['material']) or None
    return result
