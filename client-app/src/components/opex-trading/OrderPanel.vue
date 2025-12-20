<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h2 class="text-lg font-semibold text-white mb-4">Place Order</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Symbol -->
      <div>
        <label class="block text-sm text-purple-200/80 mb-2">Symbol</label>
        <input
          v-model="formData.symbol"
          type="text"
          class="w-full px-3 py-2 bg-slate-700/50 border border-purple-500/20 rounded-lg text-white"
          :value="symbol"
          readonly
        />
      </div>

      <!-- Order Type -->
      <div>
        <label class="block text-sm text-purple-200/80 mb-2">Order Type</label>
        <select
          v-model="formData.type"
          class="w-full px-3 py-2 bg-slate-700/50 border border-purple-500/20 rounded-lg text-white"
        >
          <option value="market">Market</option>
          <option value="limit">Limit</option>
          <option value="stop">Stop</option>
        </select>
      </div>

      <!-- Side -->
      <div>
        <label class="block text-sm text-purple-200/80 mb-2">Side</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            type="button"
            @click="formData.side = 'buy'"
            :class="[
              'px-4 py-2 rounded-lg font-semibold transition-all',
              formData.side === 'buy'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700/50 text-green-400 hover:bg-slate-700/70'
            ]"
          >
            Buy
          </button>
          <button
            type="button"
            @click="formData.side = 'sell'"
            :class="[
              'px-4 py-2 rounded-lg font-semibold transition-all',
              formData.side === 'sell'
                ? 'bg-red-600 text-white'
                : 'bg-slate-700/50 text-red-400 hover:bg-slate-700/70'
            ]"
          >
            Sell
          </button>
        </div>
      </div>

      <!-- Quantity -->
      <div>
        <label class="block text-sm text-purple-200/80 mb-2">Quantity</label>
        <input
          v-model.number="formData.quantity"
          type="number"
          step="0.00000001"
          min="0"
          class="w-full px-3 py-2 bg-slate-700/50 border border-purple-500/20 rounded-lg text-white"
          required
        />
      </div>

      <!-- Price (for limit/stop orders) -->
      <div v-if="formData.type !== 'market'">
        <label class="block text-sm text-purple-200/80 mb-2">Price</label>
        <input
          v-model.number="formData.price"
          type="number"
          step="0.01"
          min="0"
          class="w-full px-3 py-2 bg-slate-700/50 border border-purple-500/20 rounded-lg text-white"
          :required="formData.type !== 'market'"
        />
      </div>

      <!-- Stop Price (for stop orders) -->
      <div v-if="formData.type === 'stop'">
        <label class="block text-sm text-purple-200/80 mb-2">Stop Price</label>
        <input
          v-model.number="formData.stop_price"
          type="number"
          step="0.01"
          min="0"
          class="w-full px-3 py-2 bg-slate-700/50 border border-purple-500/20 rounded-lg text-white"
          required
        />
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm">
        {{ errorMessage }}
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {{ isSubmitting ? 'Placing Order...' : 'Place Order' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  }
})

const emit = defineEmits(['order-placed'])

const isSubmitting = ref(false)
const errorMessage = ref(null)
const formData = reactive({
  symbol: props.symbol,
  side: 'buy',
  type: 'market',
  quantity: 0,
  price: null,
  stop_price: null
})

async function handleSubmit() {
  // Validation
  if (formData.quantity <= 0) {
    errorMessage.value = 'Quantity must be greater than 0'
    return
  }

  if (formData.type !== 'market' && (!formData.price || formData.price <= 0)) {
    errorMessage.value = 'Price is required for limit and stop orders'
    return
  }

  if (formData.type === 'stop' && (!formData.stop_price || formData.stop_price <= 0)) {
    errorMessage.value = 'Stop price is required for stop orders'
    return
  }

  errorMessage.value = null
  isSubmitting.value = true
  
  try {
    const orderData = {
      symbol: formData.symbol,
      side: formData.side,
      type: formData.type,
      quantity: formData.quantity
    }
    
    if (formData.price) {
      orderData.price = formData.price
    }
    
    if (formData.stop_price) {
      orderData.stop_price = formData.stop_price
    }
    
    emit('order-placed', orderData)
    
    // Reset form
    formData.quantity = 0
    formData.price = null
    formData.stop_price = null
    errorMessage.value = null
  } catch (error) {
    console.error('Failed to place order:', error)
    errorMessage.value = error.response?.data?.detail || error.message || 'Failed to place order'
  } finally {
    isSubmitting.value = false
  }
}
</script>

