/**
 * WebSocket Service for Real-time Market Data
 * Handles WebSocket connections, subscriptions, and message handling
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    this.reconnectDelay = 5000;
    this.reconnectTimer = null;
    this.messageHandlers = new Map();
    this.connectionHandlers = new Set();
    this.isConnected = false;
    this.subscriptions = new Set();
    this.token = null;
  }

  /**
   * Initialize WebSocket connection
   */
  connect(token) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    this.token = token;

    return new Promise((resolve, reject) => {
      try {
        // Build WebSocket URL with token
        const wsUrl = `${this.url}?token=${encodeURIComponent(token)}&channels=prices,candles,market_data`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this.isConnected = true;
          this.clearReconnectTimer();
          
          // Notify connection handlers
          this.connectionHandlers.forEach(handler => handler(true));
          
          // Re-subscribe to previous subscriptions
          if (this.subscriptions.size > 0) {
            this.subscribe(Array.from(this.subscriptions));
          }
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Disconnected');
          this.isConnected = false;
          this.ws = null;
          
          // Notify connection handlers
          this.connectionHandlers.forEach(handler => handler(false));
          
          // Attempt to reconnect
          this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          reject(error);
        };

      } catch (error) {
        console.error('[WebSocket] Failed to connect:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    this.clearReconnectTimer();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.isConnected = false;
    this.subscriptions.clear();
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(message) {
    const { type, channel, data } = message;
    
    // Handle connection messages
    if (type === 'connected') {
      console.log('[WebSocket] Connection confirmed:', message);
      return;
    }
    
    if (type === 'subscribed') {
      console.log('[WebSocket] Subscribed to:', message);
      return;
    }
    
    if (type === 'pong') {
      // Ping/pong response
      return;
    }
    
    // Handle data messages
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data, channel);
        } catch (error) {
          console.error(`[WebSocket] Error in handler for ${type}:`, error);
        }
      });
    }
  }

  /**
   * Subscribe to channels and symbols
   */
  subscribe(symbols = [], channels = []) {
    if (!this.isConnected) {
      console.warn('[WebSocket] Cannot subscribe - not connected');
      return;
    }

    // Store subscriptions
    symbols.forEach(symbol => this.subscriptions.add(symbol));

    // Send subscription message
    this.send({
      type: 'subscribe',
      channels: channels.length > 0 ? channels : ['prices', 'candles', 'market_data'],
      symbols: symbols
    });
  }

  /**
   * Unsubscribe from symbols
   */
  unsubscribe(symbols = []) {
    if (!this.isConnected) {
      return;
    }

    // Remove from subscriptions
    symbols.forEach(symbol => this.subscriptions.delete(symbol));

    // Send unsubscription message
    this.send({
      type: 'unsubscribe',
      channels: ['prices', 'candles', 'market_data'],
      symbols: symbols
    });
  }

  /**
   * Send message to WebSocket
   */
  send(message) {
    if (!this.isConnected || !this.ws) {
      console.warn('[WebSocket] Cannot send message - not connected');
      return;
    }

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('[WebSocket] Failed to send message:', error);
    }
  }

  /**
   * Add message handler for specific message type
   */
  onMessage(type, handler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    this.messageHandlers.get(type).add(handler);
  }

  /**
   * Remove message handler
   */
  offMessage(type, handler) {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.messageHandlers.delete(type);
      }
    }
  }

  /**
   * Add connection handler
   */
  onConnection(handler) {
    this.connectionHandlers.add(handler);
  }

  /**
   * Remove connection handler
   */
  offConnection(handler) {
    this.connectionHandlers.delete(handler);
  }

  /**
   * Schedule reconnection attempt
   */
  scheduleReconnect() {
    if (this.reconnectTimer) {
      return;
    }

    this.reconnectTimer = setTimeout(() => {
      console.log('[WebSocket] Attempting to reconnect...');
      this.reconnectTimer = null;
      this.connect(this.token);
    }, this.reconnectDelay);
  }

  /**
   * Clear reconnection timer
   */
  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Send ping to keep connection alive
   */
  ping() {
    this.send({ type: 'ping' });
  }

  /**
   * Get connection status
   */
  getStatus() {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
