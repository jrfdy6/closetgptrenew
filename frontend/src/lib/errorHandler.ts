/**
 * Enterprise-grade error handling and recovery system
 * Provides comprehensive error management, logging, and user-friendly fallbacks
 */

export interface ErrorContext {
  operation: string;
  component?: string;
  userId?: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface ErrorRecoveryOptions {
  retryable: boolean;
  maxRetries: number;
  retryDelay: number;
  fallbackAction?: () => Promise<any>;
  userMessage: string;
}

export class RobustError extends Error {
  public readonly code: string;
  public readonly context: ErrorContext;
  public readonly recovery: ErrorRecoveryOptions;
  public readonly timestamp: number;
  public readonly severity: 'low' | 'medium' | 'high' | 'critical';

  constructor(
    message: string,
    code: string,
    context: ErrorContext,
    recovery: ErrorRecoveryOptions,
    severity: 'low' | 'medium' | 'high' | 'critical' = 'medium'
  ) {
    super(message);
    this.name = 'RobustError';
    this.code = code;
    this.context = context;
    this.recovery = recovery;
    this.timestamp = Date.now();
    this.severity = severity;
  }
}

export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLog: Array<RobustError> = [];
  private maxLogSize = 1000;

  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  /**
   * Handle errors with comprehensive logging and recovery
   */
  public async handleError(
    error: Error | RobustError,
    context: ErrorContext,
    recoveryOptions?: Partial<ErrorRecoveryOptions>
  ): Promise<any> {
    const robustError = this.wrapError(error, context, recoveryOptions);
    
    // Log the error
    this.logError(robustError);
    
    // Report to monitoring service
    await this.reportError(robustError);
    
    // Attempt recovery if configured
    if (robustError.recovery.retryable && robustError.recovery.fallbackAction) {
      return await this.attemptRecovery(robustError);
    }
    
    throw robustError;
  }

  /**
   * Wrap any error in our robust error format
   */
  private wrapError(
    error: Error | RobustError,
    context: ErrorContext,
    recoveryOptions?: Partial<ErrorRecoveryOptions>
  ): RobustError {
    if (error instanceof RobustError) {
      return error;
    }

    const defaultRecovery: ErrorRecoveryOptions = {
      retryable: false,
      maxRetries: 0,
      retryDelay: 1000,
      userMessage: 'Something went wrong. Please try again.',
      ...recoveryOptions
    };

    const severity = this.determineSeverity(error, context);
    const code = this.generateErrorCode(error, context);

    return new RobustError(
      error.message,
      code,
      context,
      defaultRecovery,
      severity
    );
  }

  /**
   * Determine error severity based on context and error type
   */
  private determineSeverity(error: Error, context: ErrorContext): 'low' | 'medium' | 'high' | 'critical' {
    // Critical: Authentication, payment, data loss
    if (context.operation.includes('auth') || context.operation.includes('payment')) {
      return 'critical';
    }

    // High: API failures, network issues
    if (error.message.includes('network') || error.message.includes('API') || error.message.includes('fetch')) {
      return 'high';
    }

    // Medium: Validation errors, user input issues
    if (error.message.includes('validation') || error.message.includes('invalid')) {
      return 'medium';
    }

    // Low: UI issues, minor bugs
    return 'low';
  }

  /**
   * Generate standardized error codes
   */
  private generateErrorCode(error: Error, context: ErrorContext): string {
    const operation = context.operation.toUpperCase().replace(/[^A-Z0-9]/g, '_');
    const errorType = error.name.toUpperCase().replace(/[^A-Z0-9]/g, '_');
    return `${operation}_${errorType}`;
  }

  /**
   * Log error with structured data
   */
  private logError(error: RobustError): void {
    const logEntry = {
      timestamp: error.timestamp,
      code: error.code,
      message: error.message,
      severity: error.severity,
      context: error.context,
      stack: error.stack,
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    console.error('🚨 RobustError:', logEntry);
    
    // Store in memory log
    this.errorLog.push(error);
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog.shift();
    }

    // Send to external logging service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToLoggingService(logEntry);
    }
  }

  /**
   * Report error to monitoring service
   */
  private async reportError(error: RobustError): Promise<void> {
    try {
      // In production, send to monitoring service (Sentry, LogRocket, etc.)
      if (process.env.NODE_ENV === 'production') {
        await fetch('/api/errors/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code: error.code,
            message: error.message,
            severity: error.severity,
            context: error.context,
            timestamp: error.timestamp
          })
        });
      }
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }

  /**
   * Attempt error recovery
   */
  private async attemptRecovery(error: RobustError): Promise<any> {
    if (!error.recovery.fallbackAction) {
      throw error;
    }

    try {
      return await error.recovery.fallbackAction();
    } catch (recoveryError) {
      console.error('Recovery failed:', recoveryError);
      throw error; // Throw original error if recovery fails
    }
  }

  /**
   * Send to external logging service
   */
  private sendToLoggingService(logEntry: any): void {
    // Implement integration with logging service
    // This could be Sentry, LogRocket, DataDog, etc.
    console.log('📊 Logging to external service:', logEntry);
  }

  /**
   * Get error statistics
   */
  public getErrorStats(): any {
    const stats = {
      total: this.errorLog.length,
      bySeverity: {
        critical: this.errorLog.filter(e => e.severity === 'critical').length,
        high: this.errorLog.filter(e => e.severity === 'high').length,
        medium: this.errorLog.filter(e => e.severity === 'medium').length,
        low: this.errorLog.filter(e => e.severity === 'low').length
      },
      byOperation: {},
      recent: this.errorLog.slice(-10)
    };

    // Group by operation
    this.errorLog.forEach(error => {
      const operation = error.context.operation;
      stats.byOperation[operation] = (stats.byOperation[operation] || 0) + 1;
    });

    return stats;
  }
}

/**
 * Convenience function for handling errors
 */
export async function handleError(
  error: Error,
  operation: string,
  options?: {
    component?: string;
    userId?: string;
    retryable?: boolean;
    fallbackAction?: () => Promise<any>;
    userMessage?: string;
  }
): Promise<any> {
  const handler = ErrorHandler.getInstance();
  const context: ErrorContext = {
    operation,
    component: options?.component,
    userId: options?.userId,
    timestamp: Date.now()
  };

  return await handler.handleError(error, context, {
    retryable: options?.retryable || false,
    maxRetries: 3,
    retryDelay: 1000,
    fallbackAction: options?.fallbackAction,
    userMessage: options?.userMessage || 'Something went wrong. Please try again.'
  });
}

/**
 * Retry mechanism with exponential backoff
 */
export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxRetries) {
        throw lastError;
      }

      const delay = baseDelay * Math.pow(2, attempt);
      console.log(`🔄 Retry attempt ${attempt + 1}/${maxRetries + 1} in ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
}

/**
 * Circuit breaker pattern
 */
export class CircuitBreaker {
  private failures: number = 0;
  private lastFailureTime: number = 0;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  constructor(
    private threshold: number = 5,
    private timeout: number = 60000,
    private resetTimeout: number = 30000
  ) {}

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() - this.lastFailureTime > this.resetTimeout) {
        this.state = 'half-open';
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    this.state = 'closed';
  }

  private onFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();
    
    if (this.failures >= this.threshold) {
      this.state = 'open';
    }
  }
}
