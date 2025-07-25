// Weather data interface for the application
export interface WeatherData {
  temperature: number;
  condition: string;
  location: string;
  humidity: number;
  wind_speed: number;
  precipitation: number;
  fallback?: boolean;
}

export type WeatherCondition = 
  | 'clear'
  | 'partly_cloudy'
  | 'cloudy'
  | 'rain'
  | 'snow'
  | 'thunderstorm'
  | 'fog'
  | 'windy'; 