// The server repeats this merge on owned saved records; request metadata is not
// an authority for ownership or edits. Keep this projection aligned with
// backend/src/utils/garment_metadata.py.
export const garmentVisualFields = [
  'material', 'pattern', 'textureStyle', 'fabricWeight', 'fit', 'silhouette',
  'length', 'genderTarget', 'sleeveLength', 'neckline', 'hangerPresent',
  'backgroundRemoved', 'wearLayer', 'formalLevel', 'waistbandType',
  'layerLevel', 'warmthFactor', 'temperatureCompatibility', 'coreCategory', 'canLayer', 'maxLayers',
  'transparency', 'collarType', 'embellishments', 'printSpecificity', 'rise',
  'legOpening', 'heelHeight', 'statementLevel',
] as const;

type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue =>
  value !== null && typeof value === 'object' && !Array.isArray(value) ? value as RecordValue : {};
const populated = (value: unknown): boolean => value !== null && value !== undefined && value !== '' &&
  !(Array.isArray(value) && value.length === 0) &&
  !(value !== null && typeof value === 'object' && Object.keys(value).length === 0);

function merge(base: unknown, override: unknown): RecordValue {
  const result = { ...record(base) };
  for (const [key, value] of Object.entries(record(override))) {
    result[key] = Object.keys(record(value)).length > 0 && Object.keys(record(result[key])).length > 0
      ? merge(result[key], value) : value;
  }
  return result;
}

const visual = (metadata: RecordValue) => merge(metadata.visual_attributes, metadata.visualAttributes);

/** Root corrections outrank analysis; empty upload defaults do not invent facts. */
export function generationGarmentMetadata(item: RecordValue): RecordValue {
  const nested = record(record(item.analysis).metadata);
  const root = record(item.metadata);
  const metadata = merge(nested, root);
  const attributes = visual(nested);
  for (const [key, value] of Object.entries(visual(root))) {
    if (populated(value)) attributes[key] = value;
  }
  for (const key of garmentVisualFields) {
    if (populated(item[key])) attributes[key] = item[key];
  }
  if (Array.isArray(attributes.material)) attributes.material = attributes.material.join(', ');
  if (Object.keys(attributes).length) metadata.visualAttributes = attributes;
  for (const [source, target] of [['style', 'styleTags'], ['occasion', 'occasionTags'],
    ['brand', 'brand'], ['description', 'naturalDescription']]) {
    if (populated(item[source])) metadata[target] = item[source];
  }
  return metadata;
}
