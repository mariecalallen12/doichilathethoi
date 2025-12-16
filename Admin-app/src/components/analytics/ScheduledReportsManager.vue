<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import toastService from '../../services/toast';
import Card from '../ui/Card.vue';
import Table from '../ui/Table.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';
import ToggleSwitch from '../settings/ToggleSwitch.vue';

const reports = ref([]);
const loading = ref(false);

const headers = [
  { key: 'report_type', label: 'Loại báo cáo', sortable: true },
  { key: 'frequency', label: 'Tần suất', sortable: true },
  { key: 'status', label: 'Trạng thái', sortable: true },
  { key: 'last_run', label: 'Chạy lần cuối', sortable: true },
  { key: 'next_run', label: 'Chạy tiếp theo', sortable: true },
  { key: 'actions', label: 'Thao tác', sortable: false },
];

const fetchReports = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/reports/scheduled');
    const data = response.data?.data || response.data || {};
    reports.value = data.reports || data.scheduled_reports || [];
  } catch (error) {
    console.error('Fetch scheduled reports error:', error);
    toastService.error('Không thể tải danh sách báo cáo đã lên lịch');
  } finally {
    loading.value = false;
  }
};

const handleToggleStatus = async (reportId, currentStatus) => {
  loading.value = true;
  try {
    const newStatus = currentStatus === 'active' ? 'pending' : 'active';
    await api.patch(`/api/admin/reports/scheduled/${reportId}`, {
      status: newStatus,
    });
    toastService.success(`Đã ${newStatus === 'active' ? 'kích hoạt' : 'tạm dừng'} báo cáo`);
    await fetchReports();
  } catch (error) {
    console.error('Toggle report status error:', error);
    toastService.error('Không thể thay đổi trạng thái báo cáo');
  } finally {
    loading.value = false;
  }
};

const handleViewHistory = async (reportId) => {
  // This would open a modal or navigate to history page
  toastService.info('Tính năng xem lịch sử đang được phát triển');
};

const handleDelete = async (reportId) => {
  if (!confirm('Bạn có chắc chắn muốn xóa báo cáo đã lên lịch này?')) {
    return;
  }
  
  loading.value = true;
  try {
    await api.delete(`/api/admin/reports/scheduled/${reportId}`);
    toastService.success('Đã xóa báo cáo');
    await fetchReports();
  } catch (error) {
    console.error('Delete report error:', error);
    toastService.error('Không thể xóa báo cáo');
  } finally {
    loading.value = false;
  }
};

const getReportTypeText = (type) => {
  const typeMap = {
    daily_summary: 'Tóm tắt hàng ngày',
    weekly_analytics: 'Phân tích hàng tuần',
    monthly_report: 'Báo cáo hàng tháng',
    financial_report: 'Báo cáo tài chính',
    trading_report: 'Báo cáo giao dịch',
  };
  return typeMap[type] || type;
};

const getFrequencyText = (frequency) => {
  const freqMap = {
    daily: 'Hàng ngày',
    weekly: 'Hàng tuần',
    monthly: 'Hàng tháng',
  };
  return freqMap[frequency] || frequency;
};

const getStatusType = (status) => {
  return status === 'active' ? 'approved' : 'pending';
};

const getStatusText = (status) => {
  return status === 'active' ? 'Đang hoạt động' : 'Tạm dừng';
};

onMounted(() => {
  fetchReports();
});
</script>

<template>
  <Card title="Quản lý báo cáo đã lên lịch">
    <Table
      :headers="headers"
      :data="reports"
      :loading="loading"
    >
      <template #default="{ data }">
        <tr
          v-for="report in data"
          :key="report.id"
          class="border-b border-white/5 hover:bg-white/5 transition-colors"
        >
          <td class="px-4 py-3 text-white/80 text-sm font-semibold">
            {{ getReportTypeText(report.report_type) }}
          </td>
          <td class="px-4 py-3 text-white/80 text-sm">
            {{ getFrequencyText(report.frequency) }}
          </td>
          <td class="px-4 py-3">
            <Badge :type="getStatusType(report.status)">
              {{ getStatusText(report.status) }}
            </Badge>
          </td>
          <td class="px-4 py-3 text-white/60 text-sm">
            {{ report.last_run ? new Date(report.last_run).toLocaleString('vi-VN') : 'Chưa chạy' }}
          </td>
          <td class="px-4 py-3 text-white/60 text-sm">
            {{ report.next_run ? new Date(report.next_run).toLocaleString('vi-VN') : 'N/A' }}
          </td>
          <td class="px-4 py-3">
            <div class="flex items-center gap-2">
              <div class="flex items-center">
                <ToggleSwitch
                  :model-value="report.status === 'active'"
                  @update:model-value="handleToggleStatus(report.id, report.status)"
                />
              </div>
              <Button
                variant="ghost"
                size="sm"
                icon="fas fa-history"
                @click="handleViewHistory(report.id)"
              >
              </Button>
              <Button
                variant="ghost"
                size="sm"
                icon="fas fa-trash text-red-400"
                @click="handleDelete(report.id)"
              >
              </Button>
            </div>
          </td>
        </tr>
      </template>
    </Table>
  </Card>
</template>

