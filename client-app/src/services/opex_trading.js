/**
 * OPEX Trading Service
 * API service for trading operations with OPEX backend
 */
import api from './api/client'

const BASE_URL = '/api/trading'

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
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'opex_trading.js:26',message:'getOrders called',data:{params,url:`${BASE_URL}/orders`},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})).catch(()=>{});
    // #endregion
    try {
      const response = await api.get(`${BASE_URL}/orders`, { params })
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'opex_trading.js:29',message:'getOrders success',data:{status:response.status,dataLength:response.data?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})).catch(()=>{});
      // #endregion
      return response.data || []
    } catch (error) {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'opex_trading.js:32',message:'getOrders error',data:{status:error?.response?.status,statusText:error?.response?.statusText,detail:error?.response?.data?.detail,url:error?.config?.url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})).catch(()=>{});
      // #endregion
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
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'opex_trading.js:66',message:'getPositions called',data:{params,url:`${BASE_URL}/positions`},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})).catch(()=>{});
    // #endregion
    try {
      const response = await api.get(`${BASE_URL}/positions`, { params })
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'opex_trading.js:69',message:'getPositions success',data:{status:response.status,dataLength:response.data?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})).catch(()=>{});
      // #endregion
      return response.data || []
    } catch (error) {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'opex_trading.js:72',message:'getPositions error',data:{status:error?.response?.status,statusText:error?.response?.statusText,detail:error?.response?.data?.detail,url:error?.config?.url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})).catch(()=>{});
      // #endregion
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

