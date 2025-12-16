<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import toastService from '../../services/toast';
import Card from '../ui/Card.vue';
import Chart from '../ui/Chart.vue';

const loading = ref(false);
const performanceData = ref({
  system: {
    uptime: 0,
    response_time: 0,
    error_rate: 0,
  },
  trading: {
    win_rate: 0,
    avg_trade_size: 0,
    profit_loss_ratio: 0,
  },
  financial: {
    cash_flow: 0,
    revenue_growth: 0,
    profit_margin: 0,
  },
});

const chartData = ref({
  systemPerformance: {
    labels: [],
    datasets: [],
  },
  tradingMetrics: {
    labels: [],
    datasets: [],
  },
  financialHealth: {
    labels: [],
    datasets: [],
  },
});

const fetchPerformanceData = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/analytics/performance');
    const data = response.data?.data || response.data || {};
    
    if (data.system_performance) {
      performanceData.value.system = {
        uptime: data.system_performance.uptime || 0,
        response_time: data.system_performance.response_time || 0,
        error_rate: data.system_performance.error_rate || 0,
      };
      
      if (data.system_performance.chart) {
        chartData.value.systemPerformance = {
          labels: data.system_performance.chart.labels || [],
          datasets: [
            {
              label: 'Uptime (%)',
              data: data.system_performance.chart.uptime_data || [],
              backgroundColor: 'rgba(34, 197, 94, 0.2)',
              borderColor: 'rgba(34, 197, 94, 1)',
              borderWidth: 2,
              fill: true,
            },
          ],
        };
      }
    }
    
    if (data.trading_metrics) {
      performanceData.value.trading = {
        win_rate: data.trading_metrics.win_rate || 0,
        avg_trade_size: data.trading_metrics.avg_trade_size || 0,
        profit_loss_ratio: data.trading_metrics.profit_loss_ratio || 0,
      };
      
      if (data.trading_metrics.chart) {
        chartData.value.tradingMetrics = {
          labels: data.trading_metrics.chart.labels || [],
          datasets: [
            {
              label: 'Win Rate (%)',
              data: data.trading_metrics.chart.win_rate_data || [],
              backgroundColor: 'rgba(0, 102, 204, 0.2)',
              borderColor: 'rgba(0, 102, 204, 1)',
              borderWidth: 2,
              fill: true,
            },
          ],
        };
      }
    }
    
    if (data.financial_health) {
      performanceData.value.financial = {
        cash_flow: data.financial_health.cash_flow || 0,
        revenue_growth: data.financial_health.revenue_growth || 0,
        profit_margin: data.financial_health.profit_margin || 0,
      };
      
      if (data.financial_health.chart) {
        chartData.value.financialHealth = {
          labels: data.financial_health.chart.labels || [],
          datasets: [
            {
              label: 'Cash Flow ($)',
              data: data.financial_health.chart.cash_flow_data || [],
              backgroundColor: 'rgba(168, 85, 247, 0.2)',
              borderColor: 'rgba(168, 85, 247, 1)',
              borderWidth: 2,
              fill: true,
            },
          ],
        };
      }
    }
  } catch (error) {
    console.error('Fetch performance data error:', error);
    toastService.error('Không thể tải dữ liệu hiệu suất');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchPerformanceData();
});
</script>

<template>
  <div class="space-y-6">
    <!-- System Performance -->
    <Card title="Hiệu suất hệ thống">
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p class="text-white/60 text-sm mb-1">Uptime</p>
            <p class="text-white text-2xl font-bold">{{ performanceData.system.uptime.toFixed(2) }}%</p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Thời gian phản hồi</p>
            <p class="text-white text-2xl font-bold">{{ performanceData.system.response_time.toFixed(2) }}ms</p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Tỷ lệ lỗi</p>
            <p class="text-white text-2xl font-bold">{{ performanceData.system.error_rate.toFixed(2) }}%</p>
          </div>
        </div>
        <Chart type="line" :data="chartData.systemPerformance" height="200px" />
      </div>
    </Card>

    <!-- Trading Metrics -->
    <Card title="Chỉ số giao dịch">
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p class="text-white/60 text-sm mb-1">Win Rate</p>
            <p class="text-white text-2xl font-bold">{{ performanceData.trading.win_rate.toFixed(1) }}%</p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Kích thước giao dịch TB</p>
            <p class="text-white text-2xl font-bold">${{ performanceData.trading.avg_trade_size.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Tỷ lệ Profit/Loss</p>
            <p class="text-white text-2xl font-bold">{{ performanceData.trading.profit_loss_ratio.toFixed(2) }}</p>
          </div>
        </div>
        <Chart type="line" :data="chartData.tradingMetrics" height="200px" />
      </div>
    </Card>

    <!-- Financial Health -->
    <Card title="Sức khỏe tài chính">
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p class="text-white/60 text-sm mb-1">Dòng tiền</p>
            <p :class="['text-white text-2xl font-bold', performanceData.financial.cash_flow >= 0 ? 'text-green-400' : 'text-red-400']">
              ${{ performanceData.financial.cash_flow.toLocaleString() }}
            </p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Tăng trưởng doanh thu</p>
            <p class="text-white text-2xl font-bold">{{ performanceData.financial.revenue_growth.toFixed(1) }}%</p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Tỷ suất lợi nhuận</p>
            <p class="text-white text-2xl font-bold">{{ performanceData.financial.profit_margin.toFixed(1) }}%</p>
          </div>
        </div>
        <Chart type="line" :data="chartData.financialHealth" height="200px" />
      </div>
    </Card>
  </div>
</template>

