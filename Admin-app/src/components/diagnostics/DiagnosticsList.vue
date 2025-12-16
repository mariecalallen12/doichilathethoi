<template>
  <div class="space-y-4">
    <!-- Filters -->
    <Card class="p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">Health Status</label>
          <Select
            v-model="filters.health"
            :options="healthOptions"
            placeholder="All Status"
            @change="loadReports"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">User ID</label>
          <Input
            v-model="filters.userId"
            type="number"
            placeholder="Filter by User ID"
            @input="debouncedLoadReports"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">Date From</label>
          <Input
            v-model="filters.dateFrom"
            type="date"
            @change="loadReports"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">Date To</label>
          <Input
            v-model="filters.dateTo"
            type="date"
            @change="loadReports"
          />
        </div>
      </div>
      <div class="mt-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Input
            v-model="searchQuery"
            placeholder="Search by URL..."
            class="w-64"
            @input="debouncedLoadReports"
          />
          <button
            @click="loadReports"
            class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            <i class="fas fa-search mr-2"></i>
            Search
          </button>
        </div>
        <button
          @click="exportReports"
          class="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
          :disabled="reports.length === 0"
        >
          <i class="fas fa-download mr-2"></i>
          Export
        </button>
      </div>
    </Card>

    <!-- Reports Table -->
    <Card>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-white/10">
              <th class="text-left p-4 text-white/80 font-medium">ID</th>
              <th class="text-left p-4 text-white/80 font-medium">User</th>
              <th class="text-left p-4 text-white/80 font-medium">Health</th>
              <th class="text-left p-4 text-white/80 font-medium">URL</th>
              <th class="text-left p-4 text-white/80 font-medium">Issues</th>
              <th class="text-left p-4 text-white/80 font-medium">Created</th>
              <th class="text-left p-4 text-white/80 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" v-for="i in 5" :key="i" class="border-b border-white/5">
              <td colspan="7" class="p-4">
                <div class="h-4 bg-white/10 rounded animate-pulse"></div>
              </td>
            </tr>
            <tr
              v-else-if="reports.length === 0"
              class="border-b border-white/5"
            >
              <td colspan="7" class="p-8 text-center text-white/60">
                No reports found
              </td>
            </tr>
            <tr
              v-else
              v-for="report in reports"
              :key="report.id"
              class="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              <td class="p-4 text-white/90">{{ report.id }}</td>
              <td class="p-4 text-white/90">
                {{ report.user_id || 'Anonymous' }}
              </td>
              <td class="p-4">
                <Badge
                  :type="getHealthBadgeType(report.overall_health)"
                  :text="report.overall_health || 'unknown'"
                />
              </td>
              <td class="p-4 text-white/70 text-sm max-w-xs truncate" :title="report.url">
                {{ report.url }}
              </td>
              <td class="p-4 text-white/90">
                {{ report.recommendations?.length || 0 }}
              </td>
              <td class="p-4 text-white/70 text-sm">
                {{ formatDate(report.created_at) }}
              </td>
              <td class="p-4">
                <button
                  @click="viewReport(report)"
                  class="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded text-sm transition-colors"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="!loading && reports.length > 0" class="p-4 border-t border-white/10 flex items-center justify-between">
        <div class="text-white/60 text-sm">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalReports) }} of {{ totalReports }} reports
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span class="text-white/80">{{ currentPage }} / {{ totalPages }}</span>
          <button
            @click="currentPage++"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Card from '../ui/Card.vue';
import Input from '../ui/Input.vue';
import Select from '../ui/Select.vue';
import Badge from '../ui/Badge.vue';
import axios from 'axios';

const emit = defineEmits(['view-report']);

const reports = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(20);
const totalReports = ref(0);
const searchQuery = ref('');

const filters = ref({
  health: '',
  userId: '',
  dateFrom: '',
  dateTo: '',
});

const healthOptions = [
  { value: '', label: 'All Status' },
  { value: 'healthy', label: 'Healthy' },
  { value: 'degraded', label: 'Degraded' },
  { value: 'unhealthy', label: 'Unhealthy' },
];

const totalPages = computed(() => Math.ceil(totalReports.value / pageSize.value));

const getHealthBadgeType = (health) => {
  switch (health) {
    case 'healthy': return 'success';
    case 'degraded': return 'warning';
    case 'unhealthy': return 'error';
    default: return 'default';
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('vi-VN');
};

let debounceTimer = null;
const debouncedLoadReports = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    loadReports();
  }, 500);
};

const loadReports = async () => {
  loading.value = true;
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    };

    if (filters.value.health) {
      params.health = filters.value.health;
    }
    if (filters.value.userId) {
      params.user_id = parseInt(filters.value.userId);
    }

    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
    const response = await axios.get('/api/diagnostics/trading-reports', {
      params,
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    });

    // Filter by search query and date range client-side if needed
    let filteredReports = response.data;
    
    if (searchQuery.value) {
      filteredReports = filteredReports.filter(r => 
        r.url.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    }

    if (filters.value.dateFrom) {
      filteredReports = filteredReports.filter(r => 
        new Date(r.created_at) >= new Date(filters.value.dateFrom)
      );
    }

    if (filters.value.dateTo) {
      filteredReports = filteredReports.filter(r => 
        new Date(r.created_at) <= new Date(filters.value.dateTo)
      );
    }

    reports.value = filteredReports;
    totalReports.value = filteredReports.length; // Approximate, API should return total
  } catch (error) {
    console.error('Error loading reports:', error);
  } finally {
    loading.value = false;
  }
};

const viewReport = (report) => {
  emit('view-report', report);
};

const exportReports = () => {
  const data = reports.value.map(r => ({
    id: r.id,
    user_id: r.user_id,
    url: r.url,
    overall_health: r.overall_health,
    created_at: r.created_at,
    recommendations_count: r.recommendations?.length || 0,
  }));

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `diagnostic-reports-${new Date().toISOString()}.json`;
  link.click();
  URL.revokeObjectURL(url);
};

onMounted(() => {
  loadReports();
});
</script>

