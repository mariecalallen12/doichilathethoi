<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import Card from '../components/ui/Card.vue';
import Input from '../components/ui/Input.vue';
import Select from '../components/ui/Select.vue';
import Button from '../components/ui/Button.vue';
import Table from '../components/ui/Table.vue';

const logs = ref([]);
const loading = ref(false);
const stats = ref(null);
const loadingStats = ref(false);

// Filters
const filters = ref({
  page: 1,
  page_size: 50,
  user_id: '',
  action: '',
  resource_type: '',
  category: '',
  severity: '',
  result: '',
  start_date: '',
  end_date: '',
  search: '',
});

const pagination = ref({
  page: 1,
  page_size: 50,
  total: 0,
  total_pages: 0,
});

const categoryOptions = [
  { label: 'Tất cả', value: '' },
  { label: 'Admin', value: 'admin' },
  { label: 'Authentication', value: 'authentication' },
  { label: 'Financial', value: 'financial' },
  { label: 'Trading', value: 'trading' },
  { label: 'Compliance', value: 'compliance' },
];

const severityOptions = [
  { label: 'Tất cả', value: '' },
  { label: 'Info', value: 'info' },
  { label: 'Warning', value: 'warning' },
  { label: 'Critical', value: 'critical' },
];

const resultOptions = [
  { label: 'Tất cả', value: '' },
  { label: 'Success', value: 'success' },
  { label: 'Failure', value: 'failure' },
  { label: 'Error', value: 'error' },
];

const fetchLogs = async () => {
  loading.value = true;
  try {
    const params = {
      page: filters.value.page,
      page_size: filters.value.page_size,
    };

    if (filters.value.user_id) params.user_id = parseInt(filters.value.user_id);
    if (filters.value.action) params.action = filters.value.action;
    if (filters.value.resource_type) params.resource_type = filters.value.resource_type;
    if (filters.value.category) params.category = filters.value.category;
    if (filters.value.severity) params.severity = filters.value.severity;
    if (filters.value.result) params.result = filters.value.result;
    if (filters.value.start_date) params.start_date = filters.value.start_date;
    if (filters.value.end_date) params.end_date = filters.value.end_date;
    if (filters.value.search) params.search = filters.value.search;

    const res = await api.get('/api/audit/logs', { params });
    logs.value = res.data?.data || [];
    pagination.value = res.data?.pagination || pagination.value;
  } catch (error) {
    console.error('Fetch audit logs error:', error);
    toastService.error('Không thể tải audit logs');
  } finally {
    loading.value = false;
  }
};

const fetchStats = async () => {
  loadingStats.value = true;
  try {
    const params = {};
    if (filters.value.start_date) params.start_date = filters.value.start_date;
    if (filters.value.end_date) params.end_date = filters.value.end_date;

    const res = await api.get('/api/audit/logs/stats', { params });
    stats.value = res.data?.data || null;
  } catch (error) {
    console.error('Fetch stats error:', error);
  } finally {
    loadingStats.value = false;
  }
};

const applyFilters = () => {
  filters.value.page = 1;
  fetchLogs();
  fetchStats();
};

const resetFilters = () => {
  filters.value = {
    page: 1,
    page_size: 50,
    user_id: '',
    action: '',
    resource_type: '',
    category: '',
    severity: '',
    result: '',
    start_date: '',
    end_date: '',
    search: '',
  };
  applyFilters();
};

const changePage = (page) => {
  filters.value.page = page;
  fetchLogs();
};

const getSeverityColor = (severity) => {
  const colors = {
    info: 'bg-blue-500/20 text-blue-300',
    warning: 'bg-yellow-500/20 text-yellow-300',
    critical: 'bg-red-500/20 text-red-300',
  };
  return colors[severity] || 'bg-white/10 text-white/70';
};

const getResultColor = (result) => {
  const colors = {
    success: 'text-green-400',
    failure: 'text-yellow-400',
    error: 'text-red-400',
  };
  return colors[result] || 'text-white/60';
};

const formatDate = (isoString) => {
  if (!isoString) return '—';
  const date = new Date(isoString);
  return date.toLocaleString('vi-VN');
};

const viewLogDetail = async (logId) => {
  try {
    const res = await api.get(`/api/audit/logs/${logId}`);
    const log = res.data?.data;
    
    // Show modal with log details
    const detailText = `
ID: ${log.id}
User ID: ${log.user_id || '—'}
User Role: ${log.user_role || '—'}
Action: ${log.action}
Resource Type: ${log.resource_type}
Resource ID: ${log.resource_id || '—'}
Category: ${log.category || '—'}
Severity: ${log.severity}
Result: ${log.result}
IP Address: ${log.ip_address || '—'}
User Agent: ${log.user_agent || '—'}
Created At: ${formatDate(log.created_at)}
Error Message: ${log.error_message || '—'}
Old Values: ${JSON.stringify(log.old_values, null, 2) || '—'}
New Values: ${JSON.stringify(log.new_values, null, 2) || '—'}
    `;
    
    alert(detailText);
  } catch (error) {
    console.error('View log detail error:', error);
    toastService.error('Không thể xem chi tiết log');
  }
};

