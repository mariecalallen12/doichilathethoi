import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import websocketService from '../services/websocket';

export const useMarketPreviewStore = defineStore('marketPreview', () => {
  // State
  const marketData = ref({});
  const candles = ref({});
  const loading = ref(false);
  const error = ref(null);
  const websocketConnected = ref(false);
  const subscriptions = ref(new Set());

  // Initialize WebSocket connection
  const initWebSocket = () => {
    try {
      // Get auth token from localStorage
      const token = localStorage.getItem('auth_token');
      if (!token) {
        console.warn('[MarketPreview] No auth token found');
        return;
      }

      // Connect using WebSocket service
      websocketService.connect(token)
        .then(() => {
          websocketConnected.value = true;
          error.value = null;
        })
        .catch(err => {
          console.error('[MarketPreview] Failed to connect WebSocket:', err);
          error.value = 'Failed to connect to WebSocket';
        });

      // Set up message handlers
      websocketService.onMessage('price_update', handlePriceUpdate);
      websocketService.onMessage('candle_update', handleCandleUpdate);
      websocketService.onMessage('market_data_update', handleMarketDataUpdate);

      // Set up connection handlers
      websocketService.onConnection((connected) => {
        websocketConnected.value = connected;
        if (connected) {
          error.value = null;
          // Re-subscribe to all symbols after reconnection
          subscriptions.value.forEach(symbol => {
            subscribeToSymbol(symbol);
          });
        }
      });

    } catch (err) {
      console.error('[MarketPreview] Failed to initialize WebSocket:', err);
      error.value = 'Failed to connect to WebSocket';
    }
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = (eventType, data) => {
    switch (eventType) {
      case 'price_update':
        handlePriceUpdate(data);
        break;
      case 'candle_update':
        handleCandleUpdate(data);
        break;
      case 'market_data_update':
        handleMarketDataUpdate(data);
        break;
      default:
        // Ignore other events
        break;
    }
  };

  // Handle price updates
  const handlePriceUpdate = (data) => {
    if (!data.symbol) return;
    
    // Update market data with new price
    if (marketData.value[data.symbol]) {
      const currentData = marketData.value[data.symbol];
      const oldPrice = currentData.price;
      const newPrice = data.price;
      
      // Calculate change
      const change_24h = newPrice - oldPrice;
      const change_percent_24h = oldPrice > 0 ? (change_24h / oldPrice * 100) : 0;
      
      // Update market data
      marketData.value[data.symbol] = {
        ...currentData,
        price: newPrice,
        change_24h: currentData.change_24h + change_24h,
        change_percent_24h: currentData.change_percent_24h + change_percent_24h,
        high_24h: Math.max(currentData.high_24h, newPrice),
        low_24h: Math.min(currentData.low_24h, newPrice),
        timestamp: data.ts || new Date().toISOString()
      };
    }
  };

  // Handle candle updates
  const handleCandleUpdate = (data) => {
    if (!data.symbol || !data.candle) return;
    
    // Update candles data
    if (!candles.value[data.symbol]) {
      candles.value[data.symbol] = [];
    }
    
    const candleList = candles.value[data.symbol];
    const newCandle = {
      timestamp: data.candle.start_ts || data.candle.timestamp,
      open: data.candle.open,
      high: data.candle.high,
      low: data.candle.low,
      close: data.candle.close,
      volume: data.candle.volume
    };
    
    // Find existing candle with same timestamp
    const existingIndex = candleList.findIndex(c => 
      new Date(c.timestamp).getTime() === new Date(newCandle.timestamp).getTime()
    );
    
    if (existingIndex >= 0) {
      // Update existing candle
      candleList[existingIndex] = newCandle;
    } else {
      // Add new candle and keep only last 200
      candleList.unshift(newCandle);
      if (candleList.length > 200) {
        candleList.splice(200);
      }
    }
  };

  // Handle market data updates
  const handleMarketDataUpdate = (data) => {
    if (!data.symbol || !data.market_data) return;
    
    // Update market data with full data from backend
    marketData.value[data.symbol] = {
      ...marketData.value[data.symbol],
      ...data.market_data
    };
  };

  // Subscribe to symbol updates
  const subscribeToSymbol = (symbol) => {
    if (!symbol) return;
    
    subscriptions.value.add(symbol);
    
    // Send subscription message via WebSocket service
    websocketService.subscribe([symbol], ['prices', 'candles', 'market_data']);
  };

  // Unsubscribe from symbol updates
  const unsubscribeFromSymbol = (symbol) => {
    if (!symbol) return;
    
    subscriptions.value.delete(symbol);
    
    // Send unsubscribe message via WebSocket service
    websocketService.unsubscribe([symbol]);
  };

  // Fetch market data from API
  const fetchMarketData = async (symbol) => {
    if (!symbol) return;
    
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get(`/api/admin/market-preview/${symbol}`);
      
      if (response.data?.success) {
        marketData.value[symbol] = response.data.data;
      } else {
        throw new Error(response.data?.detail || 'Failed to fetch market data');
      }
    } catch (err) {
      console.error(`[MarketPreview] Failed to fetch market data for ${symbol}:`, err);
      error.value = err.message || 'Failed to fetch market data';
    } finally {
      loading.value = false;
    }
  };

  // Fetch candles data from API
  const fetchCandles = async (symbol, timeframe = '1h') => {
    if (!symbol) return [];
    
    try {
      // For now, we'll use the simulator's candles
      // In production, this could call a separate candles API
      const response = await api.get(`/api/admin/simulator/snapshot`);
      
      if (response.data?.success && response.data.data?.candles?.[symbol]) {
        const simulatorCandles = response.data.data.candles[symbol];
        
        // Convert simulator candles to our format
        return simulatorCandles.map(candle => ({
          timestamp: candle.start_ts,
          open: candle.open,
          high: candle.high,
          low: candle.low,
          close: candle.close,
          volume: candle.volume
        }));
      }
      
      return [];
    } catch (err) {
      console.error(`[MarketPreview] Failed to fetch candles for ${symbol}:`, err);
      return [];
    }
  };

  // Get candles (with caching)
  const getCandles = async (symbol, timeframe = '1h') => {
    const cacheKey = `${symbol}_${timeframe}`;
    
    if (!candles.value[cacheKey]) {
      candles.value[cacheKey] = await fetchCandles(symbol, timeframe);
    }
    
    return candles.value[cacheKey];
  };

  // Refresh data for a symbol
  const refreshSymbol = async (symbol) => {
    await fetchMarketData(symbol);
    const cacheKey = `${symbol}_1h`; // Default timeframe
    candles.value[cacheKey] = await fetchCandles(symbol, '1h');
  };

  // Initialize store
  const init = () => {
    // Initialize WebSocket connection
    initWebSocket();
  };

  // Cleanup
  const cleanup = () => {
    // Disconnect WebSocket service
    websocketService.disconnect();
    
    // Clear subscriptions
    subscriptions.value.clear();
  };

  // Computed properties
  const isConnected = computed(() => websocketConnected.value);
  const isLoading = computed(() => loading.value);
  const hasError = computed(() => !!error.value);

  // Auto-initialize
  init();

  return {
    // State
    marketData,
    candles,
    loading,
    error,
    isConnected,
    isLoading,
    hasError,
    
    // Actions
    subscribeToSymbol,
    unsubscribeFromSymbol,
    fetchMarketData,
    getCandles,
    refreshSymbol,
    handleWebSocketMessage,
    
    // Cleanup
    cleanup
  };
});
