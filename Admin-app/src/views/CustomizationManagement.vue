<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

// State
const rules = ref([]);
const sessions = ref([]);
const loading = ref(false);
const activeTab = ref('rules'); // 'rules' or 'sessions'
const systemStatus = ref(null);

// Modal states
const showRuleModal = ref(false);
const showSessionModal = ref(false);
const editingRule = ref(null);

// Form data
const ruleForm = ref({
  name: '',
  symbol: '*',
  price_adjustment: null,
  change_adjustment: null,
  force_signal: null,
  confidence_boost: null,
  custom_volume: null,
  custom_market_cap: null,
  enabled: true
});

const sessionForm = ref({
  name: ''
});

// API base URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Computed
const filteredRules = computed(() => {
  return rules.value.filter(r => r.enabled);
});

const activeSessions = computed(() => {
  return sessions.value.filter(s => s.enabled);
});

// Methods
const fetchRules = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${API_BASE}/api/admin/customizations/rules`);
    rules.value = response.data;
  } catch (error) {
    console.error('Error fetching rules:', error);
    alert('Failed to fetch rules');
  } finally {
    loading.value = false;
  }
};

const fetchSessions = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${API_BASE}/api/admin/customizations/sessions`);
    sessions.value = response.data;
  } catch (error) {
    console.error('Error fetching sessions:', error);
    alert('Failed to fetch sessions');
  } finally {
    loading.value = false;
  }
};

const fetchSystemStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/admin/customizations/status`);
    systemStatus.value = response.data;
  } catch (error) {
    console.error('Error fetching status:', error);
  }
};

const createRule = async () => {
  loading.value = true;
  try {
    if (editingRule.value) {
      // Update existing rule
      await axios.put(
        `${API_BASE}/api/admin/customizations/rules/${editingRule.value.name}`,
        ruleForm.value
      );
    } else {
      // Create new rule
      await axios.post(`${API_BASE}/api/admin/customizations/rules`, ruleForm.value);
    }
    
    showRuleModal.value = false;
    resetRuleForm();
    await fetchRules();
    alert(editingRule.value ? 'Rule updated!' : 'Rule created!');
  } catch (error) {
    console.error('Error saving rule:', error);
    alert('Failed to save rule: ' + (error.response?.data?.detail || error.message));
  } finally {
    loading.value = false;
  }
};

const deleteRule = async (ruleName) => {
  if (!confirm(`Delete rule "${ruleName}"?`)) return;
  
  loading.value = true;
  try {
    await axios.delete(`${API_BASE}/api/admin/customizations/rules/${ruleName}`);
    await fetchRules();
    alert('Rule deleted!');
  } catch (error) {
    console.error('Error deleting rule:', error);
    alert('Failed to delete rule');
  } finally {
    loading.value = false;
  }
};

const createSession = async () => {
  loading.value = true;
  try {
    await axios.post(`${API_BASE}/api/admin/customizations/sessions`, sessionForm.value);
    showSessionModal.value = false;
    sessionForm.value.name = '';
    await fetchSessions();
    alert('Session created!');
  } catch (error) {
    console.error('Error creating session:', error);
    alert('Failed to create session');
  } finally {
    loading.value = false;
  }
};

const deleteSession = async (sessionId) => {
  if (!confirm('Delete this session?')) return;
  
  loading.value = true;
  try {
    await axios.delete(`${API_BASE}/api/admin/customizations/sessions/${sessionId}`);
    await fetchSessions();
    alert('Session deleted!');
  } catch (error) {
    console.error('Error deleting session:', error);
    alert('Failed to delete session');
  } finally {
    loading.value = false;
  }
};

const toggleSessionStatus = async (session) => {
  loading.value = true;
  try {
    const endpoint = session.enabled ? 'deactivate' : 'activate';
    await axios.post(`${API_BASE}/api/admin/customizations/sessions/${session.session_id}/${endpoint}`);
    await fetchSessions();
  } catch (error) {
    console.error('Error toggling session:', error);
    alert('Failed to toggle session status');
  } finally {
    loading.value = false;
  }
};

const openRuleModal = (rule = null) => {
  if (rule) {
    editingRule.value = rule;
    ruleForm.value = { ...rule };
  } else {
    editingRule.value = null;
    resetRuleForm();
  }
  showRuleModal.value = true;
};

const resetRuleForm = () => {
  ruleForm.value = {
    name: '',
    symbol: '*',
    price_adjustment: null,
    change_adjustment: null,
    force_signal: null,
    confidence_boost: null,
    custom_volume: null,
    custom_market_cap: null,
    enabled: true
  };
};

const viewSessionDetails = (session) => {
  router.push(`/customization/sessions/${session.session_id}`);
};

// Lifecycle
onMounted(async () => {
  await Promise.all([
    fetchRules(),
    fetchSessions(),
    fetchSystemStatus()
  ]);
});
</script>

<template>
  <div class="min-h-screen bg-gradient-admin p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-2">
          <i class="fas fa-sliders-h mr-3"></i>
          Customization Management
        </h1>
        <p class="text-white/70">
          Manage data customization rules and sessions for market data and trading signals
        </p>
      </div>

      <!-- System Status Card -->
      <div v-if="systemStatus" class="bg-white/10 rounded-lg p-6 mb-6 backdrop-blur-sm">
        <h2 class="text-xl font-semibold text-white mb-4">
          <i class="fas fa-chart-line mr-2"></i>
          System Status
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center">
            <div class="text-3xl font-bold text-primary">{{ systemStatus.total_rules }}</div>
            <div class="text-sm text-white/70">Total Rules</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold text-primary">{{ systemStatus.total_sessions }}</div>
            <div class="text-sm text-white/70">Total Sessions</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold text-green-400">
              {{ systemStatus.manual_overrides?.prices || 0 }}
            </div>
            <div class="text-sm text-white/70">Price Overrides</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold text-yellow-400">
              {{ systemStatus.global_enabled ? 'ON' : 'OFF' }}
            </div>
            <div class="text-sm text-white/70">Global Status</div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-4 mb-6">
        <button
          @click="activeTab = 'rules'"
          :class="[
            'px-6 py-3 rounded-lg font-semibold transition-all',
            activeTab === 'rules'
              ? 'bg-primary text-white shadow-lg'
              : 'bg-white/10 text-white/70 hover:bg-white/20'
          ]"
        >
          <i class="fas fa-list-ul mr-2"></i>
          Rules ({{ rules.length }})
        </button>
        <button
          @click="activeTab = 'sessions'"
          :class="[
            'px-6 py-3 rounded-lg font-semibold transition-all',
            activeTab === 'sessions'
              ? 'bg-primary text-white shadow-lg'
              : 'bg-white/10 text-white/70 hover:bg-white/20'
          ]"
        >
          <i class="fas fa-clock mr-2"></i>
          Sessions ({{ sessions.length }})
        </button>
      </div>

      <!-- Rules Tab -->
      <div v-if="activeTab === 'rules'" class="space-y-6">
        <!-- Actions -->
        <div class="flex justify-end">
          <button
            @click="openRuleModal()"
            class="bg-gradient-button text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all"
          >
            <i class="fas fa-plus mr-2"></i>
            Create New Rule
          </button>
        </div>

        <!-- Rules List -->
        <div class="bg-white/10 rounded-lg backdrop-blur-sm overflow-hidden">
          <table class="w-full">
            <thead class="bg-white/5">
              <tr>
                <th class="px-6 py-4 text-left text-white font-semibold">Name</th>
                <th class="px-6 py-4 text-left text-white font-semibold">Symbol</th>
                <th class="px-6 py-4 text-left text-white font-semibold">Price Adj.</th>
                <th class="px-6 py-4 text-left text-white font-semibold">Signal</th>
                <th class="px-6 py-4 text-left text-white font-semibold">Status</th>
                <th class="px-6 py-4 text-left text-white font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="rule in rules"
                :key="rule.name"
                class="border-t border-white/10 hover:bg-white/5 transition-colors"
              >
                <td class="px-6 py-4 text-white font-medium">{{ rule.name }}</td>
                <td class="px-6 py-4 text-white/80">{{ rule.symbol }}</td>
                <td class="px-6 py-4 text-white/80">
                  <span v-if="rule.price_adjustment" class="text-green-400">
                    {{ rule.price_adjustment > 0 ? '+' : '' }}{{ rule.price_adjustment }}%
                  </span>
                  <span v-else class="text-white/40">—</span>
                </td>
                <td class="px-6 py-4 text-white/80">
                  <span v-if="rule.force_signal" class="px-2 py-1 bg-primary/20 text-primary rounded text-sm">
                    {{ rule.force_signal }}
                  </span>
                  <span v-else class="text-white/40">—</span>
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="[
                      'px-3 py-1 rounded-full text-sm font-semibold',
                      rule.enabled
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    ]"
                  >
                    {{ rule.enabled ? 'Active' : 'Disabled' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex gap-2">
                    <button
                      @click="openRuleModal(rule)"
                      class="text-blue-400 hover:text-blue-300 transition-colors"
                      title="Edit"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      @click="deleteRule(rule.name)"
                      class="text-red-400 hover:text-red-300 transition-colors"
                      title="Delete"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="rules.length === 0" class="text-center py-12 text-white/50">
            <i class="fas fa-inbox text-4xl mb-4"></i>
            <p>No rules created yet</p>
          </div>
        </div>
      </div>

      <!-- Sessions Tab -->
      <div v-if="activeTab === 'sessions'" class="space-y-6">
        <!-- Actions -->
        <div class="flex justify-end">
          <button
            @click="showSessionModal = true"
            class="bg-gradient-button text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all"
          >
            <i class="fas fa-plus mr-2"></i>
            Create New Session
          </button>
        </div>

        <!-- Sessions Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="session in sessions"
            :key="session.session_id"
            class="bg-white/10 rounded-lg p-6 backdrop-blur-sm hover:bg-white/15 transition-all cursor-pointer"
            @click="viewSessionDetails(session)"
          >
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-lg font-semibold text-white">{{ session.name }}</h3>
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-semibold',
                  session.enabled
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-gray-500/20 text-gray-400'
                ]"
              >
                {{ session.enabled ? 'Active' : 'Inactive' }}
              </span>
            </div>

            <div class="text-sm text-white/70 mb-4">
              <p>Session ID: {{ session.session_id.substring(0, 8) }}...</p>
              <p>Rules: {{ session.rule_names?.length || 0 }}</p>
              <p>Created: {{ new Date(session.created_at).toLocaleDateString() }}</p>
            </div>

            <div class="flex gap-2" @click.stop>
              <button
                @click="toggleSessionStatus(session)"
                :class="[
                  'flex-1 py-2 rounded font-semibold transition-all',
                  session.enabled
                    ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                    : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                ]"
              >
                <i :class="['fas mr-2', session.enabled ? 'fa-pause' : 'fa-play']"></i>
                {{ session.enabled ? 'Deactivate' : 'Activate' }}
              </button>
              <button
                @click="deleteSession(session.session_id)"
                class="py-2 px-4 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-all"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>

        <div v-if="sessions.length === 0" class="text-center py-12 text-white/50 bg-white/10 rounded-lg">
          <i class="fas fa-calendar-times text-4xl mb-4"></i>
          <p>No sessions created yet</p>
        </div>
      </div>

      <!-- Rule Modal -->
      <div
        v-if="showRuleModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showRuleModal = false"
      >
        <div class="bg-gray-900 rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <h2 class="text-2xl font-bold text-white mb-6">
            {{ editingRule ? 'Edit Rule' : 'Create New Rule' }}
          </h2>

          <form @submit.prevent="createRule" class="space-y-4">
            <div>
              <label class="block text-white/80 mb-2">Rule Name*</label>
              <input
                v-model="ruleForm.name"
                type="text"
                required
                :disabled="!!editingRule"
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:border-primary"
                placeholder="e.g., BTC_BULLISH"
              />
            </div>

            <div>
              <label class="block text-white/80 mb-2">Symbol*</label>
              <input
                v-model="ruleForm.symbol"
                type="text"
                required
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:border-primary"
                placeholder="BTC, ETH, or * for all"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-white/80 mb-2">Price Adjustment (%)</label>
                <input
                  v-model.number="ruleForm.price_adjustment"
                  type="number"
                  step="0.1"
                  class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:border-primary"
                  placeholder="e.g., 5.0"
                />
              </div>

              <div>
                <label class="block text-white/80 mb-2">Change Adjustment (%)</label>
                <input
                  v-model.number="ruleForm.change_adjustment"
                  type="number"
                  step="0.1"
                  class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:border-primary"
                  placeholder="e.g., 3.0"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-white/80 mb-2">Force Signal</label>
                <select
                  v-model="ruleForm.force_signal"
                  class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:border-primary"
                >
                  <option :value="null">None</option>
                  <option value="STRONG_BUY">STRONG_BUY</option>
                  <option value="BUY">BUY</option>
                  <option value="NEUTRAL">NEUTRAL</option>
                  <option value="SELL">SELL</option>
                  <option value="STRONG_SELL">STRONG_SELL</option>
                </select>
              </div>

              <div>
                <label class="block text-white/80 mb-2">Confidence Boost (%)</label>
                <input
                  v-model.number="ruleForm.confidence_boost"
                  type="number"
                  step="0.1"
                  class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:border-primary"
                  placeholder="e.g., 20.0"
                />
              </div>
            </div>

            <div>
              <label class="flex items-center text-white/80">
                <input
                  v-model="ruleForm.enabled"
                  type="checkbox"
                  class="mr-2 w-4 h-4"
                />
                Enable this rule
              </label>
            </div>

            <div class="flex gap-4 mt-6">
              <button
                type="submit"
                class="flex-1 bg-gradient-button text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all"
                :disabled="loading"
              >
                {{ editingRule ? 'Update Rule' : 'Create Rule' }}
              </button>
              <button
                type="button"
                @click="showRuleModal = false"
                class="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Session Modal -->
      <div
        v-if="showSessionModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showSessionModal = false"
      >
        <div class="bg-gray-900 rounded-lg p-8 max-w-md w-full">
          <h2 class="text-2xl font-bold text-white mb-6">Create New Session</h2>

          <form @submit.prevent="createSession" class="space-y-4">
            <div>
              <label class="block text-white/80 mb-2">Session Name*</label>
              <input
                v-model="sessionForm.name"
                type="text"
                required
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded text-white focus:outline-none focus:border-primary"
                placeholder="e.g., Marketing Campaign Q1"
              />
            </div>

            <div class="flex gap-4 mt-6">
              <button
                type="submit"
                class="flex-1 bg-gradient-button text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all"
                :disabled="loading"
              >
                Create Session
              </button>
              <button
                type="button"
                @click="showSessionModal = false"
                class="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Loading Overlay -->
      <div v-if="loading" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-gray-900 rounded-lg p-8">
          <i class="fas fa-spinner fa-spin text-4xl text-primary mb-4"></i>
          <p class="text-white">Processing...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-gradient-admin {
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}

.bg-gradient-button {
  background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
}
</style>
