import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useWebSocketStore } from './websocket';
import { marketApi } from '../services/api/market';

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
      // Get list of symbols to fetch
      const symbolsToFetch = initialInstruments.map(inst => {
        // Convert symbol format: EUR/USD -> EURUSD, BTC/USD -> BTCUSDT
        let symbol = inst.symbol.replace('/', '');
        if (symbol.includes('USD') && !symbol.endsWith('USDT') && inst.type === 'crypto') {
          symbol = symbol.replace('USD', 'USDT');
        }
        return symbol;
      });

      // Fetch prices from API
      const response = await marketApi.getPrices(symbolsToFetch);
      const pricesData = response.prices || response.data?.prices || response;

      // Map API response to instruments format
      const fetchedInstruments = [];
      for (const [symbolKey, priceData] of Object.entries(pricesData)) {
        // Find matching initial instrument to get type and other metadata
        const originalSymbol = symbolKey.replace('USDT', '/USD').replace(/([A-Z]{3})([A-Z]{3})/, '$1/$2');
        const originalInst = initialInstruments.find(inst => {
          const instSymbol = inst.symbol.replace('/', '');
          const keySymbol = symbolKey.replace('USDT', 'USD');
          return instSymbol === keySymbol || inst.symbol === originalSymbol;
        });

        // Determine instrument type
        let instrumentType = 'forex';
        if (symbolKey.includes('USDT') || symbolKey.includes('BTC') || symbolKey.includes('ETH')) {
          instrumentType = 'crypto';
        } else if (['GOLD', 'OIL', 'SILVER'].some(c => symbolKey.includes(c))) {
          instrumentType = 'commodity';
        } else if (['SPX', 'NAS', 'DJ'].some(c => symbolKey.includes(c))) {
          instrumentType = 'index';
        }

        // Format symbol for display
        let displaySymbol = symbolKey;
        if (symbolKey.includes('USDT')) {
          displaySymbol = symbolKey.replace('USDT', '/USD');
        } else if (symbolKey.length === 6 && !symbolKey.includes('/')) {
          displaySymbol = symbolKey.slice(0, 3) + '/' + symbolKey.slice(3);
        }

        const instrument = {
          symbol: displaySymbol,
          type: originalInst?.type || instrumentType,
          price: priceData.price || priceData.price_24h || 0,
          change: priceData.change_24h || priceData.change || 0,
          changePercent: priceData.change_percent || priceData.change_percent_24h || 0,
          volume: priceData.volume_24h || priceData.volume || originalInst?.volume || 0,
          high: priceData.high_24h || priceData.high || originalInst?.high || 0,
          low: priceData.low_24h || priceData.low || originalInst?.low || 0,
        };

        fetchedInstruments.push(instrument);

        // Update price data
        priceData.value.set(displaySymbol, {
          price: instrument.price,
          change: instrument.change,
          changePercent: instrument.changePercent,
          timestamp: Date.now(),
        });
      }

      // Update instruments if we got data
      if (fetchedInstruments.length > 0) {
        instruments.value = fetchedInstruments;
        if (!selectedInstrument.value || !instruments.value.find(i => i.symbol === selectedInstrument.value.symbol)) {
          selectedInstrument.value = instruments.value[0];
        }
      }
    } catch (error) {
      console.error('Failed to fetch instruments from API:', error);
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

  // Setup WebSocket listeners
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
    setupWebSocketListeners: setupRealtimeSubscriptions,
    setupRealtimeSubscriptions,
  };
});

