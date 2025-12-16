<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import DiagnosticsList from '../components/diagnostics/DiagnosticsList.vue';
import DiagnosticsChart from '../components/diagnostics/DiagnosticsChart.vue';
import ReportDetailModal from '../components/diagnostics/ReportDetailModal.vue';
import Card from '../components/ui/Card.vue';

const reports = ref([]);
const selectedReport = ref(null);
const showReportModal = ref(false);
const loading = ref(false);

const loadAllReports = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
    const response = await axios.get('/api/diagnostics/trading-reports', {
      params: {
        skip: 0,
        limit: 1000, // Get all for chart
      },
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    });
    reports.value = response.data;
  } catch (error) {
    console.error('Error loading reports:', error);
  } finally {
    loading.value = false;
  }
};

const handleViewReport = (report) => {
  selectedReport.value = report;
  showReportModal.value = true;
};

const handleReportListUpdate = () => {
  // Reload all reports when list updates
  loadAllReports();
};

onMounted(() => {
  loadAllReports();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white mb-2">Diagnostics Management</h1>
      <p class="text-white/60">Monitor and analyze trading dashboard diagnostic reports</p>
    </div>

    <!-- Chart -->
    <DiagnosticsChart :reports="reports" />

    <!-- Reports List -->
    <DiagnosticsList
      @view-report="handleViewReport"
      @update="handleReportListUpdate"
    />

    <!-- Report Detail Modal -->
    <ReportDetailModal
      :show="showReportModal"
      :report="selectedReport"
      @close="showReportModal = false"
    />
  </div>
</template>

