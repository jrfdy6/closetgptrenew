import { NextResponse } from 'next/server';

// 🔥 ENHANCEMENT #2: Health check endpoint to verify backend connectivity
export async function GET() {
  const startTime = Date.now();
  
  try {
    console.log('🏥 PROFILE HEALTH: Checking backend connectivity...');
    
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
    
    // Check main backend health
    const healthUrl = `${backendUrl}/health`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout
    
    try {
      const healthResponse = await fetch(healthUrl, {
        method: 'GET',
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      const healthDuration = Date.now() - startTime;
      
      const healthData = await healthResponse.json();
      
      // Check auth endpoint (without requiring authentication)
      const authHealthUrl = `${backendUrl}/api/auth/profile/health`;
      const authHealthStart = Date.now();
      
      let authHealthStatus = 'unknown';
      try {
        const authHealthResponse = await fetch(authHealthUrl, {
          method: 'GET',
          signal: controller.signal,
        });
        authHealthStatus = authHealthResponse.ok ? 'healthy' : `error_${authHealthResponse.status}`;
      } catch (e) {
        authHealthStatus = 'unreachable';
      }
      
      const authHealthDuration = Date.now() - authHealthStart;
      
      console.log('🏥 PROFILE HEALTH: Health check complete', {
        backend: healthResponse.ok ? 'healthy' : 'unhealthy',
        backendDuration: `${healthDuration}ms`,
        auth: authHealthStatus,
        authDuration: `${authHealthDuration}ms`
      });
      
      return NextResponse.json({
        status: 'ok',
        backend: {
          reachable: healthResponse.ok,
          status: healthResponse.status,
          message: healthData.message || healthData.status,
          duration: `${healthDuration}ms`
        },
        authEndpoint: {
          status: authHealthStatus,
          duration: `${authHealthDuration}ms`
        },
        proxy: {
          status: 'healthy',
          cacheEnabled: true,
          retryEnabled: true
        },
        timestamp: new Date().toISOString(),
        totalDuration: `${Date.now() - startTime}ms`
      });
      
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      const duration = Date.now() - startTime;
      
      console.error('🏥 PROFILE HEALTH: Backend unreachable', {
        error: fetchError.message,
        isTimeout: fetchError.name === 'AbortError',
        duration: `${duration}ms`
      });
      
      return NextResponse.json({
        status: 'error',
        backend: {
          reachable: false,
          error: fetchError.name === 'AbortError' ? 'timeout' : fetchError.message,
          duration: `${duration}ms`
        },
        proxy: {
          status: 'healthy',
          cacheEnabled: true,
          retryEnabled: true
        },
        timestamp: new Date().toISOString(),
        totalDuration: `${duration}ms`
      }, { status: 503 });
    }
    
  } catch (error) {
    const duration = Date.now() - startTime;
    
    console.error('🏥 PROFILE HEALTH: Unexpected error:', error);
    
    return NextResponse.json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
      duration: `${duration}ms`,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}

