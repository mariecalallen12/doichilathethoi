<template>
  <div class="bg-slate-800 rounded-lg p-6">
    <h2 class="text-xl font-semibold text-white mb-4">Update User Balance</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-2">User ID</label>
        <input
          v-model.number="formData.userId"
          type="number"
          min="1"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          required
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Asset</label>
        <input
          v-model="formData.asset"
          type="text"
          placeholder="USDT"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          required
        />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Operation</label>
        <select
          v-model="formData.operation"
          class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          required
        >
          <option value="add">Add</option>
          <option value="subtract">Subtract</option>
          <option value="set">Set</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-2">Amount</label>
        <input
          v-model.number="formData.amount"
          type="number"
          step="0.00000001"
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
          placeholder="Reason for balance adjustment"
        />
      </div>
      
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg disabled:opacity-50 transition-all"
      >
        {{ isSubmitting ? 'Updating...' : 'Update Balance' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../../services/api'

const emit = defineEmits(['balance-updated'])

const isSubmitting = ref(false)
const formData = reactive({
  userId: null,
  asset: '',
  operation: 'add',
  amount: null,
  reason: ''
})

async function handleSubmit() {
  isSubmitting.value = true
  try {
    await api.put(`/api/admin/trading/balances/${formData.userId}`, {
      asset: formData.asset,
      operation: formData.operation,
      amount: formData.amount,
      reason: formData.reason
    })
    
    emit('balance-updated', {
      userId: formData.userId,
      asset: formData.asset,
      operation: formData.operation,
      amount: formData.amount
    })
    
    // Reset form
    formData.userId = null
    formData.asset = ''
    formData.operation = 'add'
    formData.amount = null
    formData.reason = ''
  } catch (error) {
    console.error('Failed to update balance:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

