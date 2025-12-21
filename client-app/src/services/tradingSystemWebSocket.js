/**
 * TRUE REAL-TIME WebSocket Client for TradingSystemAPI
 * =====================================================
 * 
 * Continuous 24/7 WebSocket streaming connection
 * NO polling - pure push-based updates
 */

class TradingSystemWebSocket {
  constructor() {
    // WebSocket connections
    this.marketWs = null;
    this.signalsWs = null;
    this.binaryWs = null;
    
    // Connection state
    this.isMarketConnected = false;
    this.isSignalsConnected = false;
    this.isBinaryConnected = false;
    
    // Callbacks
    this.onMarketUpdate = null;
    this.onSignalUpdate = null;
    this.onBinaryUpdate = null;
    this.onConnectionChange = null;
    
    // Reconnection
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    
    // Heartbeat
    this.heartbeatInterval = 30000; // 30s
    this.heartbeatTimers = {};
  }
  
  /**
   * Get WebSocket base URL
   */
  getWsUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_API_BASE_URL || window.location.origin;
    const cleanHost = host.replace(/^https?:\/\//, '').replace(/\/$/, '');
    
    // In production via Nginx: ws://localhost/ws
    // In development: ws://localhost:8001/ws
    return `${protocol}//${cleanHost}`;
  }
  
