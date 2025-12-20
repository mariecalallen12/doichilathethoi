<template>
  <div class="simulation-control p-6 min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold text-white mb-2">Simulation Control</h1>
      <p class="text-purple-200/80 mb-6">Manage market data simulation and scenarios</p>
      
      <!-- Status Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-4">
          <div class="text-sm text-gray-400 mb-1">Status</div>
          <div class="text-xl font-bold">
            <span :class="status.is_running ? 'text-green-400' : 'text-red-400'">
              {{ status.is_running ? '▶ Running' : '⏸ Stopped' }}
            </span>
          </div>
        </div>
        
        <div class="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-4">
          <div class="text-sm text-gray-400 mb-1">Uptime</div>
          <div class="text-xl font-bold text-white">{{ formatUptime(status.uptime_seconds) }}</div>
        </div>
        
        <div class="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-4">
          <div class="text-sm text-gray-400 mb-1">Active Scenario</div>
          <div class="text-sm font-semibold text-purple-200">
            {{ status.current_scenario?.name || 'None' }}
          </div>
        </div>
        
        <div class="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-4">
          <div class="text-sm text-gray-400 mb-1">Symbols</div>
          <div class="text-xl font-bold text-white">{{ status.symbols?.length || 0 }}</div>
        </div>
      </div>
      
      <!-- Control Buttons -->
      <div class="flex gap-3 mb-6 flex-wrap">
        <button v-if="!status.is_running" 
                @click="startSimulation"
                class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors">
          ▶ Start Simulation
        </button>
        <button v-else 
                @click="stopSimulation"
                class="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors">
          ⏸ Stop Simulation
        </button>
        <button @click="restartSimulation" 
                class="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-semibold transition-colors">
          🔄 Restart
        </button>
        <button @click="resetPrices" 
                class="px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white rounded-lg font-semibold transition-colors">
          ↺ Reset Prices
        </button>
      </div>
      
      <!-- Current Prices -->
      <div class="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-semibold text-white mb-4">Current Prices</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div v-for="(price, symbol) in status.current_prices" 
               :key="symbol"
               class="bg-slate-700/50 rounded-lg p-4">
            <div class="text-xs text-gray-400 mb-1">{{ symbol }}</div>
            <div class="text-lg font-bold text-white">${{ formatPrice(price) }}</div>
          </div>
        </div>
      </div>
      
      <!-- Configuration -->
      <div class="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-6">
        <h2 class="text-xl font-semibold text-white mb-4">Configuration</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm text-gray-400 mb-2">Volatility (%)</label>
            <input v-model.number="config.volatility" 
                   type="number" min="0.1" max="10" step="0.1"
                   class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white" />
            <div class="text-xs text-gray-500 mt-1">Current: {{ (status.volatility * 100).toFixed(1) }}%</div>
          </div>
          
          <div>
            <label class="block text-sm text-gray-400 mb-2">Trend</label>
            <select v-model="config.trend" 
                    class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white">
              <option value="up">📈 Up (Bull)</option>
              <option value="down">📉 Down (Bear)</option>
              <option value="sideways">↔️ Sideways</option>
            </select>
            <div class="text-xs text-gray-500 mt-1">Current: {{ status.trend }}</div>
          </div>
          
          <div>
            <label class="block text-sm text-gray-400 mb-2">Volume Multiplier</label>
            <input v-model.number="config.volume_multiplier" 
                   type="number" min="0.1" max="10" step="0.1"
                   class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white" />
            <div class="text-xs text-gray-500 mt-1">Current: {{ status.volume_multiplier }}x</div>
          </div>
        </div>
        
        <button @click="updateConfig" 
                class="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors">
          Update Configuration
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../services/api'

const status = ref({
  is_running: false,
  current_scenario: null,
  symbols: [],
  current_prices: {},
  uptime_seconds: 0,
  volatility: 0.005,
  trend: 'sideways',
  volume_multiplier: 1.0
})

const config = ref({
  volatility: 0.5,
  trend: 'sideways',
  volume_multiplier: 1.0
})

let statusInterval = null

async function loadStatus() {
  try {
    const response = await api.get('/api/admin/simulation/status')
    status.value = response.data
    
    // Sync config with current status
    config.value.volatility = (status.value.volatility * 100).toFixed(1)
    config.value.trend = status.value.trend
    config.value.volume_multiplier = status.value.volume_multiplier
  } catch (error) {
    console.error('Failed to load status:', error)
  }
}

async function startSimulation() {
  try {
    await api.post('/api/admin/simulation/start')
    showToast('Simulation started', 'success')
    await loadStatus()
  } catch (error) {
    showToast('Failed to start simulation', 'error')
  }
}

async function stopSimulation() {
  try {
    await api.post('/api/admin/simulation/stop')
    showToast('Simulation stopped', 'success')
    await loadStatus()
  } catch (error) {
    showToast('Failed to stop simulation', 'error')
  }
}

async function restartSimulation() {
  try {
    await api.post('/api/admin/simulation/restart')
    showToast('Simulation restarted', 'success')
    await loadStatus()
  } catch (error) {
    showToast('Failed to restart simulation', 'error')
  }
}

async function resetPrices() {
  try {
    await api.post('/api/admin/simulation/reset-prices')
    showToast('Prices reset', 'success')
    await loadStatus()
  } catch (error) {
    showToast('Failed to reset prices', 'error')
  }
}

async function updateConfig() {
  try {
    await api.put('/api/admin/simulation/config', {
      volatility: parseFloat(config.value.volatility) / 100,
      trend: config.value.trend,
      volume_multiplier: parseFloat(config.value.volume_multiplier)
    })
    showToast('Configuration updated', 'success')
    await loadStatus()
  } catch (error) {
    showToast('Failed to update config', 'error')
  }
}

function formatUptime(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

function formatPrice(price) {
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function showToast(message, type) {
  console.log(`[${type}] ${message}`)
}

onMounted(() => {
  loadStatus()
  statusInterval = setInterval(loadStatus, 5000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>
