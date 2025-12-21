/**
 * Real-time Updates Service for TradingSystemAPI
 * ==============================================
 * 
 * Polls TradingSystemAPI for real-time data updates
 * - Market prices every 5 seconds
 * - Trading signals every 30 seconds
 * - Binary sentiment every 30 seconds
 */

import { marketDataApi, tradingFeaturesApi } from './api/tradingSystem';
import { 
  mapAllMarketPrices, 
  mapAllTradingSignals,
  mapBinaryToSentiment 
} from '../utils/tradingSystemMappers';

class RealTimeUpdatesService {
  constructor() {
    // Market data update
    this.marketUpdateInterval = null;
    this.marketUpdateFrequency = 5000; // 5 seconds
    
    // Trading signals update
    this.signalsUpdateInterval = null;
    this.signalsUpdateFrequency = 30000; // 30 seconds
    
    // Sentiment update
    this.sentimentUpdateInterval = null;
    this.sentimentUpdateFrequency = 30000; // 30 seconds
    
    // Callbacks
    this.onMarketUpdate = null;
    this.onSignalsUpdate = null;
    this.onSentimentUpdate = null;
    
    // State
    this.isRunning = false;
  }
  
  /**
   * Start real-time market data updates
   */
  startMarketUpdates(callback) {
    if (this.marketUpdateInterval) {
      this.stopMarketUpdates();
    }
    
    this.onMarketUpdate = callback;
    
    // Initial fetch
    this.fetchMarketData();
    
    // Setup interval
    this.marketUpdateInterval = setInterval(() => {
      this.fetchMarketData();
    }, this.marketUpdateFrequency);
    
    console.log(`[RealTime] Market updates started (every ${this.marketUpdateFrequency/1000}s)`);
  }
  
  /**
   * Stop market data updates
   */
  stopMarketUpdates() {
    if (this.marketUpdateInterval) {
      clearInterval(this.marketUpdateInterval);
      this.marketUpdateInterval = null;
      console.log('[RealTime] Market updates stopped');
    }
  }
  
  /**
   * Start real-time trading signals updates
   */
  startSignalsUpdates(callback) {
    if (this.signalsUpdateInterval) {
      this.stopSignalsUpdates();
    }
    
    this.onSignalsUpdate = callback;
    
    // Initial fetch
    this.fetchSignals();
    
    // Setup interval
    this.signalsUpdateInterval = setInterval(() => {
      this.fetchSignals();
    }, this.signalsUpdateFrequency);
    
    console.log(`[RealTime] Signals updates started (every ${this.signalsUpdateFrequency/1000}s)`);
  }
  
  /**
   * Stop signals updates
   */
  stopSignalsUpdates() {
    if (this.signalsUpdateInterval) {
      clearInterval(this.signalsUpdateInterval);
      this.signalsUpdateInterval = null;
      console.log('[RealTime] Signals updates stopped');
    }
  }
  
  /**
   * Start real-time sentiment updates
   */
  startSentimentUpdates(callback) {
    if (this.sentimentUpdateInterval) {
      this.stopSentimentUpdates();
    }
    
    this.onSentimentUpdate = callback;
    
    // Initial fetch
    this.fetchSentiment();
    
    // Setup interval
    this.sentimentUpdateInterval = setInterval(() => {
      this.fetchSentiment();
    }, this.sentimentUpdateFrequency);
    
    console.log(`[RealTime] Sentiment updates started (every ${this.sentimentUpdateFrequency/1000}s)`);
  }
  
  /**
   * Stop sentiment updates
   */
  stopSentimentUpdates() {
    if (this.sentimentUpdateInterval) {
      clearInterval(this.sentimentUpdateInterval);
      this.sentimentUpdateInterval = null;
      console.log('[RealTime] Sentiment updates stopped');
    }
  }
  
  /**
   * Fetch market data
   */
  async fetchMarketData() {
    try {
      const response = await marketDataApi.getAllPrices();
      
      if (response && !response.error) {
        const prices = mapAllMarketPrices(response);
        
        if (this.onMarketUpdate && prices.length > 0) {
          this.onMarketUpdate(prices);
          console.log(`[RealTime] Market data updated: ${prices.length} instruments`);
        }
      }
    } catch (error) {
      console.error('[RealTime] Market data fetch error:', error.message);
    }
  }
  
  /**
   * Fetch trading signals
   */
  async fetchSignals() {
    try {
      const response = await tradingFeaturesApi.getAllSignals();
      
      if (response && !response.error) {
        const signals = mapAllTradingSignals(response);
        
        if (this.onSignalsUpdate && signals.length > 0) {
          this.onSignalsUpdate(signals);
          console.log(`[RealTime] Signals updated: ${signals.length} signals`);
        }
      }
    } catch (error) {
      console.error('[RealTime] Signals fetch error:', error.message);
    }
  }
  
  /**
   * Fetch sentiment data
   */
  async fetchSentiment() {
    try {
      const response = await tradingFeaturesApi.getBinaryArray();
      
      if (response && !response.error) {
        const sentiment = mapBinaryToSentiment(response);
        
        if (this.onSentimentUpdate) {
          this.onSentimentUpdate(sentiment);
          console.log(`[RealTime] Sentiment updated: ${sentiment.market_sentiment}`);
        }
      }
    } catch (error) {
      console.error('[RealTime] Sentiment fetch error:', error.message);
    }
  }
  
  /**
   * Start all real-time updates
   */
  startAll({ onMarket, onSignals, onSentiment }) {
    if (onMarket) {
      this.startMarketUpdates(onMarket);
    }
    
    if (onSignals) {
      this.startSignalsUpdates(onSignals);
    }
    
    if (onSentiment) {
      this.startSentimentUpdates(onSentiment);
    }
    
    this.isRunning = true;
    console.log('[RealTime] All updates started');
  }
  
  /**
   * Stop all real-time updates
   */
  stopAll() {
    this.stopMarketUpdates();
    this.stopSignalsUpdates();
    this.stopSentimentUpdates();
    this.isRunning = false;
    console.log('[RealTime] All updates stopped');
  }
  
  /**
   * Check if updates are running
   */
  isActive() {
    return this.isRunning;
  }
  
  /**
   * Set update frequencies
   */
  setUpdateFrequencies({ market, signals, sentiment }) {
    if (market) {
      this.marketUpdateFrequency = market;
      console.log(`[RealTime] Market update frequency set to ${market}ms`);
    }
    
    if (signals) {
      this.signalsUpdateFrequency = signals;
      console.log(`[RealTime] Signals update frequency set to ${signals}ms`);
    }
    
    if (sentiment) {
      this.sentimentUpdateFrequency = sentiment;
      console.log(`[RealTime] Sentiment update frequency set to ${sentiment}ms`);
    }
  }
}

// Create singleton instance
const realTimeUpdates = new RealTimeUpdatesService();

export default realTimeUpdates;

// Named exports for convenience
export const {
  startMarketUpdates,
  startSignalsUpdates,
  startSentimentUpdates,
  stopMarketUpdates,
  stopSignalsUpdates,
  stopSentimentUpdates,
  startAll,
  stopAll,
  isActive,
  setUpdateFrequencies
} = realTimeUpdates;
