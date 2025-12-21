/**
 * TradingSystemAPI Client Integration
 * ====================================
 * 
 * Direct integration with TradingSystemAPI microservice
 * - MarketData API (Port 8001/market) - Real-time market data
 * - TradingFeatures API (Port 8001/trading) - Binary signals & analysis
 * 
 * Access via Nginx Gateway:
 * - /tradingsystem/market/* → TradingSystemAPI:8001/market/*
 * - /trading/* → TradingSystemAPI:8001/trading/*
 */

import axios from 'axios';

// Get base URL from environment or use default
const getBaseUrl = () => {
  // In production via Nginx, use relative paths
  if (import.meta.env.PROD) {
    return window.location.origin;
  }
  // In development, can point directly to gateway or backend
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost';
};

const BASE_URL = getBaseUrl();

// Create axios instance for TradingSystemAPI
const tradingSystemApi = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add request interceptor for logging
tradingSystemApi.interceptors.request.use(
  (config) => {
    console.log(`[TradingSystemAPI] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
tradingSystemApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('[TradingSystemAPI] Error:', error.message);
    return Promise.reject(error);
  }
);

/**
 * ============================================
 * STREAM 1: MARKET DATA API (/market/*)
 * ============================================
 * Real-time market prices and data display
 */
export const marketDataApi = {
  /**
   * Get all current market prices
   * @returns {Promise} Market prices data
   */
  async getAllPrices() {
    try {
      const response = await tradingSystemApi.get('/tradingsystem/market/prices');
      return response.data;
    } catch (error) {
      console.error('Error fetching market prices:', error);
      return { prices: {}, error: error.message };
    }
  },

  /**
   * Get price for specific symbol
   * @param {string} symbol - Symbol to get price for (e.g., 'BTC', 'EUR/USD')
   * @returns {Promise} Price data for symbol
   */
  async getPriceForSymbol(symbol) {
    try {
      const response = await tradingSystemApi.get(`/tradingsystem/market/prices/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching price for ${symbol}:`, error);
      return { error: error.message };
    }
  },

  /**
   * Get prices by asset class
   * @param {string} assetClass - Asset class (CRYPTO, FOREX, METALS)
   * @returns {Promise} Prices for asset class
   */
  async getPricesByAssetClass(assetClass) {
    try {
      const response = await tradingSystemApi.get(`/tradingsystem/market/prices/asset/${assetClass}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching prices for ${assetClass}:`, error);
      return { prices: {}, error: error.message };
    }
  },

  /**
   * Get market overview
   * @returns {Promise} Market overview statistics
   */
  async getMarketOverview() {
    try {
      const response = await tradingSystemApi.get('/tradingsystem/market/overview');
      return response.data;
    } catch (error) {
      console.error('Error fetching market overview:', error);
      return { error: error.message };
    }
  },

  /**
   * Get complete market summary
   * @returns {Promise} Complete market summary with all data
   */
  async getMarketSummary() {
    try {
      const response = await tradingSystemApi.get('/tradingsystem/market/summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching market summary:', error);
      return { error: error.message };
    }
  },

  /**
   * Get supported symbols list
   * @returns {Promise} List of supported symbols
   */
  async getSupportedSymbols() {
    try {
      const response = await tradingSystemApi.get('/tradingsystem/market/supported-symbols');
      return response.data;
    } catch (error) {
      console.error('Error fetching supported symbols:', error);
      return { symbols: [], error: error.message };
    }
  },

  /**
   * Health check for MarketData API
   * @returns {Promise} Health status
   */
  async healthCheck() {
    try {
      const response = await tradingSystemApi.get('/tradingsystem/market/health');
      return response.data;
    } catch (error) {
      console.error('Market API health check failed:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }
};

/**
 * ============================================
 * STREAM 2: TRADING FEATURES API (/trading/*)
 * ============================================
 * Binary trading signals and analysis
 */
export const tradingFeaturesApi = {
  /**
   * Get all trading signals
   * @returns {Promise} All trading signals
   */
  async getAllSignals() {
    try {
      const response = await tradingSystemApi.get('/trading/signals');
      return response.data;
    } catch (error) {
      console.error('Error fetching trading signals:', error);
      return { signals: {}, error: error.message };
    }
  },

  /**
   * Get signal for specific symbol
   * @param {string} symbol - Symbol to get signal for
   * @returns {Promise} Trading signal for symbol
   */
  async getSignalForSymbol(symbol) {
    try {
      const response = await tradingSystemApi.get(`/trading/signals/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching signal for ${symbol}:`, error);
      return { error: error.message };
    }
  },

  /**
   * Get signals by asset class
   * @param {string} assetClass - Asset class filter
   * @returns {Promise} Signals for asset class
   */
  async getSignalsByAssetClass(assetClass) {
    try {
      const response = await tradingSystemApi.get(`/trading/signals/asset/${assetClass}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching signals for ${assetClass}:`, error);
      return { signals: {}, error: error.message };
    }
  },

  /**
   * Get binary signals array
   * Binary format: 1 = BULLISH (UP/BUY), 0 = BEARISH (DOWN/SELL)
   * @returns {Promise} Binary signals array
   */
  async getBinaryArray() {
    try {
      const response = await tradingSystemApi.get('/trading/binary');
      return response.data;
    } catch (error) {
      console.error('Error fetching binary array:', error);
      return { 
        binary_array: [], 
        binary_string: '',
        market_sentiment: 'UNKNOWN',
        error: error.message 
      };
    }
  },

  /**
   * Get binary signal for specific symbol
   * @param {string} symbol - Symbol to get binary for
   * @returns {Promise} Binary signal for symbol
   */
  async getBinaryForSymbol(symbol) {
    try {
      const response = await tradingSystemApi.get(`/trading/binary/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching binary for ${symbol}:`, error);
      return { binary_code: '0', error: error.message };
    }
  },

  /**
   * Get binary stream (real-time)
   * @returns {Promise} Binary stream data
   */
  async getBinaryStream() {
    try {
      const response = await tradingSystemApi.get('/trading/binary/stream');
      return response.data;
    } catch (error) {
      console.error('Error fetching binary stream:', error);
      return { stream: [], error: error.message };
    }
  },

  /**
   * Get comprehensive market analysis
   * @returns {Promise} Market analysis data
   */
  async getMarketAnalysis() {
    try {
      const response = await tradingSystemApi.get('/trading/analysis');
      return response.data;
    } catch (error) {
      console.error('Error fetching market analysis:', error);
      return { 
        asset_class_analysis: {},
        top_gainers: [],
        top_losers: [],
        error: error.message 
      };
    }
  },

  /**
   * Get trend analysis
   * @returns {Promise} Trend analysis data
   */
  async getTrendAnalysis() {
    try {
      const response = await tradingSystemApi.get('/trading/analysis/trends');
      return response.data;
    } catch (error) {
      console.error('Error fetching trend analysis:', error);
      return { trends: {}, error: error.message };
    }
  },

  /**
   * Get trading recommendations
   * @returns {Promise} Trading recommendations
   */
  async getRecommendations() {
    try {
      const response = await tradingSystemApi.get('/trading/recommendations');
      return response.data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return { 
        recommendations: {},
        summary: {},
        error: error.message 
      };
    }
  },

  /**
   * Get signal performance metrics
   * @returns {Promise} Performance metrics
   */
  async getPerformanceMetrics() {
    try {
      const response = await tradingSystemApi.get('/trading/performance');
      return response.data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      return { metrics: {}, error: error.message };
    }
  },

  /**
   * Health check for TradingFeatures API
   * @returns {Promise} Health status
   */
  async healthCheck() {
    try {
      const response = await tradingSystemApi.get('/trading/health');
      return response.data;
    } catch (error) {
      console.error('Trading API health check failed:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }
};

/**
 * Combined API exports for convenience
 */
export default {
  market: marketDataApi,
  trading: tradingFeaturesApi,
  
  /**
   * Check health of both APIs
   */
  async healthCheck() {
    const [marketHealth, tradingHealth] = await Promise.all([
      marketDataApi.healthCheck(),
      tradingFeaturesApi.healthCheck()
    ]);
    
    return {
      market: marketHealth,
      trading: tradingHealth,
      overall: (marketHealth.status !== 'unhealthy' && tradingHealth.status !== 'unhealthy') 
        ? 'healthy' 
        : 'degraded'
    };
  }
};
