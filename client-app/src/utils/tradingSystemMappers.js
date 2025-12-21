/**
 * Data Mapping Utilities for TradingSystemAPI Integration
 * ========================================================
 * 
 * Maps TradingSystemAPI responses to UI component data structures
 */

/**
 * Map TradingSystemAPI signal types to UI signal types
 * 
 * API Signal Types: STRONG_BUY, BUY, UP, DOWN, SELL, STRONG_SELL, NEUTRAL
 * UI Signal Types: buy, sell, hold
 * 
 * @param {string} apiSignal - Signal from TradingSystemAPI
 * @returns {string} UI signal type (buy/sell/hold)
 */
export const mapSignalType = (apiSignal) => {
  const mapping = {
    'STRONG_BUY': 'buy',
    'BUY': 'buy',
    'UP': 'buy',
    'DOWN': 'sell',
    'SELL': 'sell',
    'STRONG_SELL': 'sell',
    'NEUTRAL': 'hold'
  };
  return mapping[apiSignal?.toUpperCase()] || 'hold';
};

/**
 * Map TradingSystemAPI signal strength to UI strength
 * 
 * API Strength: extreme, strong, moderate, weak
 * UI Strength: strong, medium, weak
 * 
 * @param {string} apiStrength - Strength from TradingSystemAPI
 * @returns {string} UI strength (strong/medium/weak)
 */
export const mapSignalStrength = (apiStrength) => {
  const mapping = {
    'extreme': 'strong',
    'strong': 'strong',
    'moderate': 'medium',
    'weak': 'weak'
  };
  return mapping[apiStrength?.toLowerCase()] || 'medium';
};

/**
 * Map complete trading signal from API to UI format
 * 
 * @param {object} apiSignal - Signal object from TradingSystemAPI
 * @returns {object} UI signal object
 */
export const mapTradingSignal = (apiSignal) => {
  if (!apiSignal) return null;
  
  return {
    id: apiSignal.symbol || Date.now().toString(),
    symbol: apiSignal.symbol,
    type: mapSignalType(apiSignal.signal),
    strength: mapSignalStrength(apiSignal.signal_strength),
    price: apiSignal.current_price || apiSignal.entry_price,
    target: apiSignal.target_price,
    stop_loss: apiSignal.stop_loss,
    source: 'ai', // Default to AI, can be determined from API later
    created_at: apiSignal.timestamp || new Date().toISOString(),
    confidence: apiSignal.confidence,
    recommendation: apiSignal.recommendation,
    timeframe: apiSignal.timeframe || '24h'
  };
};

/**
 * Map binary array to Fear & Greed Index
 * 
 * Calculation: (bullish_count / total_count) * 100
 * 
 * @param {object} binaryData - Binary array data from TradingSystemAPI
 * @returns {number} Fear & Greed index (0-100)
 */
export const calculateFearGreedIndex = (binaryData) => {
  if (!binaryData || !binaryData.total_signals) return 50;
  
  const bullishRatio = binaryData.bullish_signals / binaryData.total_signals;
  return Math.round(bullishRatio * 100);
};

/**
 * Map binary array to sentiment data
 * 
 * @param {object} binaryData - Binary array data from TradingSystemAPI
 * @returns {object} Sentiment object for UI
 */
export const mapBinaryToSentiment = (binaryData) => {
  if (!binaryData) {
    return {
      fear_greed_index: 50,
      social_sentiment: {
        twitter: 0.5,
        reddit: 0.5,
        overall: 0.5
      },
      market_sentiment: 'neutral'
    };
  }
  
  const bullishRatio = binaryData.bullish_signals / (binaryData.total_signals || 1);
  
  return {
    fear_greed_index: Math.round(bullishRatio * 100),
    social_sentiment: {
      overall: bullishRatio,
      twitter: bullishRatio * 0.9, // Simulate Twitter slightly lower
      reddit: bullishRatio * 1.1 // Simulate Reddit slightly higher
    },
    market_sentiment: binaryData.market_sentiment?.toLowerCase() || 'neutral'
  };
};

/**
 * Map market sentiment string to UI format
 * 
 * API: BULLISH, BEARISH, NEUTRAL
 * UI: bullish, bearish, neutral
 * 
 * @param {string} apiSentiment - Sentiment from TradingSystemAPI
 * @returns {string} UI sentiment
 */
export const mapMarketSentiment = (apiSentiment) => {
  return apiSentiment?.toLowerCase() || 'neutral';
};

/**
 * Parse price string to number
 * 
 * Handles formats like "$88,169.00", "88169", "88,169.00"
 * 
 * @param {string|number} price - Price string or number
 * @returns {number} Parsed price
 */
export const parsePrice = (price) => {
  if (typeof price === 'number') return price;
  if (!price) return 0;
  
  // Remove currency symbols and commas
  const cleaned = price.toString().replace(/[$,]/g, '');
  const parsed = parseFloat(cleaned);
  
  return isNaN(parsed) ? 0 : parsed;
};

