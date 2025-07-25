export type QuizQuestionType = 'outfit' | 'color' | 'icon' | 'style';

export interface QuizQuestion {
  id: string;
  type: QuizQuestionType;
  question: string;
  options: QuizOption[];
  nextQuestionId?: string;
}

export interface QuizOption {
  id: string;
  label: string;
  imageUrl?: string;
  styleAttributes: StyleAttributes;
}

export interface StyleAttributes {
  colors: string[];
  patterns: string[];
  styles: string[];
  formality: 'casual' | 'business' | 'formal';
  seasonality: ('spring' | 'summer' | 'fall' | 'winter')[];
}

export interface QuizState {
  currentQuestionId: string;
  answers: Record<string, string>;
  completed: boolean;
  styleProfile: StyleProfile;
}

export interface StyleProfile {
  preferredColors: string[];
  preferredPatterns: string[];
  preferredStyles: string[];
  formality: 'casual' | 'business' | 'formal';
  seasonality: ('spring' | 'summer' | 'fall' | 'winter')[];
  confidence: number;
} 