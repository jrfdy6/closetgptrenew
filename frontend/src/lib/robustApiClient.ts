/**
 * Enterprise-grade API client with comprehensive error handling,
 * retry logic, circuit breakers, and monitoring
 */

import { handleError, retryWithBackoff, CircuitBreaker } from './errorHandler';
import { DataValidator } from './dataValidator';

export interface ApiClientConfig {
  baseUrl: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
  enableCircuitBreaker: boolean;
  enableMetrics: boolean;
}

export interface ApiRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  endpoint: string;
  data?: any;
  headers?: Record<string, string>;
  timeout?: number;
  retryable?: boolean;
  authToken?: string;
}

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  headers: Record<string, string>;
  timestamp: number;
  requestId: string;
}

export interface ApiMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  errorRate: number;
  lastRequestTime: number;
}

export class RobustApiClient {
  private static instance: RobustApiClient;
  private config: ApiClientConfig;
  private circuitBreaker: CircuitBreaker;
  private metrics: ApiMetrics;
  private requestQueue: Array<() => Promise<any>> = [];
  private isProcessingQueue = false;

  private constructor(config: Partial<ApiClientConfig> = {}) {
    this.config = {
      baseUrl: config.baseUrl || '/api',
      timeout: config.timeout || 30000,
      maxRetries: config.maxRetries || 3,
      retryDelay: config.retryDelay || 1000,
      enableCircuitBreaker: config.enableCircuitBreaker !== false,
      enableMetrics: config.enableMetrics !== false,
      ...config
    };

    this.circuitBreaker = new CircuitBreaker(5, 60000, 30000);
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      errorRate: 0,
      lastRequestTime: 0
    };
  }

  public static getInstance(config?: Partial<ApiClientConfig>): RobustApiClient {
    if (!RobustApiClient.instance) {
      RobustApiClient.instance = new RobustApiClient(config);
    }
    return RobustApiClient.instance;
  }

  /**
   * Make a robust API request with comprehensive error handling
   */
  public async request<T = any>(request: ApiRequest): Promise<ApiResponse<T>> {
    const requestId = this.generateRequestId();
    const startTime = Date.now();

    try {
      // Validate request data if it's a POST/PUT/PATCH
      if (['POST', 'PUT', 'PATCH'].includes(request.method) && request.data) {
        const validator = DataValidator.getInstance();
        const validationResult = validator.validateOutfitRequest(request.data);
        
        if (!validationResult.isValid) {
          throw new Error(`Validation failed: ${validationResult.errors.join(', ')}`);
        }
        
        request.data = validationResult.sanitizedValue;
      }

      // Execute request with circuit breaker
      const response = await this.executeRequest<T>(request, requestId);
      
      // Update metrics
      this.updateMetrics(true, Date.now() - startTime);
      
      return response;

    } catch (error) {
      // Update metrics
      this.updateMetrics(false, Date.now() - startTime);
      
      // Handle error with comprehensive logging
      return await handleError(
        error as Error,
        `api_request_${request.method.toLowerCase()}`,
        {
          component: 'RobustApiClient',
          retryable: request.retryable !== false,
          fallbackAction: () => this.getFallbackResponse<T>(request),
          userMessage: this.getUserFriendlyMessage(error as Error)
        }
      );
    }
  }

  /**
   * Execute the actual HTTP request
   */
  private async executeRequest<T>(request: ApiRequest, requestId: string): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}${request.endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'X-Request-ID': requestId,
      ...request.headers
    };

    // Add authentication header if token is provided
    if (request.authToken) {
      headers['Authorization'] = `Bearer ${request.authToken}`;
    }

    const fetchConfig: RequestInit = {
      method: request.method,
      headers,
      signal: AbortSignal.timeout(request.timeout || this.config.timeout)
    };

    if (request.data && ['POST', 'PUT', 'PATCH'].includes(request.method)) {
      fetchConfig.body = JSON.stringify(request.data);
    }

    const executeWithCircuitBreaker = async (): Promise<Response> => {
      if (this.config.enableCircuitBreaker) {
        return await this.circuitBreaker.execute(() => fetch(url, fetchConfig));
      } else {
        return await fetch(url, fetchConfig);
      }
    };

    const response = await retryWithBackoff(
      executeWithCircuitBreaker,
      this.config.maxRetries,
      this.config.retryDelay
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    const responseHeaders: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    return {
      data,
      status: response.status,
      headers: responseHeaders,
      timestamp: Date.now(),
      requestId
    };
  }

  /**
   * Get fallback response for failed requests
   */
  private async getFallbackResponse<T>(request: ApiRequest): Promise<ApiResponse<T>> {
    // Implement fallback logic based on request type
    if (request.endpoint.includes('/outfit/generate')) {
      return {
        data: this.getFallbackOutfit() as T,
        status: 200,
        headers: {},
        timestamp: Date.now(),
        requestId: 'fallback'
      };
    }

    throw new Error('No fallback available for this request');
  }

  /**
   * Get fallback outfit data
   */
  private getFallbackOutfit(): any {
    return {
      id: 'fallback-outfit',
      name: 'Fallback Outfit',
      items: [
        {
          id: 'fallback-top',
          name: 'Basic Top',
          type: 'T_SHIRT',
          color: 'white',
          imageUrl: ''
        },
        {
          id: 'fallback-bottom',
          name: 'Basic Pants',
          type: 'PANTS',
          color: 'black',
          imageUrl: ''
        },
        {
          id: 'fallback-shoes',
          name: 'Basic Shoes',
          type: 'SHOES',
          color: 'white',
          imageUrl: ''
        }
      ],
      confidence_score: 0.5,
      reasoning: 'Fallback outfit generated due to service unavailability'
    };
  }

  /**
   * Get user-friendly error message
   */
  private getUserFriendlyMessage(error: Error): string {
    if (error.message.includes('network') || error.message.includes('fetch')) {
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    }
    
    if (error.message.includes('timeout')) {
      return 'The request is taking longer than expected. Please try again.';
    }
    
    if (error.message.includes('Validation failed')) {
      return 'There was an issue with the data you provided. Please check your input and try again.';
    }
    
    return 'Something went wrong while generating your outfit. Please try again.';
  }

  /**
   * Update metrics
   */
  private updateMetrics(success: boolean, responseTime: number): void {
    if (!this.config.enableMetrics) return;

    this.metrics.totalRequests++;
    this.metrics.lastRequestTime = Date.now();
    
    if (success) {
      this.metrics.successfulRequests++;
    } else {
      this.metrics.failedRequests++;
    }

    // Update average response time
    this.metrics.averageResponseTime = 
      (this.metrics.averageResponseTime * (this.metrics.totalRequests - 1) + responseTime) / 
      this.metrics.totalRequests;

    // Update error rate
    this.metrics.errorRate = this.metrics.failedRequests / this.metrics.totalRequests;
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get current metrics
   */
  public getMetrics(): ApiMetrics {
    return { ...this.metrics };
  }

  /**
   * Reset metrics
   */
  public resetMetrics(): void {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      errorRate: 0,
      lastRequestTime: 0
    };
  }

  /**
   * Health check endpoint
   */
  public async healthCheck(): Promise<boolean> {
    try {
      const response = await this.request({
        method: 'GET',
        endpoint: '/health/simple',
        timeout: 5000,
        retryable: false
      });
      
      return response.status === 200;
    } catch {
      return false;
    }
  }

  /**
   * Queue request for batch processing
   */
  public queueRequest<T>(request: ApiRequest): Promise<ApiResponse<T>> {
    return new Promise((resolve, reject) => {
      this.requestQueue.push(async () => {
        try {
          const response = await this.request<T>(request);
          resolve(response);
        } catch (error) {
          reject(error);
        }
      });

      this.processQueue();
    });
  }

  /**
   * Process queued requests
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessingQueue || this.requestQueue.length === 0) {
      return;
    }

    this.isProcessingQueue = true;

    while (this.requestQueue.length > 0) {
      const request = this.requestQueue.shift();
      if (request) {
        try {
          await request();
        } catch (error) {
          console.error('Queued request failed:', error);
        }
      }
    }

    this.isProcessingQueue = false;
  }
}

/**
 * Convenience function for outfit generation
 */
