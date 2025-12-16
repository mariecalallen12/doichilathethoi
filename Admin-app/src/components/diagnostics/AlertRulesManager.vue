<template>
  <Card>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold text-white">Alert Rules Management</h2>
      <Button @click="showCreateModal = true">Create Rule</Button>
    </div>

    <!-- Rules List -->
    <div v-if="loading && rules.length === 0" class="text-center py-8 text-gray-400">
      <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
      <p>Loading rules...</p>
    </div>

    <Table v-else-if="rules.length > 0">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>User ID</th>
          <th>Priority</th>
          <th>Enabled</th>
          <th>Created At</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rule in rules" :key="rule.id">
          <td>{{ rule.id }}</td>
          <td>{{ rule.name }}</td>
          <td>{{ rule.user_id || 'System' }}</td>
          <td>{{ rule.priority }}</td>
          <td>
            <span
              :class="[
                'px-2 py-1 rounded text-xs font-semibold',
                rule.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
              ]"
            >
              {{ rule.enabled ? 'Yes' : 'No' }}
            </span>
          </td>
          <td>{{ formatDate(rule.created_at) }}</td>
          <td>
            <div class="flex gap-2">
              <button
                @click="editRule(rule)"
                class="text-purple-400 hover:text-purple-300 transition-colors"
                title="Edit"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="toggleRule(rule)"
                :class="[
                  'transition-colors',
                  rule.enabled ? 'text-yellow-400 hover:text-yellow-300' : 'text-green-400 hover:text-green-300'
                ]"
                :title="rule.enabled ? 'Disable' : 'Enable'"
              >
                <i :class="['fas', rule.enabled ? 'fa-toggle-on' : 'fa-toggle-off']"></i>
              </button>
              <button
                @click="deleteRule(rule)"
                class="text-red-400 hover:text-red-300 transition-colors"
                title="Delete"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </Table>

    <div v-else class="text-center py-8 text-gray-400">
      <i class="fas fa-bell-slash text-3xl mb-2"></i>
      <p>No alert rules found</p>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showCreateModal || editingRule"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="closeModal"
    >
      <div class="bg-slate-800 rounded-lg border border-purple-500/30 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-white">
            {{ editingRule ? 'Edit Alert Rule' : 'Create Alert Rule' }}
          </h3>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form @submit.prevent="saveRule" class="space-y-4">
          <!-- Name -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">
              Rule Name *
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              maxlength="200"
              class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">
              Description
            </label>
            <textarea
              v-model="formData.description"
              rows="2"
              class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          <!-- Conditions -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Conditions
            </label>
            <div class="space-y-2 bg-slate-700/50 rounded-lg p-3">
              <div>
                <label class="block text-xs text-gray-400 mb-1">Health Status</label>
                <select
                  v-model="formData.conditions.health_status"
                  class="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1 text-white text-sm"
                >
                  <option :value="null">Any</option>
                  <option value="unhealthy">Unhealthy</option>
                  <option value="degraded">Degraded</option>
                  <option value="healthy">Healthy</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-400 mb-1">Minimum API Errors</label>
                <input
                  v-model.number="formData.conditions.api_errors.min_count"
                  type="number"
                  min="0"
                  class="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1 text-white text-sm"
                />
              </div>
              <div class="flex items-center gap-2">
                <input
                  v-model="formData.conditions.ws_disconnect"
                  type="checkbox"
                  id="ws-disconnect"
                  class="rounded"
                />
                <label for="ws-disconnect" class="text-xs text-gray-400">
                  Trigger on WebSocket disconnect
                </label>
              </div>
            </div>
          </div>

          <!-- Thresholds -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Thresholds
            </label>
            <div class="space-y-2 bg-slate-700/50 rounded-lg p-3">
              <div>
                <label class="block text-xs text-gray-400 mb-1">Severity Level</label>
                <select
                  v-model="formData.thresholds.severity_level"
                  class="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1 text-white text-sm"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-400 mb-1">Minimum Error Count</label>
                <input
                  v-model.number="formData.thresholds.error_count"
                  type="number"
                  min="0"
                  class="w-full bg-slate-600 border border-slate-500 rounded px-2 py-1 text-white text-sm"
                />
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Actions
            </label>
            <div class="space-y-2 bg-slate-700/50 rounded-lg p-3">
              <div class="flex items-center gap-2">
                <input
                  v-model="formData.actions.notification_types"
                  type="checkbox"
                  value="in_app"
                  id="action-in-app"
                  class="rounded"
                />
                <label for="action-in-app" class="text-xs text-gray-400">
                  In-App Notification
                </label>
              </div>
              <div class="flex items-center gap-2">
                <input
                  v-model="formData.actions.notification_types"
                  type="checkbox"
                  value="email"
                  id="action-email"
                  class="rounded"
                />
                <label for="action-email" class="text-xs text-gray-400">
                  Email Notification
                </label>
              </div>
            </div>
          </div>

          <!-- Priority & Enabled -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-1">
                Priority (1-10)
              </label>
              <input
                v-model.number="formData.priority"
                type="number"
                min="1"
                max="10"
                required
                class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
              />
            </div>
            <div class="flex items-center gap-2 pt-6">
              <input
                v-model="formData.enabled"
                type="checkbox"
                id="enabled"
                class="rounded"
              />
              <label for="enabled" class="text-sm text-gray-300">
                Enabled
              </label>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 pt-4 border-t border-slate-700">
            <Button @click="closeModal" variant="secondary">Cancel</Button>
            <Button type="submit" :loading="saving">
              {{ editingRule ? 'Update' : 'Create' }} Rule
            </Button>
          </div>
        </form>
      </div>
    </div>
  </Card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import Card from '../ui/Card.vue';
