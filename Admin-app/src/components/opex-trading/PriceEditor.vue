<template>
  <div class="bg-slate-800 rounded-lg p-6">
    <h2 class="text-xl font-semibold text-white mb-4">Update Market Price</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-2">Symbol</label>
        <input
          v-model="formData.symbol"
          type="text"
          placeholder="BTCUSDT"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          required
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">New Price</label>
        <input
          v-model.number="formData.price"
          type="number"
          step="0.01"
          min="0"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          required
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Reason (optional)</label>
        <textarea
          v-model="formData.reason"
          rows="2"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          placeholder="Reason for price adjustment"
        />
      </div>
      
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg disabled:opacity-50 transition-all"
      >
        {{ isSubmitting ? 'Updating...' : 'Update Price' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../../services/api'

const emit = defineEmits(['price-updated'])

const isSubmitting = ref(false)
const formData = reactive({
  symbol: '',
  price: null,
  reason: ''
})

async function handleSubmit() {
  isSubmitting.value = true
  try {
    await api.put(`/api/admin/trading/prices/${formData.symbol}`, {
      price: formData.price,
      reason: formData.reason
    })
    
    emit('price-updated', {
      symbol: formData.symbol,
      price: formData.price
    })
    
    // Reset form
    formData.symbol = ''
    formData.price = null
    formData.reason = ''
  } catch (error) {
    console.error('Failed to update price:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

