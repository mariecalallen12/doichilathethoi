import axios from 'axios';
import { getApiBaseUrl } from '../../utils/runtimeConfig';
import { marketDataApi } from './tradingSystem';

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const marketApi = {
  /**
   * Get market prices - Uses TradingSystemAPI MarketData
   * @param {Array} symbols - Array of symbols (optional, gets all if empty)
   * @returns {Promise} Market prices data
   */
  async getPrices(symbols = []) {
    try {
      // Use TradingSystemAPI MarketData endpoint
      const response = await marketDataApi.getAllPrices();
      
      // Filter by symbols if requested
      if (symbols.length > 0 && response.data?.prices) {
        const filteredPrices = {};
        symbols.forEach(symbol => {
          if (response.data.prices[symbol]) {
            filteredPrices[symbol] = response.data.prices[symbol];
          }
        });
        return {
          ...response.data,
          prices: filteredPrices
        };
      }
      
      return response.data || response;
    } catch (error) {
      // Return empty prices instead of throwing to prevent crash
      console.warn('Market prices API error:', error.message);
      return {
        prices: {},
        timestamp: new Date().toISOString(),
        symbols: symbols,
        error: error.message
      };
    }
  },

  async getOrderBook(symbol) {
    try {
      // Normalize symbol format: remove slashes and spaces for backend
      // EUR/USD -> EURUSD, BTC/USD -> BTCUSD
      const normalizedSymbol = symbol.replace(/[\/\s]/g, '').toUpperCase();
      const response = await api.get(`/market/orderbook/${normalizedSymbol}`);
      return response.data;
    } catch (error) {
      // Return empty orderbook instead of throwing to prevent crash
      console.warn('Order book API error:', error.message);
      return {
        symbol: symbol,
        bids: [],
        asks: [],
        last_update_id: 0,
        error: error.message
      };
    }
  },

  async getTradeHistory(symbol, limit = 100) {
    try {
      const response = await api.get(`/market/trades/${symbol}`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      // Return empty trades instead of throwing
      console.warn('Trade history API error:', error.message);
      return {
        symbol: symbol,
        trades: [],
        timestamp: new Date().toISOString(),
        error: error.message
      };
    }
  },

  async getInstruments() {
    try {
      const response = await api.get('/market/instruments');
      return response.data;
    } catch (error) {
      // Return default instruments on error
      console.warn('Instruments API error:', error.message);
      return {
        success: false,
        instruments: [],
        error: error.message
      };
    }
  },
};
