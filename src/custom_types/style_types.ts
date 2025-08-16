// Core Aesthetic Styles
export type StyleType =
  | "Dark Academia"
  | "Old Money"
  | "Streetwear"
  | "Y2K"
  | "Minimalist"
  | "Boho"
  | "Preppy"
  | "Grunge"
  | "Classic"
  | "Techwear"
  | "Androgynous"
  | "Coastal Chic"
  | "Business Casual"
  | "Avant-Garde"
  | "Cottagecore"
  | "Edgy"
  | "Athleisure"
  | "Casual Cool"
  | "Romantic"
  | "Artsy";

// Formality Subtypes
export type FormalitySubtype =
  | "Casual"
  | "Smart Casual"
  | "Business Casual"
  | "Business Formal"
  | "Business"
  | "Black Tie"
  | "Lounge"
  | "Gala"
  | "Special Occasion";

// Activity Subtypes
export type ActivitySubtype =
  | "Date Night"
  | "Office"
  | "Brunch"
  | "Workout"
  | "Travel"
  | "Errands"
  | "Beach"
  | "Hiking"
  | "Festival"
  | "Interview"
  | "Wedding Guest"
  | "Party"
  | "School"
  | "Chill at Home";

// Weather-Based Subtypes
export type WeatherSubtype =
  | "Hot Weather"
  | "Cold Weather"
  | "Rainy Day"
  | "Windy"
  | "Snowy"
  | "Transitional Season";

// Mood or Intent-Based Subtypes
export type MoodSubtype =
  | "Confident"
  | "Playful"
  | "Relaxed"
  | "Bold"
  | "Mysterious"
  | "Creative"
  | "Cozy"
  | "Sexy"
  | "Professional"
  | "Rebellious";

// Theme or Season-Based Subtypes
export type ThemeSubtype =
  | "Summer in the City"
  | "Winter Wonderland"
  | "Holiday Party"
  | "Back to School"
  | "Resort"
  | "Valentine's Day"
  | "Pride"
  | "New Year's Eve"
  | "Spring Awakening"
  | "Fall Vibes";

// Style Rules Interface
export interface StyleRules {
  colorHarmony: string[];
  silhouetteBalance: string[];
  requiredElements: string[];
  forbiddenElements: string[];
  patternRules: {
    allowed: string[];
    forbidden: string[];
  };
  materialRules: {
    preferred: string[];
    avoid: string[];
  };
  fit: string[];
  silhouette: string[];
  keyItems: string[];
  avoidItems: string[];
  textures: string[];
  footwear: string[];
  accessories: string[];
  layering: string[];
  occasionFit: string[];
  seasonalFit: string[];
  popCultureExamples: string[];
  notes: string;
}

// Style Dictionary Type
export type StyleDictionary = {
  [key in StyleType]: StyleRules;
}; 