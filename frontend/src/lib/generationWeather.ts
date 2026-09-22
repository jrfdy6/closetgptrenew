export interface GenerationWeatherProvenance {
  source?: string;
  fallback?: boolean;
  isManualOverride?: boolean;
  isRealWeather?: boolean;
  isFallbackWeather?: boolean;
  observedAt?: string;
  rawCondition?: string;
}

/** Preserve what was used, without treating a missing provenance flag as live weather. */
export function generationWeatherProvenance(weather: GenerationWeatherProvenance): GenerationWeatherProvenance {
  const provenance: GenerationWeatherProvenance = {};
  for (const key of ['fallback', 'isManualOverride', 'isRealWeather', 'isFallbackWeather'] as const) {
    if (typeof weather[key] === 'boolean') provenance[key] = weather[key];
  }
  provenance.source = typeof weather.source === 'string' && weather.source.trim()
    ? weather.source.trim()
    : weather.isManualOverride === true ? 'manual'
      : weather.fallback === true || weather.isFallbackWeather === true ? 'estimated'
        : weather.isRealWeather === true ? 'observed' : 'unknown';
  if (typeof weather.observedAt === 'string' && weather.observedAt.trim()) provenance.observedAt = weather.observedAt;
  if (typeof weather.rawCondition === 'string' && weather.rawCondition.trim()) provenance.rawCondition = weather.rawCondition;
  return provenance;
}
