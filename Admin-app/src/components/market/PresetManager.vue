<template>
  <div class="preset-manager">
    <h3 class="manager-title">
      <i class="fas fa-layer-group text-indigo-400"></i>
      Preset Management
    </h3>

    <!-- Create New Preset -->
    <div class="create-preset-section">
      <button @click="showCreateDialog = true" class="btn-create">
        <i class="fas fa-plus"></i>
        Create Custom Preset
      </button>
    </div>

    <!-- Preset Library -->
    <div class="preset-library">
      <div class="library-header">
        <h4>Preset Library</h4>
        <div class="library-actions">
          <button @click="importPreset" class="btn-action">
            <i class="fas fa-file-import"></i>
            Import
          </button>
          <button @click="exportAll" class="btn-action">
            <i class="fas fa-file-export"></i>
            Export All
          </button>
        </div>
      </div>

      <div class="presets-grid">
        <!-- Built-in Presets -->
        <div class="preset-category">
          <h5 class="category-title">
            <i class="fas fa-star"></i>
            Built-in Presets
          </h5>
          <div class="preset-items">
            <div 
              v-for="preset in builtInPresets" 
              :key="preset.id"
              class="preset-card built-in"
            >
              <div class="preset-header">
                <div class="preset-icon" :style="{ background: preset.color }">
                  <i :class="preset.icon"></i>
                </div>
                <div class="preset-info">
                  <div class="preset-name">{{ preset.name }}</div>
                  <div class="preset-desc">{{ preset.description }}</div>
                </div>
              </div>

              <div class="preset-details">
                <div class="detail-item">
                  <span class="label">Price:</span>
                  <span class="value" :class="getValueClass(preset.config.price_adjustment)">
                    {{ formatAdjustment(preset.config.price_adjustment) }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="label">Signal:</span>
                  <span class="value">{{ preset.config.force_signal }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Confidence:</span>
                  <span class="value positive">
                    +{{ preset.config.confidence_boost }}%
                  </span>
                </div>
              </div>

              <div class="preset-actions">
                <button @click="applyPreset(preset)" class="btn-apply">
                  <i class="fas fa-play"></i>
                  Apply
                </button>
                <button @click="viewPreset(preset)" class="btn-view">
                  <i class="fas fa-eye"></i>
                </button>
                <button @click="exportPreset(preset)" class="btn-export">
                  <i class="fas fa-download"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Custom Presets -->
        <div class="preset-category">
          <h5 class="category-title">
            <i class="fas fa-wrench"></i>
            Custom Presets
          </h5>
          <div v-if="customPresets.length === 0" class="empty-state">
            <i class="fas fa-folder-open text-gray-500 text-3xl mb-2"></i>
            <p class="text-gray-400 text-sm">No custom presets yet</p>
            <button @click="showCreateDialog = true" class="btn-create-small">
              Create First Preset
            </button>
          </div>
          <div v-else class="preset-items">
            <div 
              v-for="preset in customPresets" 
              :key="preset.id"
              class="preset-card custom"
            >
              <div class="preset-header">
                <div class="preset-icon" :style="{ background: preset.color || '#8b5cf6' }">
                  <i :class="preset.icon || 'fas fa-cog'"></i>
                </div>
                <div class="preset-info">
                  <div class="preset-name">{{ preset.name }}</div>
                  <div class="preset-desc">{{ preset.description }}</div>
                </div>
              </div>

              <div class="preset-meta">
                <span class="meta-item">
                  <i class="fas fa-clock"></i>
                  Created: {{ formatDate(preset.created_at) }}
                </span>
                <span class="meta-item">
                  <i class="fas fa-chart-line"></i>
                  Used: {{ preset.usage_count }} times
                </span>
              </div>

              <div class="preset-details">
                <div class="detail-item">
                  <span class="label">Price:</span>
                  <span class="value" :class="getValueClass(preset.config.price_adjustment)">
                    {{ formatAdjustment(preset.config.price_adjustment) }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="label">Signal:</span>
                  <span class="value">{{ preset.config.force_signal || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Confidence:</span>
                  <span class="value positive">
                    {{ formatAdjustment(preset.config.confidence_boost) }}
                  </span>
                </div>
              </div>

              <div class="preset-actions">
                <button @click="applyPreset(preset)" class="btn-apply">
                  <i class="fas fa-play"></i>
                  Apply
                </button>
                <button @click="editPreset(preset)" class="btn-edit">
                  <i class="fas fa-edit"></i>
                </button>
                <button @click="duplicatePreset(preset)" class="btn-duplicate">
                  <i class="fas fa-copy"></i>
                </button>
                <button @click="exportPreset(preset)" class="btn-export">
                  <i class="fas fa-download"></i>
                </button>
                <button @click="deletePreset(preset)" class="btn-delete">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>{{ editingPreset ? 'Edit Preset' : 'Create New Preset' }}</h3>
          <button @click="closeDialog" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label>Preset Name *</label>
            <input 
              v-model="formData.name" 
              type="text" 
              class="form-input"
              placeholder="e.g., Holiday Special Campaign"
            />
          </div>

          <div class="form-group">
            <label>Description *</label>
            <textarea 
              v-model="formData.description" 
              class="form-textarea"
              rows="3"
              placeholder="Describe what this preset does..."
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Icon</label>
              <select v-model="formData.icon" class="form-select">
                <option value="fas fa-rocket">🚀 Rocket</option>
                <option value="fas fa-crown">👑 Crown</option>
                <option value="fas fa-star">⭐ Star</option>
                <option value="fas fa-fire">🔥 Fire</option>
                <option value="fas fa-bolt">⚡ Bolt</option>
                <option value="fas fa-gem">💎 Gem</option>
                <option value="fas fa-trophy">🏆 Trophy</option>
              </select>
            </div>

            <div class="form-group">
              <label>Color</label>
              <input 
                v-model="formData.color" 
                type="color" 
                class="form-color"
              />
            </div>
          </div>

          <div class="config-section">
            <h4>Configuration</h4>

            <div class="form-row">
              <div class="form-group">
                <label>Price Adjustment (%)</label>
                <input 
                  v-model.number="formData.config.price_adjustment" 
                  type="number" 
                  step="0.1"
                  class="form-input"
                  placeholder="e.g., 5.0"
                />
              </div>

              <div class="form-group">
                <label>Change Adjustment (%)</label>
                <input 
                  v-model.number="formData.config.change_adjustment" 
                  type="number" 
                  step="0.1"
                  class="form-input"
                  placeholder="e.g., 2.0"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Force Signal</label>
                <select v-model="formData.config.force_signal" class="form-select">
                  <option :value="null">No Override</option>
                  <option value="STRONG_BUY">STRONG_BUY</option>
                  <option value="BUY">BUY</option>
                  <option value="UP">UP</option>
                  <option value="DOWN">DOWN</option>
                  <option value="SELL">SELL</option>
                  <option value="STRONG_SELL">STRONG_SELL</option>
                </select>
              </div>

              <div class="form-group">
                <label>Confidence Boost (%)</label>
                <input 
                  v-model.number="formData.config.confidence_boost" 
                  type="number" 
                  step="1"
                  class="form-input"
                  placeholder="e.g., 20"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="closeDialog" class="btn-cancel">
            Cancel
          </button>
          <button @click="savePreset" class="btn-save">
            <i class="fas fa-save"></i>
            {{ editingPreset ? 'Update' : 'Create' }} Preset
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const emit = defineEmits(['apply-preset']);

// State
const showCreateDialog = ref(false);
const editingPreset = ref(null);

const builtInPresets = ref([
  {
    id: 'marketing',
    name: 'Marketing Campaign',
    description: 'Bullish campaign for customer acquisition',
    icon: 'fas fa-rocket',
    color: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    config: {
      price_adjustment: 5.0,
      change_adjustment: 2.0,
      force_signal: 'STRONG_BUY',
      confidence_boost: 20.0
    }
  },
  {
    id: 'vip',
    name: 'VIP Treatment',
    description: 'Premium data for VIP clients',
    icon: 'fas fa-crown',
    color: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
    config: {
      price_adjustment: 3.0,
      change_adjustment: 1.5,
      force_signal: 'BUY',
      confidence_boost: 30.0
    }
  },
  {
    id: 'demo',
    name: 'Demo Presentation',
    description: 'Impressive data for presentations',
    icon: 'fas fa-presentation',
    color: 'linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)',
    config: {
      price_adjustment: 10.0,
      change_adjustment: 5.0,
      force_signal: 'STRONG_BUY',
      confidence_boost: 35.0
    }
  },
  {
    id: 'risk_test',
    name: 'Risk Testing',
    description: 'Bearish scenario for risk testing',
    icon: 'fas fa-exclamation-triangle',
    color: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    config: {
      price_adjustment: -5.0,
      change_adjustment: -2.0,
      force_signal: 'STRONG_SELL',
      confidence_boost: 15.0
    }
  },
  {
    id: 'conservative',
    name: 'Conservative Mode',
    description: 'Conservative signals for risk-averse',
    icon: 'fas fa-shield-alt',
    color: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    config: {
      price_adjustment: -1.0,
      change_adjustment: -0.5,
      force_signal: 'UP',
      confidence_boost: -15.0
    }
  }
]);

const customPresets = ref([
  {
    id: 'custom-1',
    name: 'Weekend Boost',
    description: 'Special weekend trading boost',
    icon: 'fas fa-calendar-weekend',
    color: '#ec4899',
    config: {
      price_adjustment: 7.5,
      change_adjustment: 3.0,
      force_signal: 'STRONG_BUY',
      confidence_boost: 25.0
    },
    created_at: '2025-12-15T10:30:00Z',
    usage_count: 12
  }
]);

const formData = reactive({
  name: '',
  description: '',
  icon: 'fas fa-rocket',
  color: '#8b5cf6',
  config: {
    price_adjustment: null,
    change_adjustment: null,
    force_signal: null,
    confidence_boost: null
  }
});

// Methods
const formatAdjustment = (value) => {
  if (value === null || value === undefined) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value}%`;
};

const getValueClass = (value) => {
  if (value > 0) return 'positive';
  if (value < 0) return 'negative';
  return '';
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

const applyPreset = (preset) => {
  emit('apply-preset', preset);
};

const viewPreset = (preset) => {
  alert(JSON.stringify(preset.config, null, 2));
};

const exportPreset = (preset) => {
  const data = JSON.stringify(preset, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `preset-${preset.id}.json`;
  a.click();
};

const exportAll = () => {
  const allPresets = [...builtInPresets.value, ...customPresets.value];
  const data = JSON.stringify(allPresets, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'all-presets.json';
  a.click();
};

const importPreset = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const preset = JSON.parse(event.target.result);
        customPresets.value.push({
          ...preset,
          id: `custom-${Date.now()}`,
          created_at: new Date().toISOString(),
          usage_count: 0
        });
        alert('Preset imported successfully!');
      } catch (error) {
        alert('Failed to import preset: Invalid JSON');
      }
    };
    reader.readAsText(file);
  };
  input.click();
};

const editPreset = (preset) => {
  editingPreset.value = preset;
  Object.assign(formData, JSON.parse(JSON.stringify(preset)));
  showCreateDialog.value = true;
};

const duplicatePreset = (preset) => {
  const duplicate = {
    ...JSON.parse(JSON.stringify(preset)),
    id: `custom-${Date.now()}`,
    name: `${preset.name} (Copy)`,
    created_at: new Date().toISOString(),
    usage_count: 0
  };
  customPresets.value.push(duplicate);
};

const deletePreset = (preset) => {
  if (confirm(`Delete preset "${preset.name}"?`)) {
    const index = customPresets.value.findIndex(p => p.id === preset.id);
    if (index !== -1) {
      customPresets.value.splice(index, 1);
    }
  }
};

const closeDialog = () => {
  showCreateDialog.value = false;
  editingPreset.value = null;
  resetForm();
};

const resetForm = () => {
  formData.name = '';
  formData.description = '';
  formData.icon = 'fas fa-rocket';
  formData.color = '#8b5cf6';
  formData.config = {
    price_adjustment: null,
    change_adjustment: null,
    force_signal: null,
    confidence_boost: null
  };
};

const savePreset = () => {
  if (!formData.name || !formData.description) {
    alert('Please fill in required fields');
    return;
  }

  if (editingPreset.value) {
    // Update existing
    const index = customPresets.value.findIndex(p => p.id === editingPreset.value.id);
    if (index !== -1) {
      customPresets.value[index] = {
        ...customPresets.value[index],
        ...formData
      };
    }
  } else {
    // Create new
    customPresets.value.push({
      ...formData,
      id: `custom-${Date.now()}`,
      created_at: new Date().toISOString(),
      usage_count: 0
    });
  }

  closeDialog();
};
</script>

<style scoped>
.preset-manager {
  padding: 2rem 0;
}

.manager-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.create-preset-section {
  margin-bottom: 2rem;
}

.btn-create {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
}

.preset-library {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
}

.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.library-header h4 {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
}

.library-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-action:hover {
  background: rgba(255, 255, 255, 0.15);
}

.presets-grid {
  display: grid;
  gap: 2rem;
}

.preset-category {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-title {
  font-size: 1rem;
  font-weight: 700;
  color: #d1d5db;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preset-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.preset-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.2s;
}

.preset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.preset-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.preset-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.preset-info {
  flex: 1;
}

.preset-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.25rem;
}

.preset-desc {
  font-size: 0.875rem;
  color: #9ca3af;
}

.preset-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.meta-item {
  font-size: 0.75rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preset-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.detail-item .label {
  color: #9ca3af;
}

.detail-item .value {
  font-weight: 600;
  color: white;
}

.detail-item .value.positive {
  color: #22c55e;
}

.detail-item .value.negative {
  color: #ef4444;
}

.preset-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.preset-actions button {
  flex: 1;
  min-width: 60px;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.btn-apply {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  flex: 2;
}

.btn-view, .btn-edit, .btn-duplicate, .btn-export {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-delete {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 0.75rem;
  border: 2px dashed rgba(255, 255, 255, 0.1);
}

.btn-create-small {
  margin-top: 1rem;
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #6366f1;
  cursor: pointer;
}

/* Dialog Styles */
.dialog-overlay {
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

.dialog-content {
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.dialog-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.btn-close {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
}

.dialog-body {
  padding: 1.5rem;
}

.dialog-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
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

.form-input, .form-textarea, .form-select {
  width: 100%;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
}

.form-color {
  width: 100%;
  height: 50px;
  padding: 0.25rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.config-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.config-section h4 {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
}

.btn-save {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .preset-items {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
