// API endpoints
export const API_ENDPOINTS = {
  CLOTHING: '/api/clothing',
  OUTFITS: '/api/outfits',
  FEEDBACK: '/api/feedback',
  ANALYSIS: '/api/analysis'
} as const;

// Firebase collections
export const FIREBASE_COLLECTIONS = {
  WARDROBE: 'wardrobe',
  CLOTHING: 'clothing',
  OUTFITS: 'outfits',
  FEEDBACK: 'feedback',
  USERS: 'users'
} as const;

// Storage paths
export const STORAGE_PATHS = {
  CLOTHING_IMAGES: 'clothing-images',
  OUTFIT_IMAGES: 'outfit-images',
  USER_AVATARS: 'user-avatars'
} as const;

// Image settings
export const IMAGE_SETTINGS = {
  MAX_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  MAX_DIMENSION: 2048,
  QUALITY: 0.8
} as const;

// File validation constants
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

// Error codes
export const ERROR_CODES = {
  INVALID_INPUT: 'INVALID_INPUT',
  UNAUTHORIZED: 'UNAUTHORIZED',
  NOT_FOUND: 'NOT_FOUND',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  STORAGE_ERROR: 'STORAGE_ERROR',
  ANALYSIS_ERROR: 'ANALYSIS_ERROR'
} as const;

// Clothing types
export const CLOTHING_TYPES = [
  'shirt',
  'pants',
  'dress',
  'skirt',
  'jacket',
  'sweater',
  'shoes',
  'accessory',
  'other'
] as const;

// Seasons
export const SEASONS = [
  'spring',
  'summer',
  'fall',
  'winter'
] as const;

// Occasions
export const OCCASIONS = [
  'casual',
  'formal',
  'business',
  'athletic',
  'party',
  'beach',
  'outdoor',
  'evening',
  'wedding',
  'other'
] as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
} as const;

// Cache settings
export const CACHE_SETTINGS = {
  CLOTHING_TTL: 60 * 60 * 1000, // 1 hour
  OUTFITS_TTL: 60 * 60 * 1000, // 1 hour
  USER_TTL: 24 * 60 * 60 * 1000 // 24 hours
} as const; 