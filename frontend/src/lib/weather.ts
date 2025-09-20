import { WeatherCondition, WeatherData } from "@/types/weather";

/**
 * Get weather icon emoji based on condition
 */
export function getWeatherIcon(condition: string): string {
  const normalizedCondition = condition.toLowerCase();
  
  if (normalizedCondition.includes('clear') || normalizedCondition.includes('sunny')) {
    return '☀️';
  }
  if (normalizedCondition.includes('partly cloudy')) {
    return '⛅';
  }
  if (normalizedCondition.includes('cloudy') || normalizedCondition.includes('overcast')) {
    return '☁️';
  }
  if (normalizedCondition.includes('rain') || normalizedCondition.includes('shower')) {
    return '🌧️';
  }
  if (normalizedCondition.includes('thunderstorm') || normalizedCondition.includes('storm')) {
    return '⛈️';
  }
  if (normalizedCondition.includes('snow')) {
    return '🌨️';
  }
  if (normalizedCondition.includes('fog') || normalizedCondition.includes('mist')) {
    return '🌫️';
  }
  if (normalizedCondition.includes('wind')) {
    return '💨';
  }
  
  return '🌤️'; // Default
}

/**
 * Convert Celsius to Fahrenheit
 */
export function celsiusToFahrenheit(celsius: number): number {
  return Math.round((celsius * 9/5) + 32);
}

/**
 * Convert Fahrenheit to Celsius
 */
export function fahrenheitToCelsius(fahrenheit: number): number {
  return Math.round((fahrenheit - 32) * 5/9);
}

/**
 * Get temperature range description
 */
export function getTemperatureDescription(temp: number, unit: 'C' | 'F' = 'F'): string {
  const tempInF = unit === 'C' ? celsiusToFahrenheit(temp) : temp;
  
  if (tempInF < 32) return 'Freezing';
  if (tempInF < 45) return 'Very Cold';
  if (tempInF < 55) return 'Cold';
  if (tempInF < 65) return 'Cool';
  if (tempInF < 75) return 'Mild';
  if (tempInF < 85) return 'Warm';
  if (tempInF < 95) return 'Hot';
  return 'Very Hot';
}

/**
 * Get clothing recommendations based on weather
 */
export function getClothingRecommendations(weather: WeatherData): string[] {
  const recommendations: string[] = [];
  const temp = weather.temperature;
  
  // Temperature-based recommendations
  if (temp < 32) {
    recommendations.push('Heavy coat', 'Warm layers', 'Winter accessories');
  } else if (temp < 45) {
    recommendations.push('Jacket', 'Long pants', 'Closed-toe shoes');
  } else if (temp < 55) {
    recommendations.push('Light jacket', 'Long sleeves', 'Jeans');
  } else if (temp < 65) {
    recommendations.push('Light layers', 'Long or short sleeves', 'Comfortable pants');
  } else if (temp < 75) {
    recommendations.push('Light clothing', 'T-shirt', 'Shorts or pants');
  } else if (temp < 85) {
    recommendations.push('Lightweight fabrics', 'Shorts', 'Breathable clothing');
  } else {
    recommendations.push('Minimal clothing', 'Shorts', 'Tank tops', 'Sun protection');
  }
  
  // Weather condition-based recommendations
  if (weather.precipitation > 0 || weather.condition.toLowerCase().includes('rain')) {
    recommendations.push('Umbrella', 'Rain jacket', 'Waterproof shoes');
  }
  
  if (weather.wind_speed > 15) {
    recommendations.push('Wind-resistant jacket', 'Secure accessories');
  }
  
  if (weather.condition.toLowerCase().includes('sun') && temp > 70) {
    recommendations.push('Sunglasses', 'Hat', 'Sunscreen');
  }
  
  return recommendations;
}

/**
 * Determine if weather is suitable for specific clothing types
 */
export function isWeatherSuitableFor(weather: WeatherData, clothingType: string): boolean {
  const temp = weather.temperature;
  const condition = weather.condition.toLowerCase();
  
  switch (clothingType.toLowerCase()) {
    case 'shorts':
      return temp > 65 && !condition.includes('rain');
    case 'tank top':
    case 'sleeveless':
      return temp > 70;
    case 'heavy coat':
    case 'winter jacket':
      return temp < 45;
    case 'light jacket':
      return temp < 65 && temp > 45;
    case 'sandals':
      return temp > 70 && !condition.includes('rain') && !condition.includes('snow');
    case 'boots':
      return temp < 50 || condition.includes('rain') || condition.includes('snow');
    default:
      return true;
  }
}

/**
 * Get weather-appropriate color recommendations
 */
export function getWeatherColors(weather: WeatherData): string[] {
  const colors: string[] = [];
  
  if (weather.condition.toLowerCase().includes('sunny') || weather.condition.toLowerCase().includes('clear')) {
    colors.push('bright colors', 'pastels', 'white', 'light colors');
  }
  
  if (weather.condition.toLowerCase().includes('cloudy') || weather.condition.toLowerCase().includes('overcast')) {
    colors.push('bold colors', 'jewel tones', 'darker colors');
  }
  
  if (weather.condition.toLowerCase().includes('rain')) {
    colors.push('darker colors', 'waterproof materials');
  }
  
  return colors;
}

/**
 * Format weather data for display
 */
export function formatWeatherForDisplay(weather: WeatherData): {
  temperature: string;
  condition: string;
  details: string[];
} {
  return {
    temperature: `${Math.round(weather.temperature)}°F`,
    condition: `${getWeatherIcon(weather.condition)} ${weather.condition}`,
    details: [
      `Humidity: ${weather.humidity}%`,
      `Wind: ${weather.wind_speed} mph`,
      ...(weather.precipitation > 0 ? [`Precipitation: ${weather.precipitation} mm`] : [])
    ]
  };
}
