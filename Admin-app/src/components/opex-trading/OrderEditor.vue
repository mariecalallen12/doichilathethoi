<template>
  <div class="bg-slate-800 rounded-lg p-6">
    <h2 class="text-xl font-semibold text-white mb-4">Edit Order</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-2">Order ID</label>
        <input
          v-model="formData.orderId"
          type="text"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          required
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Price</label>
        <input
          v-model.number="formData.price"
          type="number"
          step="0.01"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
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
        <label class="block text-sm text-gray-400 mb-2">Status</label>
        <select
          v-model="formData.status"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
        >
          <option value="pending">Pending</option>
          <option value="open">Open</option>
          <option value="filled">Filled</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg disabled:opacity-50 transition-all"
      >
        {{ isSubmitting ? 'Updating...' : 'Update Order' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../../services/api'

const emit = defineEmits(['order-updated'])

const isSubmitting = ref(false)
const formData = reactive({
  orderId: '',
  price: null,
  quantity: null,
  status: null
})

async function handleSubmit() {
  isSubmitting.value = true
  try {
    const updates = {}
    if (formData.price !== null) updates.price = formData.price
    if (formData.quantity !== null) updates.quantity = formData.quantity
    if (formData.status !== null) updates.status = formData.status
    
    await api.put(`/api/admin/trading/orders/${formData.orderId}`, updates)
    emit('order-updated')
    
    // Reset form
    formData.orderId = ''
    formData.price = null
    formData.quantity = null
    formData.status = null
  } catch (error) {
    console.error('Failed to update order:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

