import dynamic from 'next/dynamic';

// Simple loading component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-4">
    <div className="animate-spin rounded-full h-6 w-6 border-2 border-emerald-200 border-t-emerald-600"></div>
  </div>
);

// Dynamic imports with loading states
export function createDynamicComponent(
  importFn: () => Promise<any>,
  options: {
    ssr?: boolean;
    suspense?: boolean;
  } = {}
) {
  return dynamic(importFn, {
    loading: LoadingSpinner,
    ssr: options.ssr ?? false,
  });
}

// Lazy load dashboard components
export const LazyWardrobeInsights = createDynamicComponent(
  () => import('@/components/dashboard/WardrobeInsights'),
  { ssr: false }
);

export const LazyStyleGoalsProgress = createDynamicComponent(
  () => import('@/components/dashboard/StyleGoalsProgress'),
  { ssr: false }
);

export const LazyWardrobeGapAnalysis = createDynamicComponent(
  () => import('@/components/dashboard/WardrobeGapAnalysis'),
  { ssr: false }
);

export const LazyForgottenGems = createDynamicComponent(
  () => import('@/components/dashboard/ForgottenGems'),
  { ssr: false }
);

export const LazyTodaysOutfitRecommendation = createDynamicComponent(
  () => import('@/components/dashboard/TodaysOutfitRecommendation'),
  { ssr: false }
);

// Lazy load heavy components
export const LazyImageUpload = createDynamicComponent(
  () => import('@/components/BatchImageUpload'),
  { ssr: false }
);

// export const LazyStyleQuiz = createDynamicComponent(
//   () => import('@/components/StyleQuiz'),
//   { ssr: false }
// );

export const LazyAnalytics = createDynamicComponent(
  () => import('@/components/analytics/AnalyticsDashboard'),
  { ssr: false }
);

// Lazy load forms
export const LazyUploadForm = createDynamicComponent(
  () => import('@/components/UploadForm'),
  { ssr: false }
);

export const LazyOnboardingWizard = createDynamicComponent(
  () => import('@/components/onboarding/StepWizard'),
  { ssr: false }
);

// Preload utilities
export function preloadComponent(importFn: () => Promise<any>) {
  return () => {
    importFn();
  };
}

// Preload critical components
export const preloadDashboard = preloadComponent(
  () => import('@/components/dashboard/WardrobeInsights')
);

export const preloadUpload = preloadComponent(
  () => import('@/components/UploadForm')
);

export const preloadOnboarding = preloadComponent(
  () => import('@/components/onboarding/StepWizard')
); 