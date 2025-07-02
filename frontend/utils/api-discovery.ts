/**
 * Enhanced Dynamic API Endpoint Discovery System
 * Automatically discovers and manages API endpoints with robust error handling
 */

interface EndpointConfig {
  baseUrl: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  fallbacks?: string[];
  cache?: boolean;
  timeout?: number;
}

interface DiscoveredEndpoint {
  url: string;
  available: boolean;
  responseTime: number;
  lastChecked: Date;
  errorCount: number;
  successCount: number;
}

class APIDiscovery {
  private static instance: APIDiscovery;
  private endpoints: Map<string, DiscoveredEndpoint> = new Map();
  
  // Extensive base URL fallbacks - try many different ports and configurations
  private baseUrls = [
    // Primary backends
    'http://localhost:8000',
    'http://localhost:8001', 
    'http://localhost:8002',
    'http://localhost:8003',
    'http://localhost:3001',  // Next.js might proxy
    
    // IP address fallbacks
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8001',
    'http://127.0.0.1:8002',
    'http://127.0.0.1:8003',
    
    // Alternative localhost notation
    'http://localhost.localdomain:8000',
    'http://localhost.localdomain:8001',
    
    // Development server alternatives
    'http://0.0.0.0:8000',
    'http://0.0.0.0:8001',
    
    // Network interface alternatives (if running on different interface)
    'http://192.168.1.100:8000',  // Common local IP range
    'http://10.0.0.100:8000',     // Another common range
  ];
  
  private endpointPatterns = {
    // Core system endpoints
    health: '/health',
    root: '/',
    systemStatus: '/api/system/status',
    moduleMetrics: '/api/system/module-metrics',
    
    // Trading endpoints with multiple path variations
    accountInfo: '/api/v1/trading/account_info',
    accountInfoAlt: '/api/trading/account_info',
    accountInfoSimple: '/account_info',
    
    positions: '/api/v1/trading/positions',
    positionsAlt: '/api/trading/positions',
    positionsSimple: '/positions',
    
    placeOrder: '/api/v1/trading/place_order',
    placeOrderAlt: '/api/trading/place_order',
    
    closePosition: '/api/v1/trading/close_position',
    tradeHistory: '/api/v1/trading/history',
    tradeHistoryAlt: '/api/trading/history',
    
    // Market data endpoints  
    marketTick: '/api/v1/market/tick/:symbol',
    marketTickAlt: '/api/market/tick/:symbol',
    marketStatus: '/api/v1/market/status',
    marketData: '/api/v1/market/data',
    
    // Performance endpoints with fallbacks
    performanceSummary: '/api/v1/performance/performance_summary',
    performanceSummaryAlt: '/api/performance/summary',
    performanceSummarySimple: '/performance_summary',
    
    equityCurve: '/api/v1/performance/equity_curve',
    equityCurveAlt: '/api/performance/equity_curve',
    
    statistics: '/api/v1/performance/statistics',
    statisticsAlt: '/api/performance/statistics',
    
    // God Mode endpoints
    godModeStatus: '/api/v1/god-mode/status',
    godModeActivate: '/api/v1/god-mode/activate',
    godModeDeactivate: '/api/v1/god-mode/deactivate',
    godModePredictions: '/api/v1/god-mode/predictions',
    
    // Shadow mode endpoints
    shadowActivity: '/api/v1/shadow/activity',
    shadowAlerts: '/api/v1/shadow/alerts',
    shadowWhales: '/api/v1/shadow/whales',
    shadowStatus: '/api/v1/shadow-mode/status',
    
    // Strategy Whisperer endpoints
    strategyGenerate: '/api/v1/strategy-whisperer/generate',
    strategyBacktest: '/api/v1/strategy-whisperer/backtest',
    strategyDeploy: '/api/v1/strategy-whisperer/deploy',
    
    // Adaptive Trade Manager endpoints
    atmStatus: '/api/v1/adaptive-trade-manager/status',
    atmOptimize: '/api/v1/adaptive-trade-manager/optimize',
    atmRisk: '/api/v1/adaptive-trade-manager/risk',
    
    // Market narrator endpoints
    marketNarratorStatus: '/api/v1/market-narrator/status',
    marketNarratorStories: '/api/v1/market-narrator/stories',
    marketNarratorGenerate: '/api/v1/market-narrator/generate-story',
    marketNarratorSentiment: '/api/v1/market-narrator/sentiment-analysis',
    marketNarratorInfluence: '/api/v1/market-narrator/influence-map',
    marketNarratorCorrelations: '/api/v1/market-narrator/correlations',
    marketNarratorPulse: '/api/v1/market-narrator/market-pulse',
    
    // MT5 connection endpoints
    mt5Status: '/api/v1/mt5/status',
    mt5Connect: '/api/v1/mt5/connect',
    mt5ConnectionStatus: '/api/v1/mt5/connection_status',
    
    // Quantum dashboard
    quantumDashboard: '/api/v1/quantum/dashboard',
    quantumMetrics: '/api/v1/quantum/metrics',
  };