/**
 * Parse percentage change string to number
 * 
 * Handles formats like "+0.05%", "-2.3%", "0.05"
 * 
 * @param {string|number} change - Change string or number
 * @returns {number} Parsed change
 */
export const parsePercentChange = (change) => {
  if (typeof change === 'number') return change;
  if (!change) return 0;
  
  // Remove % and + symbols
  const cleaned = change.toString().replace(/[%+]/g, '');
  const parsed = parseFloat(cleaned);
  
  return isNaN(parsed) ? 0 : parsed;
};

/**
 * Parse volume string to number
 * 
 * Handles formats like "5,284", "5284"
 * 
 * @param {string|number} volume - Volume string or number
 * @returns {number} Parsed volume
 */
export const parseVolume = (volume) => {
  if (typeof volume === 'number') return volume;
  if (!volume) return 0;
  
  // Remove commas
  const cleaned = volume.toString().replace(/,/g, '');
  const parsed = parseFloat(cleaned);
  
  return isNaN(parsed) ? 0 : parsed;
};

/**
 * Map market price from API to UI format
 * 
 * @param {object} apiPrice - Price object from TradingSystemAPI
 * @param {string} symbol - Symbol key
 * @returns {object} UI price object
 */
export const mapMarketPrice = (apiPrice, symbol) => {
  if (!apiPrice) return null;
  
  const price = parsePrice(apiPrice.current_price);
  const changePercent = parsePercentChange(apiPrice.price_change_24h);
  const change = price * (changePercent / 100);
  
  // Determine display name and type
  let displayName = symbol;
  let type = 'forex';
  
  if (['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'AVAX', 'LINK'].includes(symbol)) {
    type = 'crypto';
    displayName = `${symbol}/USD`;
  } else if (symbol === 'XAU') {
    type = 'commodity';
    displayName = 'Gold (XAU)';
  } else if (symbol === 'XAG') {
    type = 'commodity';
    displayName = 'Silver (XAG)';
  } else if (symbol.includes('/')) {
    type = 'forex';
    displayName = symbol;
  }
  
  return {
    symbol: symbol,
    displayName: displayName,
    originalSymbol: symbol, // For API calls
    type: type,
    price: price,
    change: change,
    changePercent: changePercent,
    volume: parseVolume(apiPrice.volume),
    high: parsePrice(apiPrice.high_24h) || price * 1.02,
    low: parsePrice(apiPrice.low_24h) || price * 0.98,
    source: apiPrice.source || 'api',
    timestamp: apiPrice.timestamp || new Date().toISOString()
  };
};

/**
 * Map all market prices from API response
 * 
 * @param {object} apiResponse - Response from marketDataApi.getAllPrices()
 * @returns {array} Array of UI price objects
 */
export const mapAllMarketPrices = (apiResponse) => {
  if (!apiResponse || !apiResponse.prices) return [];
  
  const prices = [];
  
  for (const [symbol, priceData] of Object.entries(apiResponse.prices)) {
    const mapped = mapMarketPrice(priceData, symbol);
    if (mapped) {
      prices.push(mapped);
    }
  }
  
  return prices;
};

/**
 * Map all trading signals from API response
 * 
 * @param {object} apiResponse - Response from tradingFeaturesApi.getAllSignals()
 * @returns {array} Array of UI signal objects
 */
export const mapAllTradingSignals = (apiResponse) => {
  if (!apiResponse) return [];
  
  // Handle both object and array responses
  const signalsData = apiResponse.data || apiResponse;
  const signals = [];
  
  if (Array.isArray(signalsData)) {
    // Already an array
    signals.push(...signalsData.map(mapTradingSignal).filter(Boolean));
  } else if (typeof signalsData === 'object') {
    // Object with symbol keys
    for (const [symbol, signalData] of Object.entries(signalsData)) {
      const mapped = mapTradingSignal(signalData);
      if (mapped) {
        signals.push(mapped);
      }
    }
  }
  
  return signals;
};

/**
 * Validate and sanitize data
 */
export const validateSignal = (signal) => {
  return signal &&
    signal.symbol &&
    signal.type &&
    (signal.type === 'buy' || signal.type === 'sell' || signal.type === 'hold');
};

export const validatePrice = (price) => {
  return price &&
    typeof price.symbol === 'string' &&
    typeof price.price === 'number' &&
    !isNaN(price.price);
};

/**
 * Export all mapping functions
 */
export default {
  // Signal mappings
  mapSignalType,
  mapSignalStrength,
  mapTradingSignal,
  mapAllTradingSignals,
  
  // Sentiment mappings
  calculateFearGreedIndex,
  mapBinaryToSentiment,
  mapMarketSentiment,
  
  // Price mappings
  parsePrice,
  parsePercentChange,
  parseVolume,
  mapMarketPrice,
  mapAllMarketPrices,
  
  // Validation
  validateSignal,
  validatePrice
};
