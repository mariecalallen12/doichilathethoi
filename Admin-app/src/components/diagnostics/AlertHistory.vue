<template>
  <Card>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold text-white">Alert History</h2>
      <Button @click="fetchAlerts" :loading="loading">Refresh</Button>
    </div>

    <!-- Filters -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
      <div>
        <label class="block text-sm text-gray-400 mb-1">Rule ID</label>
        <input
          v-model="filters.rule_id"
          type="number"
          placeholder="Filter by rule ID"
          class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm"
          @input="applyFilters"
        />
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">User ID</label>
        <input
          v-model="filters.user_id"
          type="number"
          placeholder="Filter by user ID"
          class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm"
          @input="applyFilters"
        />
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">Severity</label>
        <select
          v-model="filters.severity"
          class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm"
          @change="applyFilters"
        >
          <option value="">All</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">Status</label>
        <select
          v-model="filters.resolved"
          class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm"
          @change="applyFilters"
        >
          <option :value="null">All</option>
          <option :value="false">Unresolved</option>
          <option :value="true">Resolved</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div v-if="loading && alerts.length === 0" class="text-center py-8 text-gray-400">
      <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
      <p>Loading alerts...</p>
    </div>

    <Table v-else-if="alerts.length > 0">
      <thead>
        <tr>
          <th>ID</th>
          <th>Rule ID</th>
          <th>User ID</th>
          <th>Severity</th>
          <th>Triggered At</th>
          <th>Resolved</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="alert in alerts" :key="alert.id">
          <td>{{ alert.id }}</td>
          <td>{{ alert.alert_rule_id }}</td>
          <td>{{ alert.user_id || 'N/A' }}</td>
          <td>
            <span
              :class="[
                'px-2 py-1 rounded text-xs font-semibold',
                getSeverityClass(alert.severity)
              ]"
            >
              {{ alert.severity }}
            </span>
          </td>
          <td>{{ formatDate(alert.triggered_at) }}</td>
          <td>
            <span
              :class="[
                'px-2 py-1 rounded text-xs',
                alert.resolved_at ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
              ]"
            >
              {{ alert.resolved_at ? 'Yes' : 'No' }}
            </span>
          </td>
          <td>
            <div class="flex gap-2">
              <button
                @click="viewDetails(alert)"
                class="text-purple-400 hover:text-purple-300 transition-colors"
                title="View details"
              >
                <i class="fas fa-eye"></i>
              </button>
              <button
                v-if="!alert.resolved_at"
                @click="resolveAlert(alert.id)"
                class="text-green-400 hover:text-green-300 transition-colors"
                title="Resolve"
              >
                <i class="fas fa-check"></i>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </Table>

    <div v-else class="text-center py-8 text-gray-400">
      <i class="fas fa-bell-slash text-3xl mb-2"></i>
      <p>No alerts found</p>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="flex justify-between items-center mt-4">
      <div class="text-sm text-gray-400">
        Showing {{ (page - 1) * pageSize + 1 }} to {{ Math.min(page * pageSize, total) }} of {{ total }}
      </div>
      <div class="flex gap-2">
        <Button
          @click="previousPage"
          :disabled="page === 1"
          variant="secondary"
          size="sm"
        >
          Previous
        </Button>
        <Button
          @click="nextPage"
          :disabled="page * pageSize >= total"
          variant="secondary"
          size="sm"
        >
          Next
        </Button>
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

const alerts = ref([]);
const loading = ref(false);
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);

const filters = ref({
  rule_id: null,
  user_id: null,
  severity: '',
  resolved: null,
});

const emit = defineEmits(['view-details']);

function getSeverityClass(severity) {
  const classes = {
    low: 'bg-blue-500/20 text-blue-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    high: 'bg-orange-500/20 text-orange-400',
    critical: 'bg-red-500/20 text-red-400',
  };
  return classes[severity] || classes.medium;
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
}

async function fetchAlerts() {
  loading.value = true;
  try {
    const params = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
    };

    if (filters.value.rule_id) {
      params.rule_id = filters.value.rule_id;
    }
    if (filters.value.user_id) {
      params.user_id = filters.value.user_id;
    }
    if (filters.value.severity) {
      params.severity = filters.value.severity;
    }
    if (filters.value.resolved !== null) {
      params.resolved = filters.value.resolved;
    }

    const response = await api.get('/api/alert-history', { params });
    alerts.value = response.data.alerts || [];
    total.value = response.data.total || 0;
  } catch (error) {
    console.error('Error fetching alerts:', error);
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  page.value = 1;
  fetchAlerts();
}

function previousPage() {
  if (page.value > 1) {
    page.value--;
    fetchAlerts();
  }
}

function nextPage() {
  if (page.value * pageSize.value < total.value) {
    page.value++;
    fetchAlerts();
  }
}

function viewDetails(alert) {
  emit('view-details', alert);
}

async function resolveAlert(alertId) {
  try {
    await api.post(`/api/alert-history/${alertId}/resolve`);
    await fetchAlerts();
  } catch (error) {
    console.error('Error resolving alert:', error);
  }
}

onMounted(() => {
  fetchAlerts();
});
</script>

