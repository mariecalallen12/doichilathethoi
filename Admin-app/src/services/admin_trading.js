/**
 * Admin Trading Service
 * API service for admin trading operations
 */
import api from './api'

const BASE_URL = '/api/admin/trading'

export default {
  /**
   * Update an order (admin)
   */
  async updateOrder(orderId, updates) {
    const response = await api.put(`${BASE_URL}/orders/${orderId}`, updates)
    return response.data
  },

  /**
   * Force cancel an order (admin)
   */
  async forceCancelOrder(orderId) {
    const response = await api.delete(`${BASE_URL}/orders/${orderId}/force`)
    return response.data
  },

  /**
   * Update a position (admin)
   */
  async updatePosition(positionId, updates) {
    const response = await api.put(`${BASE_URL}/positions/${positionId}`, updates)
    return response.data
  },

  /**
   * Force close a position (admin)
   */
  async forceClosePosition(positionId) {
    const response = await api.post(`${BASE_URL}/positions/${positionId}/force-close`)
    return response.data
  },

  /**
   * Update market price (admin)
   */
  async updatePrice(symbol, price, reason = null) {
    const response = await api.put(`${BASE_URL}/prices/${symbol}`, {
      price,
      reason
    })
    return response.data
  },

  /**
   * Update user balance (admin)
   */
  async updateBalance(userId, balanceData) {
    const response = await api.put(`${BASE_URL}/balances/${userId}`, balanceData)
    return response.data
  },

  /**
   * Get adjustment history
   */
  async getAdjustments(params = {}) {
    const response = await api.get(`${BASE_URL}/adjustments`, { params })
    return response.data
  }
}

