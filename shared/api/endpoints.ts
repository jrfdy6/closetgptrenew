export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login`,
    REGISTER: `${API_BASE_URL}/api/auth/register`,
    LOGOUT: `${API_BASE_URL}/api/auth/logout`,
    REFRESH: `${API_BASE_URL}/api/auth/refresh`,
  },
  
  // User endpoints
  USER: {
    PROFILE: '/api/user/profile',
    UPDATE_PROFILE: `${API_BASE_URL}/api/users/profile`,
    STYLE_PROFILE: `${API_BASE_URL}/api/users/style-profile`,
    PREFERENCES: '/api/user/preferences',
    SETTINGS: '/api/user/settings'
  },
  
  // Wardrobe endpoints
  WARDROBE: {
    LIST: '/api/wardrobe',
    CREATE: '/api/wardrobe',
    GET: (id: string) => `/api/wardrobe/${id}`,
    UPDATE: (id: string) => `/api/wardrobe/${id}`,
    DELETE: (id: string) => `/api/wardrobe/${id}`,
    ANALYZE: '/api/wardrobe/analyze'
  },
  
  // Outfit endpoints
  OUTFITS: {
    LIST: '/api/outfits',
    CREATE: '/api/outfits',
    GET: (id: string) => `/api/outfit/${id}`,
    UPDATE: (id: string) => `/api/outfit/${id}`,
    DELETE: (id: string) => `/api/outfit/${id}`,
    RECOMMENDATIONS: '/api/outfits/recommendations',
    GENERATE: '/api/outfit/generate'  // ✅ UPDATED: Use the correct endpoint
  },
  
  // AI endpoints
  AI: {
    STYLE_ADVICE: `${API_BASE_URL}/api/ai/style-advice`,
    OUTFIT_RECOMMENDATIONS: `${API_BASE_URL}/api/ai/outfit-recommendations`,
    COLOR_ANALYSIS: `${API_BASE_URL}/api/ai/color-analysis`,
  },
  
  // Weather endpoints
  WEATHER: {
    CURRENT: '/weather/current',
    FORECAST: '/weather/forecast'
  }
}; 