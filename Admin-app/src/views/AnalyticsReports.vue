<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import ExcelJS from 'exceljs';
import KPICards from '../components/analytics/KPICards.vue';
import DateRangeSelector from '../components/analytics/DateRangeSelector.vue';
import PerformanceReport from '../components/analytics/PerformanceReport.vue';
import ScheduledReportsManager from '../components/analytics/ScheduledReportsManager.vue';
import Chart from '../components/ui/Chart.vue';
import Card from '../components/ui/Card.vue';
import Table from '../components/ui/Table.vue';

const dateRange = ref('7d');
const loading = ref(false);
const kpis = ref({
  totalRevenue: { value: 0, change: 0 },
  activeUsers: { value: 0, change: 0 },
  totalTrades: { value: 0, change: 0 },
  conversionRate: { value: 0, change: 0 },
});

const topAssets = ref([]);

const userInsights = ref({
  averageSessionTime: '0m 0s',
  retentionRate: 0,
  churnRate: 0,
  conversionRate: 0,
});

const chartData = ref({
  userGrowth: {
    labels: [],
    datasets: [],
  },
  tradingVolume: {
    labels: [],
    datasets: [],
  },
  revenueTrends: {
    labels: [],
    datasets: [],
  },
});

const getDateRangeParams = () => {
  const endDate = new Date();
  let startDate = new Date();
  
  switch (dateRange.value) {
    case '7d':
      startDate.setDate(endDate.getDate() - 7);
      break;
    case '30d':
      startDate.setDate(endDate.getDate() - 30);
      break;
    case '90d':
      startDate.setDate(endDate.getDate() - 90);
      break;
    case '1y':
      startDate.setFullYear(endDate.getFullYear() - 1);
      break;
    default:
      startDate.setDate(endDate.getDate() - 7);
  }
  
  return {
    start_date: startDate.toISOString(),
    end_date: endDate.toISOString(),
  };
};

const fetchAnalytics = async () => {
  loading.value = true;
  try {
    const params = getDateRangeParams();
    const response = await api.get('/api/admin/analytics', params);
    const data = response.data?.data || response.data || {};
    
    // Update KPIs
    if (data.kpis) {
      kpis.value = {
        totalRevenue: data.kpis.total_revenue || { value: 0, change: 0 },
        activeUsers: data.kpis.active_users || { value: 0, change: 0 },
        totalTrades: data.kpis.total_trades || { value: 0, change: 0 },
        conversionRate: data.kpis.conversion_rate || { value: 0, change: 0 },
      };
    }
    
    // Update top assets
    if (data.top_assets) {
      topAssets.value = data.top_assets;
    }
    
    // Update user insights
    if (data.user_insights) {
      userInsights.value = {
        averageSessionTime: data.user_insights.average_session_time || '0m 0s',
        retentionRate: data.user_insights.retention_rate || 0,
        churnRate: data.user_insights.churn_rate || 0,
        conversionRate: data.user_insights.conversion_rate || 0,
      };
    }
    
    // Update chart data
    if (data.user_growth_chart) {
      chartData.value.userGrowth = {
        labels: data.user_growth_chart.labels || [],
        datasets: [
          {
            label: 'Số người dùng',
            data: data.user_growth_chart.data || [],
            backgroundColor: 'rgba(0, 102, 204, 0.2)',
            borderColor: 'rgba(0, 102, 204, 1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
          },
        ],
      };
    }
    
    if (data.trading_volume_chart) {
      chartData.value.tradingVolume = {
        labels: data.trading_volume_chart.labels || [],
        datasets: [
          {
            label: 'Khối lượng giao dịch',
            data: data.trading_volume_chart.data || [],
            backgroundColor: 'rgba(34, 197, 94, 0.2)',
            borderColor: 'rgba(34, 197, 94, 1)',
            borderWidth: 2,
          },
        ],
      };
    }
    
    if (data.revenue_trends_chart) {
      chartData.value.revenueTrends = {
        labels: data.revenue_trends_chart.labels || [],
        datasets: [
          {
            label: 'Doanh thu',
            data: data.revenue_trends_chart.data || [],
            backgroundColor: 'rgba(168, 85, 247, 0.2)',
            borderColor: 'rgba(168, 85, 247, 1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
          },
        ],
      };
    }
  } catch (error) {
    console.error('Fetch analytics error:', error);
    toastService.error('Không thể tải dữ liệu phân tích');
  } finally {
    loading.value = false;
  }
};

const assetHeaders = [
  { key: 'symbol', label: 'Symbol' },
  { key: 'volume', label: 'Volume' },
  { key: 'trades', label: 'Trades' },
  { key: 'change', label: 'Change' },
];

