export function extractWeatherAppropriateness(content: string): string {
  const weatherSection = content.split('Weather Appropriateness:')[1]?.split('\n')[0]?.trim();
  return weatherSection || 'Weather appropriateness not specified';
} 