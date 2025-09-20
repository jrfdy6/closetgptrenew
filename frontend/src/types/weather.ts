export interface WeatherData {
  temperature: number;
  condition: string;
  humidity: number;
  wind_speed: number;
  location: string;
  precipitation: number;
  fallback?: boolean;
}

export interface WeatherRequest {
  location: string;
}

export interface WeatherApiResponse extends WeatherData {
  success?: boolean;
  error?: string;
}

export type WeatherCondition = 
  | "Clear"
  | "Sunny" 
  | "Partly Cloudy"
  | "Cloudy"
  | "Overcast"
  | "Rain"
  | "Light Rain"
  | "Heavy Rain"
  | "Thunderstorm"
  | "Snow"
  | "Light Snow"
  | "Heavy Snow"
  | "Fog"
  | "Mist"
  | "Windy"
  | "Hot"
  | "Cold";

export interface UserLocation {
  city?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  timezone?: string;
}
