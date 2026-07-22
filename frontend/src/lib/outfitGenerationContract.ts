interface AuthenticatedUserIdentity {
  uid: string;
  displayName?: string | null;
  email?: string | null;
}

type UnknownRecord = Record<string, unknown>;
type ProfileRecord = UnknownRecord | null | undefined;

function asRecord(value: unknown): UnknownRecord {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as UnknownRecord)
    : {};
}

function firstString(...values: unknown[]): string {
  const match = values.find(value => typeof value === 'string' && value.trim().length > 0);
  return typeof match === 'string' ? match.trim() : '';
}

function stringList(value: unknown): string[] {
  const source = Array.isArray(value) ? value : typeof value === 'string' ? [value] : [];
  return source
    .filter((item): item is string => typeof item === 'string')
    .map(item => item.trim())
    .filter((item, index, items) => Boolean(item) && items.indexOf(item) === index);
}

function firstList(...values: unknown[]): string[] {
  for (const value of values) {
    const normalized = stringList(value);
    if (normalized.length > 0) return normalized;
  }
  return [];
}

export function buildOutfitGenerationUserProfile(
  profile: ProfileRecord,
  user: AuthenticatedUserIdentity
) {
  const source = asRecord(profile);
  const measurements = asRecord(source.measurements);
  const preferences = asRecord(source.preferences);
  const colorPalette = asRecord(source.colorPalette);

  const stylePreferences = firstList(
    source.style_preferences,
    source.stylePreferences,
    preferences.style
  );
  const colorPreferences = firstList(
    source.color_preferences,
    source.colorPreferences,
    preferences.colors,
    [
      ...stringList(colorPalette.primary),
      ...stringList(colorPalette.secondary),
      ...stringList(colorPalette.accent),
    ]
  );
  const sizePreferences = firstList(source.size_preferences, source.sizePreferences, [
    measurements.topSize,
    measurements.bottomSize,
    measurements.shoeSize,
    measurements.braSize,
  ]);
  const bodyType = firstString(source.bodyType, source.body_type, measurements.bodyType) || 'average';
  const skinTone = firstString(source.skinTone, source.skin_tone, measurements.skinTone) || null;
  const height = firstString(source.height, measurements.height);
  const weight = firstString(source.weight, measurements.weight);
  const age = typeof source.age === 'number' && Number.isFinite(source.age) ? source.age : 25;

  return {
    id: user.uid,
    name: user.displayName || firstString(source.name) || 'User',
    email: user.email || firstString(source.email),
    gender: firstString(source.gender) || 'male',
    age,
    height,
    weight,
    bodyType,
    skinTone,
    stylePreferences,
    style_preferences: stylePreferences,
    size_preferences: sizePreferences,
    color_preferences: colorPreferences,
    measurements: {
      ...measurements,
      height,
      weight,
      bodyType,
      skinTone,
    },
  };
}

export function assertRequiredBaseItem(
  outfit: { baseItemId?: string | null; items?: Array<{ id?: string | null }> } | null | undefined,
  requiredBaseItemId?: string | null
): void {
  const requestedId = String(requiredBaseItemId || '').trim();
  if (!requestedId) return;

  const responseBaseItemId = String(outfit?.baseItemId || '').trim();
  if (responseBaseItemId && responseBaseItemId !== requestedId) {
    throw new Error('The outfit service returned a different required wardrobe item. Please try again.');
  }

  const includesRequestedItem = (outfit?.items || []).some(
    item => String(item?.id || '').trim() === requestedId
  );
  if (!includesRequestedItem) {
    throw new Error('The generated outfit did not include your selected wardrobe item. Please try again.');
  }
}
