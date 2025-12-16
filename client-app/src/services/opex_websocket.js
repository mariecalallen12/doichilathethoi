/**
 * OPEX WebSocket Service
 * Manages WebSocket connection for real-time trading updates
 */

let ws = null
let reconnectAttempts = 0
const maxReconnectAttempts = 5
const reconnectDelay = 3000

export function connectWebSocket(callbacks = {}) {
  // Get WebSocket URL from environment or use default
  let wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  
  // Normalize URL - remove trailing slash and ensure ws:// or wss://
  wsUrl = wsUrl.replace(/\/+$/, '').replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
  
  const wsPath = '/ws/opex'
  const fullUrl = `${wsUrl}${wsPath}`
  
  // Disconnect existing connection if any
  if (ws && ws.readyState !== WebSocket.CLOSED) {
    ws.close()
    ws = null
  }

  try {
    ws = new WebSocket(fullUrl)

    ws.onopen = () => {
      console.log('OPEX WebSocket connected')
      reconnectAttempts = 0
      if (callbacks.onConnected) {
        callbacks.onConnected()
      }

      // Subscribe to channels
      ws.send(JSON.stringify({
        type: 'subscribe',
        channels: ['orders', 'positions', 'prices', 'trades']
      }))
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        
        switch (message.type) {
          case 'connected':
            console.log('WebSocket connected:', message.client_id)
            break
          case 'order':
            if (callbacks.onOrderUpdate) {
              callbacks.onOrderUpdate(message.data)
            }
            break
          case 'position':
            if (callbacks.onPositionUpdate) {
              callbacks.onPositionUpdate(message.data)
            }
            break
          case 'price':
            if (callbacks.onPriceUpdate) {
              callbacks.onPriceUpdate(message.data)
            }
            break
          case 'trade':
            if (callbacks.onTradeUpdate) {
              callbacks.onTradeUpdate(message.data)
            }
            break
          case 'opex_update':
            // Handle OPEX update
            if (callbacks.onOpexUpdate) {
              callbacks.onOpexUpdate(message.data)
            }
            break
          default:
            console.log('Unknown message type:', message.type)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('OPEX WebSocket error:', error)
      if (callbacks.onError) {
        callbacks.onError(error)
      }
    }

    ws.onclose = (event) => {
      console.log('OPEX WebSocket disconnected', event.code, event.reason)
      if (callbacks.onDisconnected) {
        callbacks.onDisconnected(event)
      }

      // Only attempt to reconnect if not a normal closure
      if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++
        console.log(`Reconnecting... (${reconnectAttempts}/${maxReconnectAttempts})`)
        setTimeout(() => {
          connectWebSocket(callbacks)
        }, reconnectDelay)
      } else if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('Max reconnection attempts reached')
        if (callbacks.onError) {
          callbacks.onError(new Error('Max reconnection attempts reached'))
        }
      }
    }
  } catch (error) {
    console.error('Failed to connect WebSocket:', error)
  }

  return ws
}

export function disconnectWebSocket() {
  if (ws) {
    ws.close()
    ws = null
  }
}

export function sendWebSocketMessage(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message))
  } else {
    console.warn('WebSocket is not connected')
  }
}