  // Configuration for robust connections
  private config = {
    connectionTimeout: 10000,     // 10 seconds
    requestTimeout: 15000,        // 15 seconds
    maxRetries: 3,                // Maximum retry attempts
    retryDelay: 1000,             // 1 second between retries
    discoveryInterval: 15000,     // Re-discover every 15 seconds
    healthCheckInterval: 5000,    // Health check every 5 seconds
    maxErrorCount: 10,            // Mark as bad after 10 consecutive errors
  };

  private constructor() {
    this.discoverEndpoints();
    
    // More frequent re-discovery for better reliability
    setInterval(() => this.discoverEndpoints(), this.config.discoveryInterval);
    
    // Continuous health monitoring
    setInterval(() => this.healthCheck(), this.config.healthCheckInterval);
  }

  static getInstance(): APIDiscovery {
    if (!APIDiscovery.instance) {
      APIDiscovery.instance = new APIDiscovery();
    }
    return APIDiscovery.instance;
  }

  private async checkEndpoint(baseUrl: string, path: string, timeout = 5000): Promise<DiscoveredEndpoint> {
    const url = `${baseUrl}${path}`;
    const startTime = Date.now();
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Cache-Control': 'no-cache'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      const responseTime = Date.now() - startTime;
      
      // Consider both 200 and 404 as "available" - API might exist but endpoint might not
      const available = response.status < 500;
      
      return {
        url,
        available,
        responseTime,
        lastChecked: new Date(),
        errorCount: available ? 0 : 1,
        successCount: available ? 1 : 0
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;
      return {
        url,
        available: false,
        responseTime,
        lastChecked: new Date(),
        errorCount: 1,
        successCount: 0
      };
    }
  }

  private async discoverEndpoints() {
    console.log('[API Discovery] Starting comprehensive endpoint discovery...');
    
    // Find all active base URLs
    const activeBaseUrls: string[] = [];
    
    for (const baseUrl of this.baseUrls) {
      try {
        // Try both health and root endpoints to maximize detection
        const health = await this.checkEndpoint(baseUrl, '/health', 3000);
        const root = await this.checkEndpoint(baseUrl, '/', 3000);
        
        if (health.available || root.available) {
          activeBaseUrls.push(baseUrl);
          console.log(`[API Discovery] ✓ Active server found at ${baseUrl}`);
        }
      } catch (error) {
        // Silent fail - we'll try other URLs
      }
    }

    if (activeBaseUrls.length === 0) {
      console.error('[API Discovery] No active API servers found! Trying backup discovery...');
      await this.backupDiscovery();
      return;
    }

    console.log(`[API Discovery] Found ${activeBaseUrls.length} active servers`);

    // Check all endpoints on all active servers
    for (const [key, path] of Object.entries(this.endpointPatterns)) {
      let bestEndpoint: DiscoveredEndpoint | null = null;
      
      for (const baseUrl of activeBaseUrls) {
        const endpoint = await this.checkEndpoint(baseUrl, path, 5000);
        
        if (endpoint.available && (!bestEndpoint || endpoint.responseTime < bestEndpoint.responseTime)) {
          bestEndpoint = endpoint;
        }
      }
      
      if (bestEndpoint) {
        // Merge with existing endpoint data if available
        const existing = this.endpoints.get(key);
        if (existing) {
          bestEndpoint.errorCount = existing.errorCount;
          bestEndpoint.successCount = existing.successCount + 1;
        }
        
        this.endpoints.set(key, bestEndpoint);
        console.log(`[API Discovery] ✓ ${key}: ${bestEndpoint.url} (${bestEndpoint.responseTime}ms)`);
      } else {
        // Mark as unavailable but keep trying
        const existing = this.endpoints.get(key);
        if (existing) {
          existing.available = false;
          existing.errorCount++;
          existing.lastChecked = new Date();
        }
        console.log(`[API Discovery] ✗ ${key}: unavailable on all servers`);
      }
    }
  }

