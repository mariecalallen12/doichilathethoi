import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useWebSocketStore } from './websocket';
import { marketApi } from '../services/api/market';
import tradingSystemWs from '../services/tradingSystemWebSocket';
import { mapMarketPrice } from '../utils/tradingSystemMappers';

export const useMarketStore = defineStore('market', () => {
  const instruments = ref([]);
  const selectedInstrument = ref(null);
  const priceData = ref(new Map());
  const orderbooks = ref(new Map());
  const trades = ref(new Map());
  const candles = ref(new Map());
  const marketData = ref(new Map());
  const isLoadingInstruments = ref(false);

  // Fallback initial data - will be replaced with real API data
  const initialInstruments = [
    { symbol: 'EUR/USD', type: 'forex', price: 1.0849, change: 0.02, changePercent: 0.02, volume: 1250000000, high: 1.0865, low: 1.0832 },
    { symbol: 'GBP/USD', type: 'forex', price: 1.26, change: 0.00, changePercent: 0.00, volume: 890000000, high: 1.2615, low: 1.2589 },
    { symbol: 'USD/JPY', type: 'forex', price: 149.8, change: -0.01, changePercent: -0.01, volume: 1450000000, high: 149.95, low: 149.65 },
    { symbol: 'AUD/USD', type: 'forex', price: 0.6750, change: 0.0012, changePercent: 0.18, volume: 650000000, high: 0.6765, low: 0.6738 },
    { symbol: 'USD/CHF', type: 'forex', price: 0.8750, change: -0.0005, changePercent: -0.06, volume: 420000000, high: 0.8765, low: 0.8742 },
    { symbol: 'BTC/USD', type: 'crypto', price: 43250, change: 1250, changePercent: 2.98, volume: 2500000000, high: 43500, low: 42000 },
    { symbol: 'ETH/USD', type: 'crypto', price: 2650, change: 45, changePercent: 1.73, volume: 1800000000, high: 2680, low: 2605 },
    { symbol: 'BNB/USD', type: 'crypto', price: 315, change: 8.5, changePercent: 2.77, volume: 450000000, high: 318, low: 306 },
    { symbol: 'SOL/USD', type: 'crypto', price: 98.5, change: 2.3, changePercent: 2.39, volume: 320000000, high: 99.8, low: 96.2 },
    { symbol: 'GOLD', type: 'commodity', price: 2045.30, change: -5.20, changePercent: -0.25, volume: 85000000, high: 2052.50, low: 2040.10 },
    { symbol: 'OIL', type: 'commodity', price: 78.45, change: 0.05, changePercent: 0.06, volume: 120000000, high: 79.20, low: 77.80 },
    { symbol: 'SILVER', type: 'commodity', price: 24.15, change: 0.12, changePercent: 0.50, volume: 35000000, high: 24.35, low: 24.00 },
    { symbol: 'SPX500', type: 'index', price: 4785.50, change: 12.30, changePercent: 0.26, volume: 4500000000, high: 4792.30, low: 4775.20 },
    { symbol: 'NAS100', type: 'index', price: 16850, change: 85, changePercent: 0.51, volume: 3200000000, high: 16900, low: 16780 },
    { symbol: 'DJ30', type: 'index', price: 37580, change: 125, changePercent: 0.33, volume: 2800000000, high: 37620, low: 37450 },
  ];

  // Initialize with fallback data
  instruments.value = initialInstruments;
  selectedInstrument.value = instruments.value[0];

  // Initialize price data
  initialInstruments.forEach(instrument => {
    priceData.value.set(instrument.symbol, {
      price: instrument.price,
      change: instrument.change,
      changePercent: instrument.changePercent,
      timestamp: Date.now(),
    });
  });

  const wsStore = useWebSocketStore();

  // Fetch instruments from API
  async function fetchInstruments() {
    isLoadingInstruments.value = true;
    try {
      // Define symbols matching backend format EXACTLY
      const symbolsToFetch = [
        // Crypto - backend expects: BTC, ETH, BNB, SOL, etc.
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'AVAX', 'LINK',
        // Forex - backend expects: EUR/USD, GBP/USD, etc.
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CHF', 'USD/CAD', 'NZD/USD',
        // Metals - backend expects: XAU, XAG (Gold, Silver)
        'XAU', 'XAG'
      ];

      // Fetch prices from backend
      const response = await marketApi.getPrices(symbolsToFetch);
      const pricesData = response.prices || response.data?.prices || {};

      console.log('Backend response:', response);

      // Map backend response to instruments format
      const fetchedInstruments = [];
      
      for (const [symbol, data] of Object.entries(pricesData)) {
        // Keep original symbol for API calls
        const originalSymbol = symbol;
        
        // Detect instrument type and create display name
        let type = 'forex';
        let displayName = symbol;
        
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

        // Calculate absolute change from percent
        const price = parseFloat(data.price) || 0;
        const changePercent = parseFloat(data.change_24h) || 0;
        const change = data.change ? parseFloat(data.change) : (price * changePercent) / 100;

        const instrument = {
          symbol: originalSymbol,         // For API calls - keep original
          displayName: displayName,       // For UI display
          type: type,
          price: price,
          change: change,                 // Calculated if not provided
          changePercent: changePercent,
          volume: parseFloat(data.volume) || 0,
          high: parseFloat(data.high) || price,
          low: parseFloat(data.low) || price,
          source: data.source || 'api',
          timestamp: data.timestamp || Date.now()
        };

        fetchedInstruments.push(instrument);

        // Update price data map using original symbol as key
        priceData.value.set(originalSymbol, {
          price: instrument.price,
          change: instrument.change,
          changePercent: instrument.changePercent,
          timestamp: instrument.timestamp,
          source: instrument.source
        });
      }

      // Update instruments if we got data from backend
      if (fetchedInstruments.length > 0) {
        console.log(`✅ Loaded ${fetchedInstruments.length} real instruments from backend`);
        instruments.value = fetchedInstruments;
        
        // Set selected instrument
        if (!selectedInstrument.value || !instruments.value.find(i => i.symbol === selectedInstrument.value.symbol)) {
          selectedInstrument.value = instruments.value[0];
        }
      } else {
        console.warn('⚠️ No data from backend, using fallback');
        // Keep initial mock data as fallback
      }
    } catch (error) {
      console.error('❌ Failed to fetch instruments from API:', error);
      // Keep initial mock data as fallback
    } finally {
      isLoadingInstruments.value = false;
    }
  }

  // Fetch instruments on store initialization (if in browser environment)
  if (typeof window !== 'undefined') {
    fetchInstruments();
  }

  // Subscribe to price updates
  function subscribeToInstrument(symbol) {
    const callback = (data) => {
      if (data.symbol === symbol) {
        priceData.value.set(symbol, {
          price: data.price,
          change: data.change,
          changePercent: data.changePercent,
          timestamp: Date.now(),
        });

        // Update instrument in list
        const index = instruments.value.findIndex(i => i.symbol === symbol);
        if (index !== -1) {
          instruments.value[index] = {
            ...instruments.value[index],
            price: data.price,
            change: data.change,
            changePercent: data.changePercent,
          };
        }
      }
    };

    wsStore.subscribe(symbol, callback);
  }

  function selectInstrument(instrument) {
    selectedInstrument.value = instrument;
    subscribeToInstrument(instrument.symbol);
  }

  function getPrice(symbol) {
    return priceData.value.get(symbol) || { price: 0, change: 0, changePercent: 0 };
  }

  function filterInstruments(type) {
    if (type === 'all') {
      return instruments.value;
    }
    return instruments.value.filter(i => i.type === type);
  }

  // Market overview stats
  const marketStats = computed(() => {
    const total = instruments.value.length;
    const up = instruments.value.filter(i => i.changePercent > 0).length;
    const down = instruments.value.filter(i => i.changePercent < 0).length;
    const totalVolume = instruments.value.reduce((sum, i) => sum + (i.volume || 0), 0);
    
    return {
      totalAssets: total,
      upMarkets: up,
      downMarkets: down,
      totalVolume,
    };
  });

  // Filters and search
  const searchQuery = ref('');
  const selectedCategory = ref('all');
  const sortBy = ref('price');
  const sortOrder = ref('desc');

  function setSearchQuery(query) {
    searchQuery.value = query;
  }

  function setCategory(category) {
    selectedCategory.value = category;
  }

  function setSort(sort, order = 'desc') {
    sortBy.value = sort;
    sortOrder.value = order;
  }

  const filteredAndSortedInstruments = computed(() => {
    let filtered = filterInstruments(selectedCategory.value);

    // Apply search
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      filtered = filtered.filter(i => 
        i.symbol.toLowerCase().includes(query) ||
        i.name?.toLowerCase().includes(query)
      );
    }

    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
      let aVal, bVal;
      
      switch (sortBy.value) {
        case 'price':
          aVal = a.price || 0;
          bVal = b.price || 0;
          break;
        case 'change':
          aVal = a.changePercent || 0;
          bVal = b.changePercent || 0;
          break;
        case 'volume':
          aVal = a.volume || 0;
          bVal = b.volume || 0;
          break;
        default:
          aVal = a.symbol;
          bVal = b.symbol;
      }

      if (sortOrder.value === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    return filtered;
  });

  // Removed simulatePriceUpdate() - now using WebSocket real-time updates only
  // All price updates come from WebSocket 'prices' channel via setupRealtimeSubscriptions()

  // Setup WebSocket listeners for TradingSystemAPI Market Data
  function setupWebSocketListeners() {
    console.log('[MarketStore] Setting up TradingSystemAPI WebSocket...');
    
    // Connect to market data stream from TradingSystemAPI
    tradingSystemWs.connectMarket((message) => {
      if (message.type === 'market_update') {
        const data = message.data;
        
        // Update price data for all symbols in the update
        if (data.prices) {
          Object.entries(data.prices).forEach(([symbol, priceInfo]) => {
            const price = parseFloat(priceInfo.current_price?.replace(/[^0-9.-]/g, '')) || priceInfo.price;
            const changePercent = parseFloat(priceInfo.price_change_24h?.replace(/[^0-9.-]/g, '')) || 0;
            const change = (price * changePercent) / 100;
            
            priceData.value.set(symbol, {
              price,
              change,
              changePercent,
              timestamp: Date.now(),
              source: priceInfo.source
            });
            
            // Update instrument in list
            const idx = instruments.value.findIndex(i => i.symbol === symbol);
            if (idx !== -1) {
              instruments.value[idx] = {
                ...instruments.value[idx],
                price,
                change,
                changePercent,
                timestamp: Date.now()
              };
            }
          });
          
          console.log('[MarketStore] Market data updated via WebSocket');
        }
      }
    });
    
    // Connection status callback
    tradingSystemWs.onConnectionChange = (stream, status) => {
      console.log(`[MarketStore] ${stream} WebSocket:`, status ? 'CONNECTED ✅' : 'DISCONNECTED ❌');
    };
  }

  // Start real-time updates
  function startRealTimeUpdates() {
    console.log('[MarketStore] Starting real-time market updates...');
    setupWebSocketListeners();
  }

  // Stop real-time updates
  function stopRealTimeUpdates() {
    console.log('[MarketStore] Stopping real-time market updates...');
    tradingSystemWs.disconnectAll();
  }

  // Setup WebSocket listeners (old backend)
  function setupRealtimeSubscriptions() {
    // Prices
    wsStore.subscribe('prices', (message) => {
      const data = message.data || message;
      if (!data?.symbol || data.price === undefined) return;
      const symbol = data.symbol.includes('/') ? data.symbol : data.symbol.replace('USDT', '/USD');
      priceData.value.set(symbol, {
        price: data.price,
        change: data.change || data.change_24h || 0,
        changePercent: data.changePercent || data.change_percent || 0,
        timestamp: Date.now(),
      });
      const idx = instruments.value.findIndex(i => i.symbol === symbol);
      if (idx !== -1) {
        instruments.value[idx] = {
          ...instruments.value[idx],
          price: data.price,
          change: data.change !== undefined ? data.change : (data.change_24h !== undefined ? data.change_24h : instruments.value[idx].change),
          changePercent: data.changePercent !== undefined ? data.changePercent : (data.change_percent !== undefined ? data.change_percent : instruments.value[idx].changePercent),
        };
      }
    });

    // Orderbook
    wsStore.subscribe('orderbook', (message) => {
      const data = message.data;
      if (!data?.symbol || !data.orderbook) return;
      const symbol = data.symbol.includes('/') ? data.symbol : data.symbol.replace('USDT', '/USD');
      orderbooks.value.set(symbol, data.orderbook);
    });

    // Trades
    wsStore.subscribe('trades', (message) => {
      const data = message.data;
      if (!data?.symbol || !data.trade) return;
      const symbol = data.symbol.includes('/') ? data.symbol : data.symbol.replace('USDT', '/USD');
      const list = trades.value.get(symbol) || [];
      list.unshift(data.trade);
      trades.value.set(symbol, list.slice(0, 200));
    });

    // Candles
    wsStore.subscribe('candles', (message) => {
      const data = message.data;
      if (!data?.symbol || !data.candle) return;
      const symbol = data.symbol.includes('/') ? data.symbol : data.symbol.replace('USDT', '/USD');
      const list = candles.value.get(symbol) || [];
      const ts = data.candle.timestamp || data.candle.ts;
      const candle = {
        timestamp: ts,
        open: data.candle.open,
        high: data.candle.high,
        low: data.candle.low,
        close: data.candle.close,
        volume: data.candle.volume,
      };
      const idx = list.findIndex(c => c.timestamp === ts);
      if (idx >= 0) list[idx] = candle;
      else list.push(candle);
      if (list.length > 600) list.shift();
      candles.value.set(symbol, list);
    });

    // Market data channel
    wsStore.subscribe('market_data', (message) => {
      const data = message.data || message;
      if (data.symbol) {
        const symbol = data.symbol.includes('/') ? data.symbol : data.symbol.replace('USDT', '/USD');
        marketData.value.set(symbol, data.market_data || data);
      }
    });

    // Scenario changed event
    wsStore.subscribe('scenario_changed', (message) => {
      // Reload chart data when scenario changes
      console.log('Scenario changed, reloading market data...');
      fetchInstruments();
    });

    // Ensure connection
    wsStore.connect && wsStore.connect();
  }

  if (typeof window !== 'undefined') {
    setupRealtimeSubscriptions();
  }

  return {
    instruments,
    selectedInstrument,
    priceData,
    orderbooks,
    trades,
    candles,
    marketData,
    marketStats,
    searchQuery,
    selectedCategory,
    sortBy,
    sortOrder,
    filteredAndSortedInstruments,
    isLoadingInstruments,
    selectInstrument,
    getPrice,
    filterInstruments,
    setSearchQuery,
    setCategory,
    setSort,
    fetchInstruments,
    setupWebSocketListeners,
    startRealTimeUpdates,
    stopRealTimeUpdates,
    setupRealtimeSubscriptions,
  };
});

