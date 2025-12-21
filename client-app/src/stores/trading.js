import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { tradingFeaturesApi } from '../services/api/tradingSystem';
import tradingSystemWs from '../services/tradingSystemWebSocket';

export const useTradingStore = defineStore('trading', () => {
  // State
  const signals = ref({});
  const binaryArray = ref([]);
  const binaryString = ref('');
  const marketSentiment = ref('UNKNOWN');
  const assetClassAnalysis = ref({});
  const topGainers = ref([]);
  const topLosers = ref([]);
  const recommendations = ref({});
  const analysis = ref({});
  const signalStream = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const lastUpdate = ref(null);
  
  // WebSocket connection status
  const wsConnected = ref({
    signals: false,
    binary: false
  });

  /**
   * Fetch all trading signals
   */
  async function fetchAllSignals() {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingFeaturesApi.getAllSignals();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      signals.value = response.signals || {};
      lastUpdate.value = new Date().toISOString();
      
      console.log('[TradingStore] Signals fetched:', Object.keys(signals.value).length);
    } catch (err) {
      error.value = err.message;
      console.error('[TradingStore] Error fetching signals:', err);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch binary array
   */
  async function fetchBinaryArray() {
    try {
      const response = await tradingFeaturesApi.getBinaryArray();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      binaryArray.value = response.binary_array || [];
      binaryString.value = response.binary_string || '';
      marketSentiment.value = response.market_sentiment || 'UNKNOWN';
      
      console.log('[TradingStore] Binary array:', binaryString.value);
      console.log('[TradingStore] Market sentiment:', marketSentiment.value);
    } catch (err) {
      error.value = err.message;
      console.error('[TradingStore] Error fetching binary:', err);
    }
  }

  /**
   * Fetch market analysis
   */
  async function fetchMarketAnalysis() {
    try {
      const response = await tradingFeaturesApi.getMarketAnalysis();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      assetClassAnalysis.value = response.asset_class_analysis || {};
      topGainers.value = response.top_gainers || [];
      topLosers.value = response.top_losers || [];
      
      console.log('[TradingStore] Analysis fetched');
    } catch (err) {
      error.value = err.message;
      console.error('[TradingStore] Error fetching analysis:', err);
    }
  }

  /**
   * Fetch trading recommendations
   */
  async function fetchRecommendations() {
    try {
      const response = await tradingFeaturesApi.getRecommendations();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      recommendations.value = response.recommendations || {};
      analysis.value = response.summary || {};
      
      console.log('[TradingStore] Recommendations fetched');
    } catch (err) {
      error.value = err.message;
      console.error('[TradingStore] Error fetching recommendations:', err);
    }
  }

  /**
   * Setup WebSocket real-time listeners
   */
  function setupWebSocketListeners(onConnectionChange) {
    // Signals stream
    tradingSystemWs.connectSignals((message) => {
      if (message.type === 'signal_update') {
        // Update individual signal
        const { symbol, signal } = message.data;
        signals.value[symbol] = signal;
        
        // Add to stream
        signalStream.value.unshift({
          timestamp: new Date().toISOString(),
          symbol,
          signal
        });
        
        // Keep only last 50 signals in stream
        if (signalStream.value.length > 50) {
          signalStream.value = signalStream.value.slice(0, 50);
        }
        
        lastUpdate.value = new Date().toISOString();
        console.log('[TradingStore] Signal update:', symbol, signal.direction);
      }
    });
    
    // Binary stream
    tradingSystemWs.connectBinary((message) => {
      if (message.type === 'binary_update') {
        binaryArray.value = message.data.binary_array || [];
        binaryString.value = message.data.binary_string || '';
        marketSentiment.value = message.data.market_sentiment || 'UNKNOWN';
        
        console.log('[TradingStore] Binary update:', marketSentiment.value);
      }
    });
    
    // Connection status
    tradingSystemWs.onConnectionChange = (stream, status) => {
      wsConnected.value[stream] = status;
      
      if (onConnectionChange) {
        onConnectionChange(stream, status);
      }
      
      console.log(`[TradingStore] ${stream} connection:`, status ? 'CONNECTED' : 'DISCONNECTED');
    };
  }

  /**
   * Start real-time updates
   */
  function startRealTimeUpdates() {
    console.log('[TradingStore] Starting real-time updates...');
    
    // Initial fetch
    fetchAllSignals();
    fetchBinaryArray();
    fetchMarketAnalysis();
    
    // Periodic refresh for analysis (every 30s)
    const analysisInterval = setInterval(() => {
      fetchMarketAnalysis();
      fetchRecommendations();
    }, 30000);
    
    // Store interval for cleanup
    window._tradingAnalysisInterval = analysisInterval;
  }

  /**
   * Stop real-time updates
   */
  function stopRealTimeUpdates() {
    console.log('[TradingStore] Stopping real-time updates...');
    
    // Disconnect WebSocket
    tradingSystemWs.disconnectAll();
    
    // Clear intervals
    if (window._tradingAnalysisInterval) {
      clearInterval(window._tradingAnalysisInterval);
      delete window._tradingAnalysisInterval;
    }
  }

  /**
   * Get signal for specific symbol
   */
  async function getSignalForSymbol(symbol) {
    try {
      const response = await tradingFeaturesApi.getSignalForSymbol(symbol);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      return response.signal;
    } catch (err) {
      console.error(`[TradingStore] Error fetching signal for ${symbol}:`, err);
      return null;
    }
  }

  // Computed
  const bullishCount = computed(() => {
    return binaryArray.value.filter(b => b === 1).length;
  });

  const bearishCount = computed(() => {
    return binaryArray.value.filter(b => b === 0).length;
  });

  const sentimentPercentage = computed(() => {
    const total = binaryArray.value.length;
    if (total === 0) return 50;
    return (bullishCount.value / total) * 100;
  });

  const signalCount = computed(() => {
    return Object.keys(signals.value).length;
  });

  return {
    // State
    signals,
    binaryArray,
    binaryString,
    marketSentiment,
    assetClassAnalysis,
    topGainers,
    topLosers,
    recommendations,
    analysis,
    signalStream,
    isLoading,
    error,
    lastUpdate,
    wsConnected,
    
    // Computed
    bullishCount,
    bearishCount,
    sentimentPercentage,
    signalCount,
    
    // Actions
    fetchAllSignals,
    fetchBinaryArray,
    fetchMarketAnalysis,
    fetchRecommendations,
    getSignalForSymbol,
    setupWebSocketListeners,
    startRealTimeUpdates,
    stopRealTimeUpdates
  };
});
