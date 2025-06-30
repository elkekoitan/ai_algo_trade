/**
 * API service for ICT Ultra v2
 * Handles all backend communication with proper error handling
 */

import axios from 'axios';

// Define response type
export interface ApiResponse<T = any> {
  error: boolean;
  status?: number;
  message?: string;
  data: T | null;
}

// Base API configuration
const api = axios.create({
  baseURL: 'http://localhost:8002',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler
const handleError = (error: any): ApiResponse => {
  console.error('API Error:', error);
  
  if (error.response) {
    // Server responded with an error status code
    return {
      error: true,
      status: error.response.status,
      message: error.response.data?.detail || 'Server error',
      data: null
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      error: true,
      status: 0,
      message: 'No response from server. Check your connection.',
      data: null
    };
  } else {
    // Something else caused the error
    return {
      error: true,
      status: 0,
      message: error.message || 'Unknown error',
      data: null
    };
  }
};

// API endpoints
export const ApiService = {
  // Health and status
  async getHealth(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/health');
      return { error: false, data: response.data, message: 'Success' };
    } catch (error) {
      return handleError(error);
    }
  },

  // Account information
  async getAccountInfo(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/trading/account_info');
      return { error: false, data: response.data, message: 'Success' };
    } catch (error) {
      return handleError(error);
    }
  },

  // Trading
  async getPositions(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/trading/positions');
      return { error: false, data: response.data, message: 'Positions fetched' };
    } catch (error) {
      return handleError(error);
    }
  },

  async placeOrder(orderData: any): Promise<ApiResponse> {
    try {
      const response = await api.post('/api/v1/trading/place_order', orderData);
      return { error: false, data: response.data, message: response.data.message || 'Order request processed' };
    } catch (error) {
      return handleError(error);
    }
  },

  async closePosition(ticket: number): Promise<ApiResponse> {
    try {
      const response = await api.post(`/api/v1/trading/close_position/${ticket}`);
      return { error: false, data: response.data, message: response.data.message || 'Close request processed' };
    } catch (error) {
      return handleError(error);
    }
  },

  // Market data
  async getSymbols(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/market/symbols');
      return { error: false, data: response.data?.symbols || [], message: 'Symbols fetched' };
    } catch (error) {
      return handleError(error);
    }
  },

  async getSymbolTick(symbol: string): Promise<ApiResponse> {
    try {
      const response = await api.get(`/api/v1/market/tick/${symbol}`);
      return { error: false, data: response.data, message: `Tick for ${symbol} fetched` };
    } catch (error) {
      return handleError(error);
    }
  },

  async getCandles(symbol: string, timeframe: string = 'H1', count: number = 100): Promise<ApiResponse> {
    try {
      const response = await api.get(`/api/v1/market/candles/${symbol}`, {
        params: { timeframe, count }
      });
      return { error: false, data: response.data, message: 'Candles fetched' };
    } catch (error) {
      return handleError(error);
    }
  },

  // ICT Signals
  async getIctSignals(params: { limit?: number, symbol?: string, timeframe?: string } = {}): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/signals/ict', { params });
      return { error: false, data: response.data, message: 'Success' };
    } catch (error) {
      return handleError(error);
    }
  },

  // Auto Trader
  async getAutoTraderStatus(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/auto-trader/status');
      return { error: false, data: response.data, message: 'Success' };
    } catch (error) {
      return handleError(error);
    }
  },

  // Scanner
  async getScannerOverview(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/scanner/overview');
      return { error: false, data: response.data, message: 'Success' };
    } catch (error) {
      return handleError(error);
    }
  },

  async getScannerOpportunities(params: any = {}): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/v1/scanner/opportunities', { params });
      return { error: false, data: response.data, message: 'Success' };
    } catch (error) {
      return handleError(error);
    }
  },
};

export default ApiService;

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8002';

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  account: `${API_BASE_URL}/api/v1/trading/account_info`,
  positions: `${API_BASE_URL}/api/v1/trading/positions`,
  history: `${API_BASE_URL}/api/v1/trading/history`,
  prices: `${API_BASE_URL}/api/v1/market_data/prices`,
  symbols: `${API_BASE_URL}/api/v1/market_data/symbols`,
  symbols_active: `${API_BASE_URL}/api/v1/market_data/symbols/active`,
  symbols_crypto: `${API_BASE_URL}/api/v1/market_data/symbols/crypto`,
  status: `${API_BASE_URL}/api/v1/market_data/status`,
  trade: `${API_BASE_URL}/api/v1/trading/trade`,
  signals: `${API_BASE_URL}/api/v1/signals`,
  performance: `${API_BASE_URL}/api/v1/performance/performance_summary`,
  equity_curve: `${API_BASE_URL}/api/v1/performance/equity_curve`,
}; 