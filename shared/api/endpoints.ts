export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-backend-production.up.railway.app';

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    VERIFY_TOKEN: `${API_BASE_URL}/auth/verify-token`,
  },
  
  // User endpoints - these may need to be implemented on backend
  USER: {
    PROFILE: `${API_BASE_URL}/api/user/profile`,
    UPDATE_PROFILE: `${API_BASE_URL}/api/users/profile`,
    STYLE_PROFILE: `${API_BASE_URL}/api/users/style-profile`,
    PREFERENCES: `${API_BASE_URL}/api/user/preferences`,
    SETTINGS: `${API_BASE_URL}/api/user/settings`
  },
  
  // Wardrobe endpoints - ✅ AVAILABLE ON BACKEND
  WARDROBE: {
    LIST: `${API_BASE_URL}/api/wardrobe`,
    CREATE: `${API_BASE_URL}/api/wardrobe`,
    GET: (id: string) => `${API_BASE_URL}/api/wardrobe/${id}`,
    UPDATE: (id: string) => `${API_BASE_URL}/api/wardrobe/${id}`,
    DELETE: (id: string) => `${API_BASE_URL}/api/wardrobe/${id}`,
    STATS: `${API_BASE_URL}/api/wardrobe/wardrobe-stats`,
    GAPS: `${API_BASE_URL}/api/wardrobe/gaps`,
    RECOMMENDATIONS: `${API_BASE_URL}/api/wardrobe/recommendations`,
    FORGOTTEN_GEMS: `${API_BASE_URL}/api/wardrobe/forgotten-gems`,
    TRENDING_STYLES: `${API_BASE_URL}/api/wardrobe/trending-styles`,
    COVERAGE: `${API_BASE_URL}/api/wardrobe/coverage`,
    VALIDATION_ERRORS: `${API_BASE_URL}/api/wardrobe/validation-errors`,
    INCREMENT_WEAR: `${API_BASE_URL}/api/wardrobe/increment-wear`,
    FORCE_REFRESH_TRENDS: `${API_BASE_URL}/api/wardrobe/force-refresh-trends`
  },
  
  // Outfit endpoints - ✅ AVAILABLE ON BACKEND
  OUTFITS: {
    GENERATE: `${API_BASE_URL}/api/outfits/generate`,
    LIST: `${API_BASE_URL}/api/outfits`,
    GET: (id: string) => `${API_BASE_URL}/api/outfits/${id}`,
    CREATE: `${API_BASE_URL}/api/outfits`,
    UPDATE: (id: string) => `${API_BASE_URL}/api/outfits/${id}`,
    DELETE: (id: string) => `${API_BASE_URL}/api/outfits/${id}`,
    HISTORY: `${API_BASE_URL}/api/outfit-history`,
    HISTORY_STATS: `${API_BASE_URL}/api/outfit-history/stats`,
    MARK_WORN: `${API_BASE_URL}/api/outfit-history/mark-worn`
  },
  
  // Image processing endpoints - ✅ AVAILABLE ON BACKEND
  IMAGE: {
    UPLOAD: `${API_BASE_URL}/api/image/upload`,
    PROCESS: `${API_BASE_URL}/api/process-image`,
    ANALYZE: `${API_BASE_URL}/api/analyze-image`,
    DELETE: `${API_BASE_URL}/api/delete-photo`
  },
  
  // Analytics endpoints - ✅ AVAILABLE ON BACKEND
  ANALYTICS: {
    OUTFIT_FEEDBACK: `${API_BASE_URL}/api/analytics/outfit-feedback`,
    WARDROBE_STATS: `${API_BASE_URL}/api/analytics/wardrobe-stats`,
    EVENT: `${API_BASE_URL}/api/analytics/event`,
    OUTFITS: `${API_BASE_URL}/api/analytics/outfits`
  },
  
  // Style quiz endpoints - ✅ AVAILABLE ON BACKEND
  STYLE_QUIZ: {
    SUBMIT: `${API_BASE_URL}/api/style-quiz/submit`,
    ANALYZE: `${API_BASE_URL}/api/style-quiz/analyze`
  },
  
  // Profile endpoints - ✅ AVAILABLE ON BACKEND
  PROFILE: {
    SAVE: `${API_BASE_URL}/api/profile/save`,
    UPDATE_STYLE: `${API_BASE_URL}/api/update-style-profile`
  },
  
  // Validation rules endpoints - ✅ AVAILABLE ON BACKEND
  VALIDATION: {
    RULES: `${API_BASE_URL}/api/validation-rules`,
    UPDATE: `${API_BASE_URL}/api/validation-rules/update`,
    APPLY_FIX: `${API_BASE_URL}/api/validation-rules/apply-fix`,
    GENERATE_FIX: `${API_BASE_URL}/api/validation-rules/generate-fix-suggestion`
  },
  
  // Weather endpoint - ✅ AVAILABLE ON BACKEND
  WEATHER: `${API_BASE_URL}/api/weather`,
  
  // Health check endpoint - ✅ AVAILABLE ON BACKEND
  HEALTH: `${API_BASE_URL}/health`,
  
  // Test endpoints - ✅ AVAILABLE ON BACKEND
  TEST: {
    AUTH: `${API_BASE_URL}/api/test-auth`,
    GENDER: `${API_BASE_URL}/api/test-gender`
  }
}; 