import { defineStore } from 'pinia';
import { ref, computed, onMounted, onUnmounted } from 'vue';
import websocketService from '../services/websocket';
import { logError, logInfo } from '../services/utils/logging';
import { useDiagnosticsStore } from './diagnostics';

export const useWebSocketStore = defineStore('websocket', () => {
  const connected = ref(false);
  const reconnectAttempts = ref(0);
  const error = ref(null);
  const lastLatencyMs = ref(null);

  const isConnected = computed(() => connected.value);

  function connect(url) {
    websocketService.connect(url);
    
    websocketService.on('connected', () => {
      connected.value = true;
      error.value = null;
      reconnectAttempts.value = 0;
      logInfo('ws_connected', { url });
    });

    websocketService.on('disconnected', (data) => {
      connected.value = false;
      logInfo('ws_disconnected', data || {});
      // Trigger diagnostic check on disconnect (but not on initial connection failure)
      if (reconnectAttempts.value > 0) {
        try {
          const diagnosticsStore = useDiagnosticsStore();
          if (diagnosticsStore) {
            diagnosticsStore.collectDiagnostics().catch(() => {});
          }
        } catch {
          // Ignore diagnostic errors
        }
      }
    });

    websocketService.on('reconnected', (data) => {
      connected.value = true;
      reconnectAttempts.value = data.attempts || 0;
      logInfo('ws_reconnected', data);
    });

    websocketService.on('error', (err) => {
      error.value = err;
      connected.value = false;
      logError('ws_error', err);
      // Trigger diagnostic check on WebSocket error
      try {
        const diagnosticsStore = useDiagnosticsStore();
        if (diagnosticsStore) {
          diagnosticsStore.collectDiagnostics().catch(() => {});
        }
      } catch {
        // Ignore diagnostic errors
      }
    });

    // Simple latency check via ping/pong
    const pingStart = performance.now();
    websocketService.send({ type: 'ping' });
    const timeout = setTimeout(() => {
      lastLatencyMs.value = null;
    }, 5000);
    websocketService.on('pong', () => {
      clearTimeout(timeout);
      lastLatencyMs.value = performance.now() - pingStart;
      logInfo('ws_latency', { latencyMs: lastLatencyMs.value });
    });

    // Subscribe to diagnostic channel
    websocketService.subscribe('diagnostics', (message) => {
      if (message.type === 'health_update') {
        // Handle health update
        window.dispatchEvent(new CustomEvent('diagnostic-health-change', {
          detail: message.data,
        }));
      } else if (message.type === 'alert') {
        // Handle alert
        window.dispatchEvent(new CustomEvent('diagnostic-alert', {
          detail: message.data || message,
        }));
      }
    });
  }

  function disconnect() {
    websocketService.disconnect();
    connected.value = false;
  }

  function subscribe(instrument, callback) {
    websocketService.subscribe(instrument, callback);
  }

  function unsubscribe(instrument, callback) {
    websocketService.unsubscribe(instrument, callback);
  }

  function send(data) {
    websocketService.send(data);
  }

  return {
    connected,
    reconnectAttempts,
    error,
    lastLatencyMs,
    isConnected,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
  };
});
