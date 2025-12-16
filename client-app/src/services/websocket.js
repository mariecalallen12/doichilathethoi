import { getWsBaseUrl } from '../utils/runtimeConfig';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.subscribers = new Map();
    this.eventListeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000; // 30 seconds max
    this.messageQueue = [];
    this.batchUpdateQueue = new Map(); // For batching high-frequency updates
    this.batchUpdateTimer = null;
    this.batchUpdateInterval = 16; // ~60fps (16ms)
    this.heartbeatInterval = null;
    this.heartbeatTimeout = null;
    this.heartbeatIntervalMs = 30000; // 30 seconds
    this.heartbeatTimeoutMs = 10000; // 10 seconds timeout
    this.isManualDisconnect = false;
    this.reconnectTimer = null;
  }

  connect(url = getWsBaseUrl()) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      if (import.meta.env.DEV) {
        console.log('WebSocket already connected');
      }
      return;
    }

    this.isManualDisconnect = false;
    
    // Normalize URL to ws/wss and ensure single /ws path
    let wsUrl = url.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:').replace(/\/+$/, '');
    if (!/\/ws($|\/|\?)/.test(wsUrl)) {
      wsUrl = `${wsUrl}/ws`;
    }

    // Add token to query params
    const token = localStorage.getItem('auth_token');
    const separator = wsUrl.includes('?') ? '&' : '?';
    wsUrl = `${wsUrl}${separator}token=${encodeURIComponent(token || '')}`;
    
    // Add channels to subscribe (include market streams) - ensure all real-time channels
    wsUrl += '&channels=orders,positions,prices,orderbook,trades,candles,market_data,scenario_changed,account,transactions,exchange_rates,diagnostics';
    
    try {
      this.socket = new WebSocket(wsUrl);
      this.setupEventHandlers();
      this.startHeartbeat();
    } catch (error) {
      // Only log in development
      if (import.meta.env.DEV) {
        console.error('WebSocket connection error:', error);
      }
      this.emit('error', { type: 'connection_error', error });
      this.scheduleReconnect();
    }
  }

  setupEventHandlers() {
    this.socket.onopen = () => {
      this.connected = true;
      this.reconnectAttempts = 0;
      if (import.meta.env.DEV) {
        console.log('WebSocket connected');
      }
      this.emit('connected', { status: 'connected' });
      
      // Process queued messages
      this.processMessageQueue();
    };

    this.socket.onclose = (event) => {
      this.connected = false;
      
      // Suppress expected errors (1006 = abnormal closure, often due to no auth)
      // Only log in development or for unexpected errors
      const isExpectedError = event.code === 1006 && !localStorage.getItem('auth_token');
      if (import.meta.env.DEV || !isExpectedError) {
        if (import.meta.env.DEV) {
          console.log('WebSocket disconnected:', event.code, event.reason);
        } else if (!isExpectedError && event.code !== 1000) {
          // Log unexpected errors even in production
          console.warn('WebSocket disconnected unexpectedly:', event.code);
        }
      }
      
      this.stopHeartbeat();
      this.emit('disconnected', { status: 'disconnected', code: event.code, reason: event.reason });
      
      // Auto-reconnect if not manual disconnect and not normal closure
      if (!this.isManualDisconnect && event.code !== 1000) {
        this.scheduleReconnect();
      }
    };

    this.socket.onerror = (error) => {
      // Only log in development or for critical errors
      if (import.meta.env.DEV) {
        console.error('WebSocket error:', error);
      }
      this.emit('error', { type: 'socket_error', error });
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        // Handle different message types
        if (message.type === 'connected') {
          if (import.meta.env.DEV) {
            console.log('WebSocket handshake complete');
          }
        } else if (message.type === 'pong') {
          // Clear heartbeat timeout on pong
          if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
          }
        } else if (message.type === 'ping') {
          // Respond to ping
          this.send({ type: 'pong' });
        } else if (message.type === 'order_update') {
          this.handleOrderUpdate(message);
        } else if (message.type === 'position_update') {
          this.handlePositionUpdate(message);
        } else if (message.type === 'health_update' || message.type === 'alert') {
          this.handleDiagnosticMessage(message);
        } else if (message.type === 'price_update' || message.channel === 'prices') {
          this.handlePriceUpdate(message);
        } else if (message.type === 'orderbook_update' || message.channel === 'orderbook') {
          this.handleOrderBookUpdate(message);
        } else if (message.type === 'trade_update' || message.channel === 'trades') {
          this.handleTradeUpdate(message);
        } else if (message.type === 'candle_update' || message.channel === 'candles') {
          this.handleCandleUpdate(message);
        } else if (message.type === 'market_data_update' || message.channel === 'market_data') {
          this.handleMarketDataUpdate(message);
        } else if (message.type === 'scenario_changed' || message.channel === 'scenario_changed') {
          this.handleScenarioChanged(message);
        } else if (message.channel === 'orders') {
          this.handleOrderUpdate(message);
        } else if (message.channel === 'positions') {
          this.handlePositionUpdate(message);
        } else if (message.channel === 'prices') {
          this.handlePriceUpdate(message);
        } 
      } catch (error) {
        // Only log parsing errors in development
        if (import.meta.env.DEV) {
          console.error('Error parsing WebSocket message:', error);
        }
      }
    };
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      this.messageQueue.push({ data, timestamp: Date.now() });
    }
  }

  handleOrderUpdate(message) {
    const callbacks = this.subscribers.get('orders');
    if (callbacks) {
      callbacks.forEach(callback => callback(message));
    }
  }

  handlePositionUpdate(message) {
    const callbacks = this.subscribers.get('positions');
    if (callbacks) {
      callbacks.forEach(callback => callback(message));
    }
  }

  handleAccountUpdate(data) {
    const callbacks = this.subscribers.get('account');
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  handleNewsUpdate(data) {
    const callbacks = this.subscribers.get('news');
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  handleIndicatorsUpdate(data) {
    const callbacks = this.subscribers.get('indicators');
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  handleTransactionUpdate(message) {
    const callbacks = this.subscribers.get('transactions');
    if (callbacks) {
      callbacks.forEach(callback => callback(message));
    }
  }

  handleExchangeRateUpdate(message) {
    const callbacks = this.subscribers.get('exchange_rates');
    if (callbacks) {
      callbacks.forEach(callback => callback(message));
    }
  }

  disconnect() {
    this.isManualDisconnect = true;
    this.stopHeartbeat();
    
    // Clear batch update timer
    if (this.batchUpdateTimer) {
      clearInterval(this.batchUpdateTimer);
      this.batchUpdateTimer = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.socket) {
      this.socket.close(1000, 'Manual disconnect');
      this.socket = null;
      this.connected = false;
    }
    
    this.messageQueue = [];
    this.batchUpdateQueue.clear();
    this.reconnectAttempts = 0;
  }

  subscribe(channel, callback) {
    const key = channel;
    if (!this.subscribers.has(key)) {
      this.subscribers.set(key, new Set());
    }

    this.subscribers.get(key).add(callback);
    
    // Send subscribe message if connected
    if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.send({
        type: 'subscribe',
        channels: [channel]
      });
    }
  }

  unsubscribe(channel, callback) {
    const key = channel;
    if (this.subscribers.has(key)) {
      this.subscribers.get(key).delete(callback);
      
      if (this.subscribers.get(key).size === 0) {
        this.subscribers.delete(key);
      }
    }
  }

  handleMarketData(data) {
    const callbacks = this.subscribers.get(data.instrument);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  handlePriceUpdate(message) {
    // Normalize message format (handle both short and long keys)
    const data = message.data || message;
    const symbol = data.s || data.symbol; // Support short key 's' or long 'symbol'
    
    if (symbol) {
      // Normalize to standard format for consumers
      const normalizedMessage = {
        ...message,
        data: {
          symbol: symbol,
          price: data.p !== undefined ? data.p : data.price,
          change: data.c !== undefined ? data.c : data.change,
          changePercent: data.cp !== undefined ? data.cp : data.changePercent,
          timestamp: data.t ? new Date(data.t * 1000).toISOString() : data.timestamp,
        }
      };
      
      // Store latest price update for this symbol
      if (!this.batchUpdateQueue.has('prices')) {
        this.batchUpdateQueue.set('prices', new Map());
      }
      const priceQueue = this.batchUpdateQueue.get('prices');
      if (priceQueue) {
        priceQueue.set(symbol, normalizedMessage);
      }
      
      // Start batch processing if not already started
      if (!this.batchUpdateTimer) {
        this.batchUpdateTimer = setInterval(() => {
          this.processBatchUpdates();
        }, this.batchUpdateInterval);
      }
    } else {
      // Immediate update if no symbol (fallback)
      const priceCallbacks = this.subscribers.get('prices');
      if (priceCallbacks) {
        priceCallbacks.forEach(callback => callback(message));
      }
    }
  }

  processBatchUpdates() {
    // Process all batched updates
    if (this.batchUpdateQueue.has('prices')) {
      const priceUpdates = this.batchUpdateQueue.get('prices');
      const priceCallbacks = this.subscribers.get('prices');
      
      if (priceCallbacks && priceUpdates && priceUpdates.size > 0) {
        // Send all batched price updates
        priceUpdates.forEach((message, symbol) => {
          priceCallbacks.forEach(callback => callback(message));
          
          // Also handle by symbol
          const symbolCallbacks = this.subscribers.get(symbol);
          if (symbolCallbacks) {
            symbolCallbacks.forEach(callback => callback(message));
          }
        });
        
        priceUpdates.clear();
      }
    }
  }

  handleMarketDataUpdate(message) {
    const callbacks = this.subscribers.get('market_data');
    if (callbacks) {
      callbacks.forEach(cb => cb(message));
    }
    if (message.data && message.data.symbol) {
      const symbolCallbacks = this.subscribers.get(`${message.data.symbol}:market_data`);
      if (symbolCallbacks) {
        symbolCallbacks.forEach(cb => cb(message));
      }
    }
  }

  handleScenarioChanged(message) {
    // Broadcast scenario change event to all subscribers
    const callbacks = this.subscribers.get('scenario_changed');
    if (callbacks) {
      callbacks.forEach(cb => cb(message));
    }
    // Also emit as event
    this.emit('scenario_changed', message);
  }

  handleOrderBookUpdate(message) {
    const callbacks = this.subscribers.get('orderbook');
    if (callbacks) {
      callbacks.forEach(cb => cb(message));
    }
    if (message.data && message.data.symbol) {
      const symbolCallbacks = this.subscribers.get(`${message.data.symbol}:orderbook`);
      if (symbolCallbacks) {
        symbolCallbacks.forEach(cb => cb(message));
      }
    }
  }

  handleTradeUpdate(message) {
    const callbacks = this.subscribers.get('trades');
    if (callbacks) {
      callbacks.forEach(cb => cb(message));
    }
    if (message.data && message.data.symbol) {
      const symbolCallbacks = this.subscribers.get(`${message.data.symbol}:trades`);
      if (symbolCallbacks) {
        symbolCallbacks.forEach(cb => cb(message));
      }
    }
  }

  handleCandleUpdate(message) {
    const callbacks = this.subscribers.get('candles');
    if (callbacks) {
      callbacks.forEach(cb => cb(message));
    }
    if (message.data && message.data.symbol) {
      const symbolCallbacks = this.subscribers.get(`${message.data.symbol}:candles`);
      if (symbolCallbacks) {
        symbolCallbacks.forEach(cb => cb(message));
      }
    }
  }

  emit(event, data) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach((callback) => callback(data));
    }
  }

  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event).add(callback);
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).delete(callback);
    }
  }

  // Heartbeat mechanism
  startHeartbeat() {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
        
        // Set timeout for pong response
        this.heartbeatTimeout = setTimeout(() => {
          if (import.meta.env.DEV) {
            console.warn('WebSocket heartbeat timeout, reconnecting...');
          }
          if (this.socket) {
            this.socket.close();
          }
          this.scheduleReconnect();
        }, this.heartbeatTimeoutMs);
      }
    }, this.heartbeatIntervalMs);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  // Exponential backoff reconnection
  scheduleReconnect() {
    if (this.isManualDisconnect || this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );

    // Only log reconnection attempts in development
    if (import.meta.env.DEV) {
      console.log(`Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
    }
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      // Recreate connection using getWsBaseUrl for proper URL resolution
      const url = getWsBaseUrl();
      this.connect(url);
      
      if (this.reconnectAttempts > 0) {
        this.emit('reconnected', { attempts: this.reconnectAttempts });
      }
    }, delay);
  }

  // Process queued messages
  processMessageQueue() {
    if (this.messageQueue.length === 0) {
      return;
    }

    // Only log in development
    if (import.meta.env.DEV) {
      console.log(`Processing ${this.messageQueue.length} queued messages`);
    }
    
    const messages = [...this.messageQueue];
    this.messageQueue = [];
    
    messages.forEach(({ data }) => {
      if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send(data);
      } else {
        // Re-queue if still not connected
        this.messageQueue.push({ data, timestamp: Date.now() });
      }
    });
  }
}

export default new WebSocketService();

