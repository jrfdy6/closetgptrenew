export interface OutfitConfiguration {
  occasion: string;
  style: string;
  mood: string;
}

// Surprise Me should choose a useful brief. These defaults only apply to random
// generation; deliberate style and occasion selections remain unrestricted.
const RANDOM_STYLES_BY_OCCASION: Readonly<Record<string, readonly string[]>> = {
  Casual: ['Casual Cool', 'Classic', 'Minimalist', 'Modern', 'Preppy', 'Streetwear', 'Boho', 'Coastal Chic', 'Scandinavian', 'Athleisure'],
  Business: ['Classic', 'Business Casual', 'Preppy', 'Urban Professional', 'Minimalist', 'Old Money'],
  Party: ['Y2K', 'Artsy', 'Maximalist', 'Colorblock', 'Romantic', 'Modern', 'Monochrome', 'Edgy', 'Classic'],
  Date: ['Classic', 'Romantic', 'Minimalist', 'Modern', 'Old Money', 'Preppy', 'French Girl', 'Coastal Chic', 'Monochrome'],
  Interview: ['Classic', 'Business Casual', 'Preppy', 'Urban Professional', 'Minimalist', 'Old Money'],
  Weekend: ['Casual Cool', 'Classic', 'Minimalist', 'Modern', 'Preppy', 'Streetwear', 'Boho', 'Coastal Chic', 'Athleisure', 'Cottagecore'],
  Loungewear: ['Loungewear', 'Casual Cool', 'Athleisure', 'Minimalist'],
  Gym: ['Workout', 'Athleisure'],
};

export function randomOutfitConfiguration(
  options: {
    occasions: readonly string[];
    styles: readonly string[];
    moods: readonly string[];
  },
  random: () => number = Math.random,
): OutfitConfiguration | null {
  const eligibleOccasions = options.occasions.flatMap(occasion => {
    const styles = (RANDOM_STYLES_BY_OCCASION[occasion] ?? []).filter(style => options.styles.includes(style));
    return styles.length > 0 ? [{ occasion, styles }] : [];
  });

  if (eligibleOccasions.length === 0 || options.moods.length === 0) return null;

  const pick = <T,>(values: readonly T[]): T => values[Math.floor(random() * values.length)];
  // Choose the occasion first, so occasions with more styles are not favored.
  const selected = pick(eligibleOccasions);
  return {
    occasion: selected.occasion,
    style: pick(selected.styles),
    mood: pick(options.moods),
  };
}