  private async backupDiscovery() {
    console.log('[API Discovery] Running backup discovery on extended port range...');
    
    // Try even more ports as backup
    const backupPorts = [3000, 4000, 5000, 8080, 8888, 9000];
    for (const port of backupPorts) {
      const baseUrl = `http://localhost:${port}`;
      try {
        const health = await this.checkEndpoint(baseUrl, '/', 2000);
        if (health.available) {
          console.log(`[API Discovery] Backup server found at ${baseUrl}`);
          this.baseUrls.unshift(baseUrl); // Add to beginning of list
          break;
        }
      } catch (error) {
        // Continue trying
      }
    }
  }

  private async healthCheck() {
    // Continuously monitor health of known endpoints
    for (const [key, endpoint] of this.endpoints.entries()) {
      if (endpoint.available && Math.random() < 0.1) { // Random 10% check
        try {
          const healthCheck = await this.checkEndpoint(
            endpoint.url.split('/api')[0], 
            '/health', 
            2000
          );
          
          if (!healthCheck.available) {
            endpoint.errorCount++;
            if (endpoint.errorCount > this.config.maxErrorCount) {
              endpoint.available = false;
              console.warn(`[API Discovery] Endpoint ${key} marked as unavailable due to errors`);
            }
          } else {
            endpoint.errorCount = Math.max(0, endpoint.errorCount - 1);
            endpoint.successCount++;
          }
        } catch (error) {
          // Silent health check failure
        }
      }
    }
  }

  getEndpoint(key: string, params?: Record<string, string>): string | null {
    const endpoint = this.endpoints.get(key);
    if (!endpoint || !endpoint.available) {
      // Try alternative endpoint names
      const alternatives = this.getAlternativeEndpoints(key);
      for (const alt of alternatives) {
        const altEndpoint = this.endpoints.get(alt);
        if (altEndpoint && altEndpoint.available) {
          console.log(`[API Discovery] Using alternative endpoint ${alt} for ${key}`);
          return this.buildUrl(altEndpoint.url, params);
        }
      }
      
      console.warn(`[API Discovery] Endpoint ${key} not available, alternatives also failed`);
      return null;
    }

    return this.buildUrl(endpoint.url, params);
  }

  private getAlternativeEndpoints(key: string): string[] {
    // Map endpoints to their alternatives
    const alternatives: Record<string, string[]> = {
      'accountInfo': ['accountInfoAlt', 'accountInfoSimple'],
      'positions': ['positionsAlt', 'positionsSimple'],
      'performanceSummary': ['performanceSummaryAlt', 'performanceSummarySimple'],
      'equityCurve': ['equityCurveAlt'],
      'statistics': ['statisticsAlt'],
      'tradeHistory': ['tradeHistoryAlt'],
      'placeOrder': ['placeOrderAlt']
    };
    
    return alternatives[key] || [];
  }

  private buildUrl(url: string, params?: Record<string, string>): string {
    let finalUrl = url;
    
    // Replace path parameters
    if (params) {
      Object.entries(params).forEach(([param, value]) => {
        finalUrl = finalUrl.replace(`:${param}`, encodeURIComponent(value));
      });
    }

    return finalUrl;
  }

  async request<T = any>(
    key: string,
    options: RequestInit = {},
    params?: Record<string, string>
  ): Promise<T> {
    let lastError: Error | null = null;
    
    // Retry logic with exponential backoff
    for (let attempt = 0; attempt < this.config.maxRetries; attempt++) {
      try {
        const url = this.getEndpoint(key, params);
        
        if (!url) {
          // Force re-discovery and try again
          console.log(`[API Discovery] Endpoint ${key} not found, forcing re-discovery...`);
          await this.discoverEndpoints();
          
          const retryUrl = this.getEndpoint(key, params);
          if (!retryUrl) {
            throw new Error(`Endpoint ${key} not available after re-discovery`);
          }
          
          return await this.performRequest<T>(retryUrl, options);
        }

        return await this.performRequest<T>(url, options);
        
      } catch (error) {
        lastError = error as Error;
        console.warn(`[API Discovery] Request attempt ${attempt + 1} failed for ${key}:`, error);
        
        if (attempt < this.config.maxRetries - 1) {
          // Exponential backoff: 1s, 2s, 4s
          const delay = this.config.retryDelay * Math.pow(2, attempt);
          console.log(`[API Discovery] Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError || new Error(`All retry attempts failed for endpoint ${key}`);
  }

  private async performRequest<T>(url: string, options: RequestInit): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.requestTimeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
          ...options.headers
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} for ${url}`);
      }

      // Handle both JSON and text responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        try {
          return JSON.parse(text);
        } catch {
          // Return as-is if not JSON
          return text as any;
        }
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error(`[API Discovery] Request failed for ${url}:`, error);
      throw error;
    }
  }

