// Stub implementation for apiWithAnalytics
// This is a temporary fix to resolve import errors

export const apiWithAnalytics = {
  get: async (url: string) => {
    console.warn('apiWithAnalytics.get called with:', url);
    return { data: null };
  },
  post: async (url: string, data?: any) => {
    console.warn('apiWithAnalytics.post called with:', url, data);
    return { data: null };
  },
  put: async (url: string, data?: any) => {
    console.warn('apiWithAnalytics.put called with:', url, data);
    return { data: null };
  },
  delete: async (url: string) => {
    console.warn('apiWithAnalytics.delete called with:', url);
    return { data: null };
  }
}; 