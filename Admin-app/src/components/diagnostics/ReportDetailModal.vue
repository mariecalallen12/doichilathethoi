<template>
  <Modal :show="show" @close="$emit('close')" size="large">
    <template #header>
      <h2 class="text-xl font-bold text-white">Diagnostic Report Details</h2>
    </template>

    <template #body>
      <div v-if="report" class="space-y-6">
        <!-- Basic Info -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-white/60 text-sm">Report ID</label>
            <div class="text-white font-medium">{{ report.id }}</div>
          </div>
          <div>
            <label class="text-white/60 text-sm">User ID</label>
            <div class="text-white font-medium">{{ report.user_id || 'Anonymous' }}</div>
          </div>
          <div>
            <label class="text-white/60 text-sm">Overall Health</label>
            <Badge
              :type="getHealthBadgeType(report.overall_health)"
              :text="report.overall_health || 'unknown'"
            />
          </div>
          <div>
            <label class="text-white/60 text-sm">Created At</label>
            <div class="text-white font-medium">{{ formatDate(report.created_at) }}</div>
          </div>
          <div class="col-span-2">
            <label class="text-white/60 text-sm">URL</label>
            <div class="text-white font-medium break-all">{{ report.url }}</div>
          </div>
        </div>

        <!-- Recommendations -->
        <div v-if="report.recommendations && report.recommendations.length > 0">
          <h3 class="text-lg font-bold text-white mb-3">Recommendations</h3>
          <div class="space-y-2">
            <div
              v-for="(rec, index) in report.recommendations"
              :key="index"
              :class="[
                'p-3 rounded-lg border',
                rec.severity === 'high' ? 'bg-red-500/20 border-red-500/30' :
                rec.severity === 'medium' ? 'bg-yellow-500/20 border-yellow-500/30' :
                'bg-blue-500/20 border-blue-500/30'
              ]"
            >
              <div class="flex items-start justify-between mb-2">
                <div class="font-medium text-white">{{ rec.issue }}</div>
                <Badge
                  :type="rec.severity === 'high' ? 'error' : rec.severity === 'medium' ? 'warning' : 'info'"
                  :text="rec.severity"
                />
              </div>
              <div class="text-white/70 text-sm">
                <strong>Category:</strong> {{ rec.category }}
              </div>
              <div class="text-white/80 text-sm mt-2">
                <strong>Solution:</strong> {{ rec.solution }}
              </div>
            </div>
          </div>
        </div>

        <!-- Auth Status -->
        <div v-if="report.auth_status">
          <h3 class="text-lg font-bold text-white mb-3">Authentication Status</h3>
          <div class="bg-slate-700/30 rounded-lg p-4">
            <pre class="text-white/80 text-sm overflow-x-auto">{{ JSON.stringify(report.auth_status, null, 2) }}</pre>
          </div>
        </div>

        <!-- API Status -->
        <div v-if="report.api_status">
          <h3 class="text-lg font-bold text-white mb-3">API Status</h3>
          <div class="bg-slate-700/30 rounded-lg p-4">
            <pre class="text-white/80 text-sm overflow-x-auto">{{ JSON.stringify(report.api_status, null, 2) }}</pre>
          </div>
        </div>

        <!-- WebSocket Status -->
        <div v-if="report.ws_status">
          <h3 class="text-lg font-bold text-white mb-3">WebSocket Status</h3>
          <div class="bg-slate-700/30 rounded-lg p-4">
            <pre class="text-white/80 text-sm overflow-x-auto">{{ JSON.stringify(report.ws_status, null, 2) }}</pre>
          </div>
        </div>

        <!-- Component Status -->
        <div v-if="report.component_status">
          <h3 class="text-lg font-bold text-white mb-3">Component Status</h3>
          <div class="bg-slate-700/30 rounded-lg p-4">
            <pre class="text-white/80 text-sm overflow-x-auto">{{ JSON.stringify(report.component_status, null, 2) }}</pre>
          </div>
        </div>

        <!-- Raw Data -->
        <div>
          <h3 class="text-lg font-bold text-white mb-3">Raw Data</h3>
          <div class="bg-slate-700/30 rounded-lg p-4 max-h-96 overflow-auto">
            <pre class="text-white/80 text-xs">{{ JSON.stringify(report, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button
          @click="downloadReport"
          class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
        >
          <i class="fas fa-download mr-2"></i>
          Download JSON
        </button>
        <button
          @click="$emit('close')"
          class="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors"
        >
          Close
        </button>
      </div>
    </template>
  </Modal>
</template>

<script setup>
import Modal from '../ui/Modal.vue';
import Badge from '../ui/Badge.vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  report: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close']);

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

const downloadReport = () => {
  if (!props.report) return;
  
  const blob = new Blob([JSON.stringify(props.report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `diagnostic-report-${props.report.id}.json`;
  link.click();
  URL.revokeObjectURL(url);
};
</script>

