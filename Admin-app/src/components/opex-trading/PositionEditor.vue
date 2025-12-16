<template>
  <div class="bg-slate-800 rounded-lg p-6">
    <h2 class="text-xl font-semibold text-white mb-4">Edit Position</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-2">Position ID</label>
        <input
          v-model="formData.positionId"
          type="text"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          required
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Quantity</label>
        <input
          v-model.number="formData.quantity"
          type="number"
          step="0.00000001"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Entry Price</label>
        <input
          v-model.number="formData.entryPrice"
          type="number"
          step="0.01"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Leverage</label>
        <input
          v-model.number="formData.leverage"
          type="number"
          step="0.1"
          min="1"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
        />
      </div>
      
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg disabled:opacity-50 transition-all"
      >
        {{ isSubmitting ? 'Updating...' : 'Update Position' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../../services/api'

const emit = defineEmits(['position-updated'])

const isSubmitting = ref(false)
const formData = reactive({
  positionId: '',
  quantity: null,
  entryPrice: null,
  leverage: null
})

async function handleSubmit() {
  isSubmitting.value = true
  try {
    const updates = {}
    if (formData.quantity !== null) updates.quantity = formData.quantity
    if (formData.entryPrice !== null) updates.entry_price = formData.entryPrice
    if (formData.leverage !== null) updates.leverage = formData.leverage
    
    await api.put(`/api/admin/trading/positions/${formData.positionId}`, updates)
    emit('position-updated')
    
    // Reset form
    formData.positionId = ''
    formData.quantity = null
    formData.entryPrice = null
    formData.leverage = null
  } catch (error) {
    console.error('Failed to update position:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

