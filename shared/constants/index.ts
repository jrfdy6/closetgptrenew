export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export const CLOTHING_CATEGORIES = {
  TOPS: 'tops',
  BOTTOMS: 'bottoms',
  DRESSES: 'dresses',
  OUTERWEAR: 'outerwear',
  SHOES: 'shoes',
  ACCESSORIES: 'accessories',
} as const;

export const OCCASIONS = {
  CASUAL: 'casual',
  FORMAL: 'formal',
  BUSINESS: 'business',
  ATHLETIC: 'athletic',
  PARTY: 'party',
  BEACH: 'beach',
} as const;

export const SEASONS = {
  SPRING: 'spring',
  SUMMER: 'summer',
  FALL: 'fall',
  WINTER: 'winter',
} as const;

export const COLORS = {
  BLACK: '#000000',
  WHITE: '#FFFFFF',
  RED: '#FF0000',
  BLUE: '#0000FF',
  GREEN: '#008000',
  YELLOW: '#FFFF00',
  PURPLE: '#800080',
  PINK: '#FFC0CB',
  BROWN: '#A52A2A',
  GRAY: '#808080',
} as const;

export const MATERIALS = {
  COTTON: 'cotton',
  WOOL: 'wool',
  SILK: 'silk',
  LINEN: 'linen',
  DENIM: 'denim',
  LEATHER: 'leather',
  POLYESTER: 'polyester',
  NYLON: 'nylon',
  VELVET: 'velvet',
  FUR: 'fur',
} as const;

const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_PROFILE: 'user_profile',
  STYLE_PREFERENCES: 'style_preferences',
} as const;

export type StorageKeys = typeof STORAGE_KEYS;
export { STORAGE_KEYS }; 