  // Helper methods for common requests with enhanced error handling
  async get<T = any>(key: string, params?: Record<string, string>): Promise<T> {
    return this.request<T>(key, { method: 'GET' }, params);
  }

  async post<T = any>(key: string, data: any, params?: Record<string, string>): Promise<T> {
    return this.request<T>(
      key,
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      params
    );
  }

  async put<T = any>(key: string, data: any, params?: Record<string, string>): Promise<T> {
    return this.request<T>(
      key,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      params
    );
  }

  async delete<T = any>(key: string, params?: Record<string, string>): Promise<T> {
    return this.request<T>(key, { method: 'DELETE' }, params);
  }

  // Get comprehensive status of all endpoints
  getStatus(): Record<string, DiscoveredEndpoint & { reliability: number }> {
    const status: Record<string, DiscoveredEndpoint & { reliability: number }> = {};
    this.endpoints.forEach((endpoint, key) => {
      const total = endpoint.successCount + endpoint.errorCount;
      const reliability = total > 0 ? endpoint.successCount / total : 0;
      
      status[key] = {
        ...endpoint,
        reliability
      };
    });
    return status;
  }

  // Force immediate re-discovery
  async forceDiscovery(): Promise<void> {
    console.log('[API Discovery] Forcing immediate endpoint discovery...');
    await this.discoverEndpoints();
  }

  // Get connection health summary
  getHealthSummary(): {
    totalEndpoints: number;
    availableEndpoints: number;
    avgResponseTime: number;
    overallHealth: 'excellent' | 'good' | 'poor' | 'critical';
  } {
    const endpoints = Array.from(this.endpoints.values());
    const available = endpoints.filter(e => e.available);
    const avgResponseTime = available.length > 0 
      ? available.reduce((sum, e) => sum + e.responseTime, 0) / available.length 
      : -1;
    
    const healthRatio = endpoints.length > 0 ? available.length / endpoints.length : 0;
    
    let overallHealth: 'excellent' | 'good' | 'poor' | 'critical';
    if (healthRatio >= 0.9) overallHealth = 'excellent';
    else if (healthRatio >= 0.7) overallHealth = 'good';
    else if (healthRatio >= 0.4) overallHealth = 'poor';
    else overallHealth = 'critical';
    
    return {
      totalEndpoints: endpoints.length,
      availableEndpoints: available.length,
      avgResponseTime,
      overallHealth
    };
  }
}

// Export singleton instance
export const apiDiscovery = APIDiscovery.getInstance();

// Export enhanced helper functions with built-in error handling
export const api = {
  get: async <T = any>(key: string, params?: Record<string, string>) => {
    try {
      return await apiDiscovery.get<T>(key, params);
    } catch (error) {
      console.error(`[API] GET ${key} failed:`, error);
      throw error;
    }
  },
  
  post: async <T = any>(key: string, data: any, params?: Record<string, string>) => {
    try {
      return await apiDiscovery.post<T>(key, data, params);
    } catch (error) {
      console.error(`[API] POST ${key} failed:`, error);
      throw error;
    }
  },
  
  put: async <T = any>(key: string, data: any, params?: Record<string, string>) => {
    try {
      return await apiDiscovery.put<T>(key, data, params);
    } catch (error) {
      console.error(`[API] PUT ${key} failed:`, error);
      throw error;
    }
  },
  
  delete: async <T = any>(key: string, params?: Record<string, string>) => {
    try {
      return await apiDiscovery.delete<T>(key, params);
    } catch (error) {
      console.error(`[API] DELETE ${key} failed:`, error);
      throw error;
    }
  },
  
  status: () => apiDiscovery.getStatus(),
  health: () => apiDiscovery.getHealthSummary(),
  forceDiscovery: () => apiDiscovery.forceDiscovery()
}; 