const handleExportReport = async () => {
  try {
    // Prepare export data
    const exportData = {
      'KPIs': [
        {
          'Chỉ số': 'Tổng doanh thu',
          'Giá trị': kpis.value.totalRevenue.value,
          'Thay đổi (%)': kpis.value.totalRevenue.change,
        },
        {
          'Chỉ số': 'Người dùng hoạt động',
          'Giá trị': kpis.value.activeUsers.value,
          'Thay đổi (%)': kpis.value.activeUsers.change,
        },
        {
          'Chỉ số': 'Tổng giao dịch',
          'Giá trị': kpis.value.totalTrades.value,
          'Thay đổi (%)': kpis.value.totalTrades.change,
        },
        {
          'Chỉ số': 'Tỷ lệ chuyển đổi',
          'Giá trị': kpis.value.conversionRate.value,
          'Thay đổi (%)': kpis.value.conversionRate.change,
        },
      ],
      'Top Assets': topAssets.value.map(asset => ({
        'Symbol': asset.symbol,
        'Volume': asset.volume,
        'Trades': asset.trades,
        'Change (%)': asset.change,
      })),
      'User Insights': [
        {
          'Metric': 'Thời gian phiên trung bình',
          'Value': userInsights.value.averageSessionTime,
        },
        {
          'Metric': 'Tỷ lệ giữ chân',
          'Value': `${userInsights.value.retentionRate}%`,
        },
        {
          'Metric': 'Tỷ lệ rời bỏ',
          'Value': `${userInsights.value.churnRate}%`,
        },
        {
          'Metric': 'Tỷ lệ chuyển đổi',
          'Value': `${userInsights.value.conversionRate}%`,
        },
      ],
    };
    
    // Create workbook using ExcelJS
    const workbook = new ExcelJS.Workbook();
    
    // Add KPIs sheet
    const kpisSheet = workbook.addWorksheet('KPIs');
    const kpisHeaders = Object.keys(exportData['KPIs'][0]);
    kpisSheet.columns = kpisHeaders.map(header => ({ header, key: header, width: 20 }));
    kpisSheet.addRows(exportData['KPIs']);
    kpisSheet.getRow(1).font = { bold: true };
    kpisSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE0E0E0' }
    };
    
    // Add Top Assets sheet
    const assetsSheet = workbook.addWorksheet('Top Assets');
    if (exportData['Top Assets'].length > 0) {
      const assetsHeaders = Object.keys(exportData['Top Assets'][0]);
      assetsSheet.columns = assetsHeaders.map(header => ({ header, key: header, width: 20 }));
      assetsSheet.addRows(exportData['Top Assets']);
      assetsSheet.getRow(1).font = { bold: true };
      assetsSheet.getRow(1).fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFE0E0E0' }
      };
    }
    
    // Add User Insights sheet
    const insightsSheet = workbook.addWorksheet('User Insights');
    const insightsHeaders = Object.keys(exportData['User Insights'][0]);
    insightsSheet.columns = insightsHeaders.map(header => ({ header, key: header, width: 25 }));
    insightsSheet.addRows(exportData['User Insights']);
    insightsSheet.getRow(1).font = { bold: true };
    insightsSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE0E0E0' }
    };
    
    // Generate filename with date range
    const filename = `analytics_report_${dateRange.value}_${new Date().toISOString().split('T')[0]}.xlsx`;
    
    // Write file
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    toastService.success('Đã xuất báo cáo ra file Excel');
  } catch (error) {
    console.error('Export report error:', error);
    toastService.error('Không thể xuất báo cáo');
  }
};

onMounted(() => {
  fetchAnalytics();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Phân tích & Báo cáo</h1>
        <p class="text-white/60">Thống kê và phân tích hiệu suất hệ thống</p>
      </div>
      <div class="flex items-center gap-3">
      <DateRangeSelector v-model="dateRange" @update:model-value="fetchAnalytics" />
        <button
          @click="handleExportReport"
          class="px-4 py-2 rounded-lg bg-primary hover:bg-primary/80 text-white font-medium transition-colors flex items-center gap-2"
        >
          <i class="fas fa-download"></i>
          Xuất báo cáo
        </button>
      </div>
    </div>

    <!-- KPI Cards -->
    <KPICards :kpis="kpis" />

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card title="Tăng trưởng người dùng">
        <Chart type="line" :data="chartData.userGrowth" height="300px" />
      </Card>
      <Card title="Khối lượng giao dịch">
        <Chart type="bar" :data="chartData.tradingVolume" height="300px" />
      </Card>
      <Card title="Xu hướng doanh thu">
        <Chart type="line" :data="chartData.revenueTrends" height="300px" />
      </Card>
      <Card title="Top Assets">
        <Table :headers="assetHeaders" :data="topAssets">
          <template #default="{ data }">
            <tr
              v-for="asset in data"
              :key="asset.symbol"
              class="border-b border-white/5 hover:bg-white/5"
            >
              <td class="px-4 py-3 text-white font-semibold">{{ asset.symbol }}</td>
              <td class="px-4 py-3 text-white">${{ asset.volume.toLocaleString() }}</td>
              <td class="px-4 py-3 text-white/80">{{ asset.trades.toLocaleString() }}</td>
              <td :class="['px-4 py-3', asset.change >= 0 ? 'text-green-400' : 'text-red-400']">
                {{ asset.change >= 0 ? '+' : '' }}{{ asset.change }}%
              </td>
            </tr>
          </template>
        </Table>
      </Card>
    </div>

    <!-- User Insights -->
    <Card title="Thông tin người dùng">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p class="text-white/60 text-sm mb-1">Thời gian phiên trung bình</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.averageSessionTime }}</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Tỷ lệ giữ chân</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.retentionRate }}%</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Tỷ lệ rời bỏ</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.churnRate }}%</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Tỷ lệ chuyển đổi</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.conversionRate }}%</p>
        </div>
      </div>
    </Card>

    <!-- Performance Report -->
    <PerformanceReport />

    <!-- Scheduled Reports Manager -->
    <ScheduledReportsManager />
  </div>
</template>

