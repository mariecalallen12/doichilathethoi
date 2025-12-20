/**
 * OPEX Trading Service
 * API service for trading operations with OPEX backend
 */
import api from './api/client'

const BASE_URL = '/trading'

export default {
  /**
   * Place a trading order
   */
  async placeOrder(orderData) {
    try {
      const response = await api.post(`${BASE_URL}/orders`, orderData)
      return response.data
    } catch (error) {
      console.error('Failed to place order:', error)
      throw error
    }
  },

  /**
   * Get user's orders
   */
  async getOrders(params = {}) {
    const { debugLog } = await import('../utils/sessionManager')
    debugLog('opex_trading.js:getOrders', 'getOrders called', { params, url: `${BASE_URL}/orders` })
    try {
      const response = await api.get(`${BASE_URL}/orders`, { params })
      debugLog('opex_trading.js:getOrders', 'getOrders success', { status: response.status, dataLength: response.data?.length })
      return response.data || []
    } catch (error) {
      debugLog('opex_trading.js:getOrders', 'getOrders error', { status: error?.response?.status, statusText: error?.response?.statusText, detail: error?.response?.data?.detail, url: error?.config?.url })
      console.error('Failed to get orders:', error)
      // Return empty array on error instead of throwing
      return []
    }
  },

  /**
   * Get trading health status
   */
  async getHealth() {
    try {
      const response = await api.get(`${BASE_URL}/health`)
      return response.data
    } catch (error) {
      console.error('Failed to get trading health:', error)
      return { status: 'unknown', service: 'opex-trading' }
    }
  },

  /**
   * Cancel an order
   */
  async cancelOrder(orderId) {
    try {
      const response = await api.delete(`${BASE_URL}/orders/${orderId}`)
      return response.data
    } catch (error) {
      console.error('Failed to cancel order:', error)
      throw error
    }
  },

  /**
   * Get user's positions
   */
  async getPositions(params = {}) {
    const { debugLog } = await import('../utils/sessionManager')
    debugLog('opex_trading.js:getPositions', 'getPositions called', { params, url: `${BASE_URL}/positions` })
    try {
      const response = await api.get(`${BASE_URL}/positions`, { params })
      debugLog('opex_trading.js:getPositions', 'getPositions success', { status: response.status, dataLength: response.data?.length })
      return response.data || []
    } catch (error) {
      debugLog('opex_trading.js:getPositions', 'getPositions error', { status: error?.response?.status, statusText: error?.response?.statusText, detail: error?.response?.data?.detail, url: error?.config?.url })
      console.error('Failed to get positions:', error)
      // Return empty array on error instead of throwing
      return []
    }
  },

  /**
   * Close a position
   */
  async closePosition(positionId) {
    try {
      const response = await api.post(`${BASE_URL}/positions/${positionId}/close`)
      return response.data
    } catch (error) {
      console.error('Failed to close position:', error)
      throw error
    }
  }
}

