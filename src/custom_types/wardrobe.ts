import { StyleType } from './style_types';

export type SeasonType = 'Spring' | 'Summer' | 'Fall' | 'Winter';
export type FormalityLevel = 'Casual' | 'Business Casual' | 'Business' | 'Formal' | 'Black Tie';

export interface ClothingItem {
  id: string;
  name: string;
  type: string;
  color: string;
  style: StyleType[];
  occasion: string[];
  material?: string;
  metadata: {
    visualAttributes?: {
      material?: string;
      fit?: string;
      pattern?: string;
    };
    tags?: string[];
    care?: {
      washing?: string;
      drying?: string;
      ironing?: string;
    };
    seasonality?: SeasonType[];
    formality?: FormalityLevel;
  };
} 