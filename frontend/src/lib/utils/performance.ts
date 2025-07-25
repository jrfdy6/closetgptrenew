// Performance monitoring utilities
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number> = new Map();

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  // Track page load time
  trackPageLoad(pageName: string) {
    if (typeof window !== 'undefined') {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
        this.metrics.set(`${pageName}_load_time`, loadTime);
        console.log(`Page load time for ${pageName}: ${loadTime}ms`);
      }
    }
  }

  // Track component render time
  trackComponentRender(componentName: string, startTime: number) {
    const renderTime = performance.now() - startTime;
    this.metrics.set(`${componentName}_render_time`, renderTime);
    console.log(`Component render time for ${componentName}: ${renderTime}ms`);
  }

  // Track image load time
  trackImageLoad(imageUrl: string, startTime: number) {
    const loadTime = performance.now() - startTime;
    this.metrics.set(`image_${imageUrl}_load_time`, loadTime);
    console.log(`Image load time for ${imageUrl}: ${loadTime}ms`);
  }

  // Track API call time
  trackApiCall(endpoint: string, startTime: number) {
    const callTime = performance.now() - startTime;
    this.metrics.set(`api_${endpoint}_call_time`, callTime);
    console.log(`API call time for ${endpoint}: ${callTime}ms`);
  }

  // Get all metrics
  getMetrics(): Map<string, number> {
    return new Map(this.metrics);
  }

  // Clear metrics
  clearMetrics() {
    this.metrics.clear();
  }

  // Report metrics to analytics
  reportMetrics() {
    const metrics = this.getMetrics();
    // Send to analytics service
    console.log('Performance metrics:', Object.fromEntries(metrics));
  }
}

// Core Web Vitals monitoring
export function monitorCoreWebVitals() {
  if (typeof window === 'undefined') return;

  // Largest Contentful Paint (LCP)
  new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
      const lcp = entry.startTime;
      console.log('LCP:', lcp);
      // Report to analytics
    }
  }).observe({ entryTypes: ['largest-contentful-paint'] });

  // First Input Delay (FID)
  new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
      const fidEntry = entry as PerformanceEventTiming;
      const fid = fidEntry.processingStart - fidEntry.startTime;
      console.log('FID:', fid);
      // Report to analytics
    }
  }).observe({ entryTypes: ['first-input'] });

  // Cumulative Layout Shift (CLS)
  new PerformanceObserver((entryList) => {
    let cls = 0;
    for (const entry of entryList.getEntries()) {
      const layoutShiftEntry = entry as any;
      if (!layoutShiftEntry.hadRecentInput) {
        cls += layoutShiftEntry.value;
      }
    }
    console.log('CLS:', cls);
    // Report to analytics
  }).observe({ entryTypes: ['layout-shift'] });
}

// Image optimization utilities
export function preloadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve();
    img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
    img.src = src;
  });
}

export function preloadCriticalImages(images: string[]) {
  return Promise.allSettled(images.map(preloadImage));
}

// Bundle size monitoring
export function getBundleSize() {
  if (typeof window === 'undefined') return null;

  const performance = window.performance;
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  
  if (navigation) {
    return {
      transferSize: navigation.transferSize,
      encodedBodySize: navigation.encodedBodySize,
      decodedBodySize: navigation.decodedBodySize,
    };
  }
  
  return null;
}

// Memory usage monitoring
export function getMemoryUsage() {
  if (typeof window === 'undefined' || !('memory' in performance)) return null;

  const memory = (performance as any).memory;
  return {
    usedJSHeapSize: memory.usedJSHeapSize,
    totalJSHeapSize: memory.totalJSHeapSize,
    jsHeapSizeLimit: memory.jsHeapSizeLimit,
  };
}

// Network monitoring
export function getNetworkInfo() {
  if (typeof navigator === 'undefined' || !('connection' in navigator)) return null;

  const connection = (navigator as any).connection;
  return {
    effectiveType: connection.effectiveType,
    downlink: connection.downlink,
    rtt: connection.rtt,
    saveData: connection.saveData,
  };
}

// Performance budget checking
export function checkPerformanceBudget(metrics: Map<string, number>) {
  const budgets = {
    page_load_time: 3000, // 3 seconds
    component_render_time: 100, // 100ms
    image_load_time: 1000, // 1 second
    api_call_time: 2000, // 2 seconds
  };

  const violations: string[] = [];

  for (const [metric, value] of metrics) {
    for (const [budgetName, budgetValue] of Object.entries(budgets)) {
      if (metric.includes(budgetName) && value > budgetValue) {
        violations.push(`${metric}: ${value}ms (budget: ${budgetValue}ms)`);
      }
    }
  }

  if (violations.length > 0) {
    console.warn('Performance budget violations:', violations);
  }

  return violations;
}

// Initialize performance monitoring
export function initializePerformanceMonitoring() {
  monitorCoreWebVitals();
  
  // Track page load time
  if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
      const monitor = PerformanceMonitor.getInstance();
      monitor.trackPageLoad(window.location.pathname);
    });
  }
} 