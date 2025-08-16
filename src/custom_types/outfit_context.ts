import { 
  FormalitySubtype, 
  ActivitySubtype, 
  WeatherSubtype, 
  MoodSubtype, 
  ThemeSubtype 
} from './style_types';

export interface OutfitContext {
  formalityLevel: FormalitySubtype;
  activityContext: ActivitySubtype;
  weatherContext: WeatherSubtype;
  moodContext: MoodSubtype;
  themeContext?: ThemeSubtype;
}

export interface ContextRules {
  requiredElements: string[];
  forbiddenElements: string[];
  materialRules: {
    preferred: string[];
    avoid: string[];
  };
  colorRules: {
    preferred: string[];
    avoid: string[];
  };
}

export interface OutfitContextRules {
  formalityLevel: {
    [key in FormalitySubtype]: ContextRules;
  };
  activityContext: {
    [key in ActivitySubtype]: ContextRules;
  };
  weatherContext: {
    [key in WeatherSubtype]: ContextRules;
  };
  moodContext: {
    [key in MoodSubtype]: ContextRules;
  };
  themeContext: {
    [key in ThemeSubtype]: ContextRules;
  };
} 