export async function generateOutfit(requestData: any, authToken?: string): Promise<any> {
  const client = RobustApiClient.getInstance();
  
  console.log('🔍 DEBUG: Making API call to MAIN HYBRID endpoint with converted data', `/api/outfits/generate`);
  
  try {
    return await client.request({
      method: 'POST',
      endpoint: '/api/outfits/generate',
      data: requestData,
      retryable: true,
      authToken: authToken
    });
  } catch (error: any) {
    // 🔥 FALLBACK: If Vercel proxy fails with 405, call Railway backend directly
    if (error?.status === 405 || error?.message?.includes('405') || error?.message?.includes('Method Not Allowed')) {
      console.warn('⚠️ Vercel proxy returned 405, falling back to direct Railway backend call');
      
      const railwayBackendUrl = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate';
      
      try {
        const directResponse = await fetch(railwayBackendUrl, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
        
        if (!directResponse.ok) {
          throw new Error(`Direct backend call failed: ${directResponse.status} ${directResponse.statusText}`);
        }
        
        const data = await directResponse.json();
        console.log('✅ Direct Railway backend call succeeded');
        
        return {
          data,
          status: directResponse.status,
          headers: {},
          timestamp: Date.now(),
          requestId: 'direct-fallback-' + Date.now()
        };
      } catch (directError) {
        console.error('❌ Direct backend call also failed:', directError);
        throw directError;
      }
    }
    
    // Re-throw if it's not a 405 error
    throw error;
  }
}

/**
 * Convenience function for health check
 */
export async function checkApiHealth(): Promise<boolean> {
  const client = RobustApiClient.getInstance();
  return await client.healthCheck();
}
