/**
 * Performance Service
 * Handles caching, optimistic updates, and performance monitoring
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

class PerformanceService {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly WARDROBE_TTL = 2 * 60 * 1000; // 2 minutes
  private readonly OUTFIT_TTL = 10 * 60 * 1000; // 10 minutes
  private readonly USER_DATA_TTL = 15 * 60 * 1000; // 15 minutes

  // Performance metrics
  private metrics: {
    cacheHits: number;
    cacheMisses: number;
    apiCalls: number;
    avgResponseTime: number;
    responseTimes: number[];
  } = {
    cacheHits: 0,
    cacheMisses: 0,
    apiCalls: 0,
    avgResponseTime: 0,
    responseTimes: []
  };

  /**
   * Get data from cache or fetch if not available/expired
   */
  async getOrFetch<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = this.get<T>(key);
    if (cached !== null) {
      this.metrics.cacheHits++;
      return cached;
    }

    this.metrics.cacheMisses++;
    this.metrics.apiCalls++;

    const startTime = performance.now();
    try {
      const data = await fetcher();
      const responseTime = performance.now() - startTime;
      this.recordResponseTime(responseTime);
      
      this.set(key, data, ttl);
      return data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get data from cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) {
      return null;
    }

    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Set data in cache
   */
  set<T>(key: string, data: T, ttl?: number): void {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.DEFAULT_TTL
    };
    this.cache.set(key, entry);
  }

  /**
   * Invalidate cache entry
   */
  invalidate(key: string): void {
    this.cache.delete(key);
  }

  /**
   * Invalidate all cache entries matching a pattern
   */
  invalidatePattern(pattern: string | RegExp): void {
    const regex = typeof pattern === 'string' 
      ? new RegExp(pattern.replace('*', '.*'))
      : pattern;
    
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache key for wardrobe
   */
  getWardrobeKey(userId: string): string {
    return `wardrobe:${userId}`;
  }

  /**
   * Get cache key for outfit
   */
  getOutfitKey(userId: string, outfitId?: string): string {
    return outfitId 
      ? `outfit:${userId}:${outfitId}`
      : `outfits:${userId}`;
  }

  /**
   * Get cache key for user data
   */
  getUserDataKey(userId: string): string {
    return `user:${userId}`;
  }

  /**
   * Get cache key for usage data
   */
  getUsageKey(userId: string): string {
    return `usage:${userId}`;
  }

  /**
   * Record API response time
   */
  private recordResponseTime(time: number): void {
    this.metrics.responseTimes.push(time);
    // Keep only last 100 response times
    if (this.metrics.responseTimes.length > 100) {
      this.metrics.responseTimes.shift();
    }
    
    // Calculate average
    const sum = this.metrics.responseTimes.reduce((a, b) => a + b, 0);
    this.metrics.avgResponseTime = sum / this.metrics.responseTimes.length;
  }

  /**
   * Get performance metrics
   */
  getMetrics() {
    const totalRequests = this.metrics.cacheHits + this.metrics.cacheMisses;
    const hitRate = totalRequests > 0 
      ? (this.metrics.cacheHits / totalRequests) * 100 
      : 0;

    return {
      ...this.metrics,
      hitRate: Math.round(hitRate * 100) / 100,
      cacheSize: this.cache.size,
      totalRequests
    };
  }

  /**
   * Reset metrics
   */
  resetMetrics(): void {
    this.metrics = {
      cacheHits: 0,
      cacheMisses: 0,
      apiCalls: 0,
      avgResponseTime: 0,
      responseTimes: []
    };
  }

  // Convenience methods with appropriate TTLs
  async getWardrobe<T>(userId: string, fetcher: () => Promise<T>): Promise<T> {
    return this.getOrFetch(
      this.getWardrobeKey(userId),
      fetcher,
      this.WARDROBE_TTL
    );
  }

  async getOutfits<T>(userId: string, fetcher: () => Promise<T>, outfitId?: string): Promise<T> {
    return this.getOrFetch(
      this.getOutfitKey(userId, outfitId),
      fetcher,
      this.OUTFIT_TTL
    );
  }

  async getUserData<T>(userId: string, fetcher: () => Promise<T>): Promise<T> {
    return this.getOrFetch(
      this.getUserDataKey(userId),
      fetcher,
      this.USER_DATA_TTL
    );
  }

  async getUsage<T>(userId: string, fetcher: () => Promise<T>): Promise<T> {
    return this.getOrFetch(
      this.getUsageKey(userId),
      fetcher,
      this.WARDROBE_TTL
    );
  }
}

export const performanceService = new PerformanceService();