onMounted(() => {
  fetchLogs();
  fetchStats();
});
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Audit Log Viewer</h1>
        <p class="text-white/60">
          Xem và filter tất cả audit logs trong hệ thống
        </p>
      </div>
      <Button variant="secondary" @click="applyFilters" :loading="loading">
        <i class="fas fa-search mr-2"></i>
        Áp dụng filter
      </Button>
    </div>

    <!-- Stats -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <div class="p-4">
          <p class="text-white/60 text-sm mb-1">Tổng số logs</p>
          <p class="text-2xl font-bold text-white">{{ stats.total || 0 }}</p>
        </div>
      </Card>
      <Card>
        <div class="p-4">
          <p class="text-white/60 text-sm mb-1">By Category</p>
          <div class="text-sm text-white/80">
            <div v-for="(count, cat) in stats.by_category" :key="cat" class="mb-1">
              {{ cat }}: {{ count }}
            </div>
          </div>
        </div>
      </Card>
      <Card>
        <div class="p-4">
          <p class="text-white/60 text-sm mb-1">By Severity</p>
          <div class="text-sm text-white/80">
            <div v-for="(count, sev) in stats.by_severity" :key="sev" class="mb-1">
              {{ sev }}: {{ count }}
            </div>
          </div>
        </div>
      </Card>
      <Card>
        <div class="p-4">
          <p class="text-white/60 text-sm mb-1">By Result</p>
          <div class="text-sm text-white/80">
            <div v-for="(count, res) in stats.by_result" :key="res" class="mb-1">
              {{ res }}: {{ count }}
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Filters -->
    <Card title="Filters">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          v-model="filters.search"
          label="Search"
          placeholder="Tìm kiếm action, resource type, error..."
        />
        <Input
          v-model="filters.user_id"
          label="User ID"
          type="number"
          placeholder="Filter by user ID"
        />
        <Input
          v-model="filters.action"
          label="Action"
          placeholder="Filter by action"
        />
        <Input
          v-model="filters.resource_type"
          label="Resource Type"
          placeholder="Filter by resource type"
        />
        <Select
          v-model="filters.category"
          :options="categoryOptions"
          label="Category"
        />
        <Select
          v-model="filters.severity"
          :options="severityOptions"
          label="Severity"
        />
        <Select
          v-model="filters.result"
          :options="resultOptions"
          label="Result"
        />
        <Input
          v-model="filters.start_date"
          label="Start Date"
          type="datetime-local"
        />
        <Input
          v-model="filters.end_date"
          label="End Date"
          type="datetime-local"
        />
      </div>
      <div class="mt-4 flex gap-2">
        <Button variant="primary" @click="applyFilters" :loading="loading">
          <i class="fas fa-filter mr-2"></i>
          Áp dụng
        </Button>
        <Button variant="secondary" @click="resetFilters">
          <i class="fas fa-undo mr-2"></i>
          Reset
        </Button>
      </div>
    </Card>

    <!-- Logs Table -->
    <Card title="Audit Logs">
      <div class="overflow-x-auto">
        <table class="min-w-full text-left text-white/80">
          <thead class="text-white/60 border-b border-white/10">
            <tr>
              <th class="py-2 pr-4">ID</th>
              <th class="py-2 pr-4">User ID</th>
              <th class="py-2 pr-4">Action</th>
              <th class="py-2 pr-4">Resource</th>
              <th class="py-2 pr-4">Category</th>
              <th class="py-2 pr-4">Severity</th>
              <th class="py-2 pr-4">Result</th>
              <th class="py-2 pr-4">Created At</th>
              <th class="py-2 pr-4"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="log in logs"
              :key="log.id"
              class="border-b border-white/5 hover:bg-white/5"
            >
              <td class="py-2 pr-4 font-semibold text-white">{{ log.id }}</td>
              <td class="py-2 pr-4">{{ log.user_id || '—' }}</td>
              <td class="py-2 pr-4">{{ log.action }}</td>
              <td class="py-2 pr-4">
                {{ log.resource_type }}
                <span v-if="log.resource_id" class="text-white/40">({{ log.resource_id }})</span>
              </td>
              <td class="py-2 pr-4">{{ log.category || '—' }}</td>
              <td class="py-2 pr-4">
                <span
                  :class="['px-2 py-1 rounded text-xs', getSeverityColor(log.severity)]"
                >
                  {{ log.severity }}
                </span>
              </td>
              <td class="py-2 pr-4">
                <span :class="getResultColor(log.result)">
                  {{ log.result }}
                </span>
              </td>
              <td class="py-2 pr-4 text-sm">{{ formatDate(log.created_at) }}</td>
              <td class="py-2 pr-4 text-right">
                <Button
                  size="sm"
                  variant="tertiary"
                  @click="viewLogDetail(log.id)"
                >
                  <i class="fas fa-eye mr-2"></i>Chi tiết
                </Button>
              </td>
            </tr>
            <tr v-if="logs.length === 0 && !loading">
              <td colspan="9" class="py-8 text-center text-white/60">
                Không có log nào
              </td>
            </tr>
            <tr v-if="loading">
              <td colspan="9" class="py-8 text-center text-white/60">
                <i class="fas fa-spinner fa-spin mr-2"></i>Đang tải...
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total_pages > 1" class="mt-4 flex items-center justify-between">
        <div class="text-white/60 text-sm">
          Trang {{ pagination.page }} / {{ pagination.total_pages }} 
          (Tổng: {{ pagination.total }} logs)
        </div>
        <div class="flex gap-2">
          <Button
            size="sm"
            variant="secondary"
            @click="changePage(pagination.page - 1)"
            :disabled="pagination.page <= 1"
          >
            <i class="fas fa-chevron-left mr-2"></i>Trước
          </Button>
          <Button
            size="sm"
            variant="secondary"
            @click="changePage(pagination.page + 1)"
            :disabled="pagination.page >= pagination.total_pages"
          >
            Sau<i class="fas fa-chevron-right ml-2"></i>
          </Button>
        </div>
      </div>
    </Card>
  </div>
</template>