  /**
   * Connect to market data stream
   */
  connectMarket(callback) {
    if (this.marketWs && this.marketWs.readyState === WebSocket.OPEN) {
      console.log('[WS] Market already connected');
      return;
    }
    
    this.onMarketUpdate = callback;
    const wsUrl = `${this.getWsUrl()}/ws/market/stream`;
    
    console.log(`[WS] Connecting to market stream: ${wsUrl}`);
    
    try {
      this.marketWs = new WebSocket(wsUrl);
      
      this.marketWs.onopen = () => {
        this.isMarketConnected = true;
        this.reconnectAttempts = 0;
        console.log('[WS] Market stream CONNECTED ✅');
        
        if (this.onConnectionChange) {
          this.onConnectionChange('market', true);
        }
        
        // Start heartbeat
        this.startHeartbeat('market');
      };
      
      this.marketWs.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'market_update' && this.onMarketUpdate) {
            this.onMarketUpdate(message);
          } else if (message.type === 'pong') {
            console.log('[WS] Market heartbeat OK');
          }
        } catch (error) {
          console.error('[WS] Market message parse error:', error);
        }
      };
      
      this.marketWs.onerror = (error) => {
        console.error('[WS] Market error:', error);
      };
      
      this.marketWs.onclose = () => {
        this.isMarketConnected = false;
        console.log('[WS] Market stream DISCONNECTED');
        
        if (this.onConnectionChange) {
          this.onConnectionChange('market', false);
        }
        
        this.stopHeartbeat('market');
        
        // Auto-reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect('market');
        }
      };
      
    } catch (error) {
      console.error('[WS] Market connection error:', error);
      this.scheduleReconnect('market');
    }
  }
  
  /**
   * Connect to trading signals stream
   */
  connectSignals(callback) {
    if (this.signalsWs && this.signalsWs.readyState === WebSocket.OPEN) {
      console.log('[WS] Signals already connected');
      return;
    }
    
    this.onSignalUpdate = callback;
    const wsUrl = `${this.getWsUrl()}/ws/trading/signals/stream`;
    
    console.log(`[WS] Connecting to signals stream: ${wsUrl}`);
    
    try {
      this.signalsWs = new WebSocket(wsUrl);
      
      this.signalsWs.onopen = () => {
        this.isSignalsConnected = true;
        this.reconnectAttempts = 0;
        console.log('[WS] Signals stream CONNECTED ✅');
        
        if (this.onConnectionChange) {
          this.onConnectionChange('signals', true);
        }
        
        this.startHeartbeat('signals');
      };
      
      this.signalsWs.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'signal_update' && this.onSignalUpdate) {
            this.onSignalUpdate(message);
          }
        } catch (error) {
          console.error('[WS] Signals message parse error:', error);
        }
      };
      
      this.signalsWs.onerror = (error) => {
        console.error('[WS] Signals error:', error);
      };
      
      this.signalsWs.onclose = () => {
        this.isSignalsConnected = false;
        console.log('[WS] Signals stream DISCONNECTED');
        
        if (this.onConnectionChange) {
          this.onConnectionChange('signals', false);
        }
        
        this.stopHeartbeat('signals');
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect('signals');
        }
      };
      
    } catch (error) {
      console.error('[WS] Signals connection error:', error);
      this.scheduleReconnect('signals');
    }
  }
  
  /**
   * Connect to binary sentiment stream
   */
  connectBinary(callback) {
    if (this.binaryWs && this.binaryWs.readyState === WebSocket.OPEN) {
      console.log('[WS] Binary already connected');
      return;
    }
    
    this.onBinaryUpdate = callback;
    const wsUrl = `${this.getWsUrl()}/ws/trading/binary/stream`;
    
    console.log(`[WS] Connecting to binary stream: ${wsUrl}`);
    
    try {
      this.binaryWs = new WebSocket(wsUrl);
      
      this.binaryWs.onopen = () => {
        this.isBinaryConnected = true;
        this.reconnectAttempts = 0;
        console.log('[WS] Binary stream CONNECTED ✅');
        
        if (this.onConnectionChange) {
          this.onConnectionChange('binary', true);
        }
        
        this.startHeartbeat('binary');
      };
      
      this.binaryWs.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'binary_update' && this.onBinaryUpdate) {
            this.onBinaryUpdate(message);
          }
        } catch (error) {
          console.error('[WS] Binary message parse error:', error);
        }
      };
      
      this.binaryWs.onerror = (error) => {
        console.error('[WS] Binary error:', error);
      };
      
      this.binaryWs.onclose = () => {
        this.isBinaryConnected = false;
        console.log('[WS] Binary stream DISCONNECTED');
        
        if (this.onConnectionChange) {
          this.onConnectionChange('binary', false);
        }
        
        this.stopHeartbeat('binary');
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect('binary');
        }
      };
      
    } catch (error) {
      console.error('[WS] Binary connection error:', error);
      this.scheduleReconnect('binary');
    }
  }
  
  /**
   * Start heartbeat ping
   */
  startHeartbeat(stream) {
    this.heartbeatTimers[stream] = setInterval(() => {
      const ws = stream === 'market' ? this.marketWs :
                 stream === 'signals' ? this.signalsWs : this.binaryWs;
      
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, this.heartbeatInterval);
  }
  
  /**
   * Stop heartbeat
   */
  stopHeartbeat(stream) {
    if (this.heartbeatTimers[stream]) {
      clearInterval(this.heartbeatTimers[stream]);
      delete this.heartbeatTimers[stream];
    }
  }
  
  /**
   * Schedule reconnection
   */
  scheduleReconnect(stream) {
    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * this.reconnectAttempts, 30000);
    
    console.log(`[WS] Reconnecting ${stream} in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (stream === 'market') {
        this.connectMarket(this.onMarketUpdate);
      } else if (stream === 'signals') {
        this.connectSignals(this.onSignalUpdate);
      } else if (stream === 'binary') {
        this.connectBinary(this.onBinaryUpdate);
      }
    }, delay);
  }
  
  /**
   * Disconnect all streams
   */
  disconnectAll() {
    if (this.marketWs) {
      this.marketWs.close();
      this.marketWs = null;
    }
    
    if (this.signalsWs) {
      this.signalsWs.close();
      this.signalsWs = null;
    }
    
    if (this.binaryWs) {
      this.binaryWs.close();
      this.binaryWs = null;
    }
    
    Object.keys(this.heartbeatTimers).forEach(stream => {
      this.stopHeartbeat(stream);
    });
    
    console.log('[WS] All streams disconnected');
  }
  
  /**
   * Check connection status
   */
  isConnected() {
    return {
      market: this.isMarketConnected,
      signals: this.isSignalsConnected,
      binary: this.isBinaryConnected
    };
  }
}

// Create singleton
const tradingSystemWs = new TradingSystemWebSocket();

export default tradingSystemWs;