import Table from '../ui/Table.vue';
import Button from '../ui/Button.vue';

const rules = ref([]);
const loading = ref(false);
const saving = ref(false);
const showCreateModal = ref(false);
const editingRule = ref(null);

const formData = ref({
  name: '',
  description: '',
  conditions: {
    health_status: null,
    api_errors: {
      min_count: 0,
    },
    ws_disconnect: false,
  },
  thresholds: {
    severity_level: 'medium',
    error_count: 0,
  },
  actions: {
    notification_types: ['in_app'],
  },
  enabled: true,
  priority: 5,
});

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
}

async function fetchRules() {
  loading.value = true;
  try {
    const response = await api.get('/api/alert-rules', {
      params: { limit: 100 },
    });
    rules.value = response.data.rules || [];
  } catch (error) {
    console.error('Error fetching rules:', error);
  } finally {
    loading.value = false;
  }
}

async function saveRule() {
  saving.value = true;
  try {
    const data = {
      name: formData.value.name,
      description: formData.value.description,
      conditions: formData.value.conditions,
      thresholds: formData.value.thresholds,
      actions: formData.value.actions,
      enabled: formData.value.enabled,
      priority: formData.value.priority,
    };

    if (editingRule.value) {
      await api.put(`/api/alert-rules/${editingRule.value.id}`, data);
    } else {
      await api.post('/api/alert-rules', data);
    }

    closeModal();
    fetchRules();
  } catch (error) {
    console.error('Error saving rule:', error);
  } finally {
    saving.value = false;
  }
}

function editRule(rule) {
  editingRule.value = rule;
  formData.value = {
    name: rule.name,
    description: rule.description || '',
    conditions: {
      health_status: rule.conditions?.health_status || null,
      api_errors: {
        min_count: rule.conditions?.api_errors?.min_count || 0,
      },
      ws_disconnect: rule.conditions?.ws_disconnect || false,
    },
    thresholds: {
      severity_level: rule.thresholds?.severity_level || 'medium',
      error_count: rule.thresholds?.error_count || 0,
    },
    actions: {
      notification_types: rule.actions?.notification_types || ['in_app'],
    },
    enabled: rule.enabled,
    priority: rule.priority,
  };
  showCreateModal.value = true;
}

async function toggleRule(rule) {
  try {
    await api.put(`/api/alert-rules/${rule.id}`, {
      enabled: !rule.enabled,
    });
    fetchRules();
  } catch (error) {
    console.error('Error toggling rule:', error);
  }
}

async function deleteRule(rule) {
  if (!confirm(`Are you sure you want to delete "${rule.name}"?`)) {
    return;
  }

  try {
    await api.delete(`/api/alert-rules/${rule.id}`);
    fetchRules();
  } catch (error) {
    console.error('Error deleting rule:', error);
  }
}

function closeModal() {
  showCreateModal.value = false;
  editingRule.value = null;
  formData.value = {
    name: '',
    description: '',
    conditions: {
      health_status: null,
      api_errors: {
        min_count: 0,
      },
      ws_disconnect: false,
    },
    thresholds: {
      severity_level: 'medium',
      error_count: 0,
    },
    actions: {
      notification_types: ['in_app'],
    },
    enabled: true,
    priority: 5,
  };
}

onMounted(() => {
  fetchRules();
});
</script>

