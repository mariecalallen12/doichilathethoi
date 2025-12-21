<template>
  <div class="market-reality-control">
    <!-- Header -->
    <div class="header-section">
      <h1 class="text-3xl font-bold text-white flex items-center gap-3">
        <i class="fas fa-gamepad text-purple-400"></i>
        Market Reality Control Panel
      </h1>
      <p class="text-gray-400 mt-2">
        Control market data customizations in real-time
      </p>
    </div>

    <!-- System Status Banner -->
    <div 
      class="status-banner"
      :class="customizationsEnabled ? 'bg-green-900/30 border-green-500' : 'bg-gray-800/30 border-gray-600'"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div 
            class="status-dot"
            :class="customizationsEnabled ? 'bg-green-400 animate-pulse' : 'bg-gray-500'"
          ></div>
          <span class="text-lg font-semibold">
            Customizations: {{ customizationsEnabled ? 'ENABLED' : 'DISABLED' }}
          </span>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-400">
            Active Rules: {{ activeRulesCount }}
          </span>
          <button
            @click="toggleCustomizations"
            :class="customizationsEnabled ? 'btn-danger' : 'btn-success'"
          >
            <i :class="customizationsEnabled ? 'fas fa-pause' : 'fas fa-play'"></i>
            {{ customizationsEnabled ? 'Disable' : 'Enable' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Warning Banner -->
    <div v-if="customizationsEnabled" class="warning-banner">
      <i class="fas fa-exclamation-triangle"></i>
      <div>
        <strong>WARNING:</strong> Market customizations are active. 
        Data shown to users is MODIFIED. Please use responsibly and ethically.
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Global Market Control -->
      <div class="control-card">
        <h2 class="card-title">
          <i class="fas fa-globe text-blue-400"></i>
          Global Market Manipulation
        </h2>
        
        <div class="form-group">
          <label>Market Mode</label>
          <select v-model="marketMode" @change="applyMarketMode" class="form-select">
            <option value="normal">Normal Mode (Real Data)</option>
            <option value="bullish">Bullish Mode (+5% all)</option>
            <option value="bearish">Bearish Mode (-5% all)</option>
            <option value="custom">Custom Mode</option>
          </select>
        </div>

        <div v-if="marketMode === 'custom'" class="custom-controls">
          <div class="form-group">
            <label>Price Adjustment (%)</label>
            <input 
              v-model.number="globalSettings.priceAdjustment" 
              type="number" 
              step="0.1"
              class="form-input"
              placeholder="e.g., 5.0 for +5%"
            />
          </div>

          <div class="form-group">
            <label>Change Boost (%)</label>
            <input 
              v-model.number="globalSettings.changeAdjustment" 
              type="number" 
              step="0.1"
              class="form-input"
              placeholder="e.g., 2.0 for +2%"
            />
          </div>

          <div class="form-group">
            <label>Force Signal</label>
            <select v-model="globalSettings.forceSignal" class="form-select">
              <option :value="null">No Override</option>
              <option value="STRONG_BUY">STRONG_BUY 🟢🔺</option>
              <option value="BUY">BUY 🟢↗️</option>
              <option value="UP">UP 🟢↑</option>
              <option value="DOWN">DOWN 🔴↓</option>
              <option value="SELL">SELL 🔴↘️</option>
              <option value="STRONG_SELL">STRONG_SELL 🔴🔻</option>
            </select>
          </div>

          <div class="form-group">
            <label>Confidence Boost (%)</label>
            <input 
              v-model.number="globalSettings.confidenceBoost" 
              type="number" 
              step="1"
              class="form-input"
              placeholder="e.g., 20 for +20%"
            />
          </div>

          <button @click="applyGlobalSettings" class="btn-primary w-full">
            <i class="fas fa-check"></i>
            Apply to All Symbols
          </button>
        </div>
      </div>

      <!-- Symbol-Specific Control -->
      <div class="control-card">
        <h2 class="card-title">
          <i class="fas fa-bullseye text-yellow-400"></i>
          Symbol-Specific Control
        </h2>

        <div class="form-group">
          <label>Select Symbol</label>
          <select v-model="selectedSymbol" class="form-select">
            <option v-for="symbol in symbols" :key="symbol" :value="symbol">
              {{ symbol }}
            </option>
          </select>
        </div>

        <div class="override-section">
          <div class="override-item">
            <label class="override-label">
              <input 
                type="checkbox" 
                v-model="overrides.enablePrice"
                class="checkbox"
              />
              <span>Manual Price Override</span>
            </label>
            <input 
              v-model.number="overrides.manualPrice" 
              :disabled="!overrides.enablePrice"
              type="number"
              step="0.01"
              class="form-input"
              placeholder="e.g., 100000.00"
            />
          </div>

          <div class="override-item">
            <label class="override-label">
              <input 
                type="checkbox" 
                v-model="overrides.enableSignal"
                class="checkbox"
              />
              <span>Force Signal</span>
            </label>
            <select 
              v-model="overrides.forceSignal" 
              :disabled="!overrides.enableSignal"
              class="form-select"
            >
              <option value="STRONG_BUY">STRONG_BUY 🟢🔺</option>
              <option value="BUY">BUY 🟢↗️</option>
              <option value="UP">UP 🟢↑</option>
              <option value="DOWN">DOWN 🔴↓</option>
              <option value="SELL">SELL 🔴↘️</option>
              <option value="STRONG_SELL">STRONG_SELL 🔴🔻</option>
            </select>
          </div>

          <div class="override-item">
            <label class="override-label">
              <input 
                type="checkbox" 
                v-model="overrides.enableConfidence"
                class="checkbox"
              />
              <span>Confidence Boost (%)</span>
            </label>
            <input 
              v-model.number="overrides.confidenceBoost" 
              :disabled="!overrides.enableConfidence"
              type="number"
              step="1"
              class="form-input"
              placeholder="e.g., 25"
            />
          </div>

          <button @click="applySymbolOverride" class="btn-primary w-full">
            <i class="fas fa-check"></i>
            Apply to {{ selectedSymbol }}
          </button>
        </div>
      </div>
    </div>

    <!-- Scenario Presets -->
    <div class="control-card">
      <h2 class="card-title">
        <i class="fas fa-theater-masks text-pink-400"></i>
        Scenario Presets
      </h2>

      <div class="presets-grid">
        <button 
          @click="applyPreset('marketing')"
          class="preset-btn preset-marketing"
        >
          <i class="fas fa-rocket"></i>
          <div>
            <div class="preset-title">Marketing Campaign</div>
            <div class="preset-desc">+5% prices, STRONG_BUY, +20% conf</div>
          </div>
        </button>

        <button 
          @click="applyPreset('risk_test')"
          class="preset-btn preset-risk"
        >
          <i class="fas fa-exclamation-triangle"></i>
          <div>
            <div class="preset-title">Risk Testing</div>
            <div class="preset-desc">-5% prices, STRONG_SELL, +15% conf</div>
          </div>
        </button>

        <button 
          @click="applyPreset('vip')"
          class="preset-btn preset-vip"
        >
          <i class="fas fa-crown"></i>
          <div>
            <div class="preset-title">VIP Treatment</div>
            <div class="preset-desc">+3% prices, BUY, +30% conf</div>
          </div>
        </button>

        <button 
          @click="applyPreset('conservative')"
          class="preset-btn preset-conservative"
        >
          <i class="fas fa-shield-alt"></i>
          <div>
            <div class="preset-title">Conservative Mode</div>
            <div class="preset-desc">-1% prices, UP only, -15% conf</div>
          </div>
        </button>

        <button 
          @click="applyPreset('demo')"
          class="preset-btn preset-demo"
        >
          <i class="fas fa-presentation"></i>
          <div>
            <div class="preset-title">Demo Presentation</div>
            <div class="preset-desc">+10% prices, STRONG_BUY, +35% conf</div>
          </div>
        </button>
      </div>
    </div>

    <!-- Active Customizations -->
    <div class="control-card">
      <h2 class="card-title">
        <i class="fas fa-list-check text-green-400"></i>
        Active Customizations
      </h2>

      <div v-if="activeCustomizations.length === 0" class="empty-state">
        <i class="fas fa-inbox text-gray-500 text-4xl mb-3"></i>
        <p class="text-gray-400">No active customizations</p>
      </div>

      <div v-else class="customizations-list">
        <div 
          v-for="(custom, index) in activeCustomizations" 
          :key="index"
          class="customization-item"
        >
          <div class="flex items-start justify-between">
            <div>
              <div class="text-white font-semibold">{{ custom.symbol }}</div>
              <div class="text-sm text-gray-400 mt-1">{{ custom.description }}</div>
            </div>
            <button @click="removeCustomization(custom)" class="btn-sm btn-danger">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="flex gap-3 mt-4">
        <button @click="loadActiveCustomizations" class="btn-secondary">
          <i class="fas fa-sync"></i>
          Refresh
        </button>
        <button @click="clearAllCustomizations" class="btn-danger">
          <i class="fas fa-trash"></i>
          Clear All
        </button>
      </div>
    </div>

    <!-- Real-time Preview Component -->
    <RealTimePreview 
      :api-base-url="API_BASE"
      :symbols="symbols"
      @update="handlePreviewUpdate"
    />

    <!-- Emergency Reset -->
    <div class="emergency-section">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-xl font-bold text-white mb-1">
            <i class="fas fa-exclamation-circle text-red-400"></i>
            Emergency Reset
          </h3>
          <p class="text-gray-400 text-sm">
            Immediately disable and clear all customizations
          </p>
        </div>
        <button @click="emergencyReset" class="btn-emergency">
          <i class="fas fa-power-off"></i>
          EMERGENCY RESET
        </button>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin text-4xl text-purple-400"></i>
        <p class="mt-3 text-white">Processing...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import RealTimePreview from '@/components/market/RealTimePreview.vue';

// API base URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
const API_URL = `${API_BASE}/admin/market-control`;

// State
const loading = ref(false);
const customizationsEnabled = ref(true);
const marketMode = ref('normal');
const selectedSymbol = ref('BTC');
const symbols = ref(['BTC', 'ETH', 'XRP', 'SOL', 'ADA', 'DOT', 'AVAX', 'MATIC', 'LINK', 'UNI']);

const globalSettings = ref({
  priceAdjustment: 5.0,
  changeAdjustment: 2.0,
  forceSignal: null,
  confidenceBoost: 20.0
});

const overrides = ref({
  enablePrice: false,
  manualPrice: 100000,
  enableSignal: false,
  forceSignal: 'STRONG_BUY',
  enableConfidence: false,
  confidenceBoost: 25
});

const activeCustomizations = ref([]);
const activeRulesCount = computed(() => activeCustomizations.value.length);

const previewData = ref([]);

// Methods
const handlePreviewUpdate = (data) => {
  previewData.value = data;
};

const showNotification = (message, type = 'success') => {
  // TODO: Integrate with toast notification system
  console.log(`[${type.toUpperCase()}]`, message);
  alert(message);
};

const applyMarketMode = async () => {
  if (marketMode.value === 'normal') {
    await clearAllCustomizations();
    return;
  }

  if (marketMode.value === 'custom') {
    return; // Wait for manual application
  }

  // Auto-apply preset modes
  const presetMap = {
    bullish: 'marketing',
    bearish: 'risk_test'
  };

  const preset = presetMap[marketMode.value];
  if (preset) {
    await applyPreset(preset);
  }
};

const applyGlobalSettings = async () => {
  loading.value = true;
  try {
    const response = await axios.post(`${API_URL}/global`, {
      price_adjustment: globalSettings.value.priceAdjustment,
      change_adjustment: globalSettings.value.changeAdjustment,
      force_signal: globalSettings.value.forceSignal,
      confidence_boost: globalSettings.value.confidenceBoost
    });

    if (response.data.success) {
      showNotification('Global customizations applied successfully!');
      await loadActiveCustomizations();
    }
  } catch (error) {
    console.error('Error applying global settings:', error);
    showNotification('Failed to apply global settings', 'error');
  } finally {
    loading.value = false;
  }
};

const applySymbolOverride = async () => {
  loading.value = true;
  try {
    const data = {};
    
    if (overrides.value.enablePrice) {
      data.manual_price = overrides.value.manualPrice;
    }
    if (overrides.value.enableSignal) {
      data.force_signal = overrides.value.forceSignal;
    }
    if (overrides.value.enableConfidence) {
      data.confidence_boost = overrides.value.confidenceBoost;
    }

    const response = await axios.post(`${API_URL}/symbol/${selectedSymbol.value}`, data);

    if (response.data.success) {
      showNotification(`Customizations applied to ${selectedSymbol.value}!`);
      await loadActiveCustomizations();
    }
  } catch (error) {
    console.error('Error applying symbol override:', error);
    showNotification(`Failed to apply customizations to ${selectedSymbol.value}`, 'error');
  } finally {
    loading.value = false;
  }
};

const applyPreset = async (presetName) => {
  loading.value = true;
  try {
    const response = await axios.post(`${API_URL}/preset/${presetName}`);

    if (response.data.success) {
      showNotification(`Preset "${response.data.preset}" applied successfully!`);
      await loadActiveCustomizations();
      customizationsEnabled.value = true;
    }
  } catch (error) {
    console.error('Error applying preset:', error);
    showNotification(`Failed to apply preset "${presetName}"`, 'error');
  } finally {
    loading.value = false;
  }
};

const toggleCustomizations = async () => {
  loading.value = true;
  try {
    const newState = !customizationsEnabled.value;
    const response = await axios.post(`${API_URL}/toggle?enabled=${newState}`);

    if (response.data.success) {
      customizationsEnabled.value = newState;
      showNotification(`Customizations ${newState ? 'enabled' : 'disabled'}!`);
    }
  } catch (error) {
    console.error('Error toggling customizations:', error);
    showNotification('Failed to toggle customizations', 'error');
  } finally {
    loading.value = false;
  }
};

const loadActiveCustomizations = async () => {
  try {
    const response = await axios.get(`${API_URL}/active`);
    
    // Transform active rules into display format
    const rules = response.data.active_rules || [];
    const manualOverrides = response.data.manual_overrides || {};
    
    activeCustomizations.value = [];
    
    // Add rules
    rules.forEach(ruleName => {
      activeCustomizations.value.push({
        symbol: '*',
        description: `Rule: ${ruleName}`,
        type: 'rule',
        name: ruleName
      });
    });
    
    // Add manual price overrides
    Object.entries(manualOverrides.prices || {}).forEach(([symbol, price]) => {
      activeCustomizations.value.push({
        symbol,
        description: `Manual price: ${price}`,
        type: 'price'
      });
    });
    
    // Add signal overrides
    Object.entries(manualOverrides.signals || {}).forEach(([symbol, signal]) => {
      activeCustomizations.value.push({
        symbol,
        description: `Force signal: ${signal}`,
        type: 'signal'
      });
    });
    
    customizationsEnabled.value = response.data.enabled;
  } catch (error) {
    console.error('Error loading active customizations:', error);
  }
};

const clearAllCustomizations = async () => {
  if (!confirm('Are you sure you want to clear ALL customizations?')) {
    return;
  }

  loading.value = true;
  try {
    const response = await axios.delete(`${API_URL}/clear`);

    if (response.data.success) {
      showNotification('All customizations cleared!');
      await loadActiveCustomizations();
      marketMode.value = 'normal';
      customizationsEnabled.value = false;
    }
  } catch (error) {
    console.error('Error clearing customizations:', error);
    showNotification('Failed to clear customizations', 'error');
  } finally {
    loading.value = false;
  }
};

const removeCustomization = async (custom) => {
  // TODO: Implement individual customization removal
  showNotification('Individual removal coming soon. Use "Clear All" for now.', 'info');
};

const emergencyReset = async () => {
  if (!confirm('⚠️ EMERGENCY RESET: This will immediately disable and clear ALL customizations. Continue?')) {
    return;
  }

  loading.value = true;
  try {
    await axios.delete(`${API_URL}/clear`);
    await axios.post(`${API_URL}/toggle?enabled=false`);
    
    showNotification('🚨 Emergency reset completed!', 'warning');
    await loadActiveCustomizations();
    marketMode.value = 'normal';
    customizationsEnabled.value = false;
  } catch (error) {
    console.error('Error during emergency reset:', error);
    showNotification('Emergency reset failed!', 'error');
  } finally {
    loading.value = false;
  }
};

// Lifecycle
onMounted(() => {
  loadActiveCustomizations();
});
</script>

<style scoped>
.market-reality-control {
  padding: 2rem;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
}

.header-section {
  margin-bottom: 2rem;
}

.status-banner {
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 2px solid;
  margin-bottom: 1.5rem;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.warning-banner {
  background: rgba(239, 68, 68, 0.1);
  border: 2px solid #ef4444;
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #fca5a5;
  margin-bottom: 1.5rem;
}

.warning-banner i {
  font-size: 1.5rem;
}

.control-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  color: #d1d5db;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.form-input, .form-select {
  width: 100%;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #a78bfa;
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.custom-controls {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.override-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.override-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.override-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #d1d5db;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.checkbox {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.preset-btn {
  padding: 1rem;
  border-radius: 0.75rem;
  border: 2px solid;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.preset-btn i {
  font-size: 1.5rem;
}

.preset-title {
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.preset-desc {
  font-size: 0.75rem;
  opacity: 0.8;
}

.preset-marketing {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
  color: #22c55e;
}

.preset-marketing:hover {
  background: rgba(34, 197, 94, 0.2);
}

.preset-risk {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  color: #ef4444;
}

.preset-risk:hover {
  background: rgba(239, 68, 68, 0.2);
}

.preset-vip {
  background: rgba(251, 191, 36, 0.1);
  border-color: #fbbf24;
  color: #fbbf24;
}

.preset-vip:hover {
  background: rgba(251, 191, 36, 0.2);
}

.preset-conservative {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
  color: #3b82f6;
}

.preset-conservative:hover {
  background: rgba(59, 130, 246, 0.2);
}

.preset-demo {
  background: rgba(168, 85, 247, 0.1);
  border-color: #a855f7;
  color: #a855f7;
}

.preset-demo:hover {
  background: rgba(168, 85, 247, 0.2);
}

.customizations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.customization-item {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.emergency-section {
  background: rgba(239, 68, 68, 0.1);
  border: 2px solid #ef4444;
  padding: 1.5rem;
  border-radius: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
}

.btn-success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(34, 197, 94, 0.3);
}

.btn-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.btn-emergency {
  background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
  color: white;
  padding: 1rem 2rem;
  border-radius: 0.5rem;
  font-weight: 700;
  font-size: 1.125rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 0 30px rgba(220, 38, 38, 0.5);
}

.btn-emergency:hover {
  transform: scale(1.05);
  box-shadow: 0 0 40px rgba(220, 38, 38, 0.7);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
}

.loading-spinner {
  text-align: center;
}

@media (max-width: 768px) {
  .market-reality-control {
    padding: 1rem;
  }

  .presets-grid {
    grid-template-columns: 1fr;
  }
}
</style>
