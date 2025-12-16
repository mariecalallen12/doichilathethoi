<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6 flex items-center">
      <i class="fas fa-chart-pie mr-2 text-purple-400"></i>
      Phân Tích Portfolio
    </h3>

    <!-- Total Portfolio Value -->
    <div class="mb-6 p-4 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 border border-purple-500/30 rounded-lg">
      <div class="text-purple-300 text-sm mb-1">Tổng giá trị portfolio</div>
      <div class="font-orbitron text-3xl font-bold text-white">{{ formatVND(totalValue) }}</div>
    </div>

    <!-- Top Assets -->
    <div class="mb-6">
      <div class="text-white font-medium mb-4">Top 5 tài sản lớn nhất</div>
      <div class="space-y-3">
        <div
          v-for="(asset, index) in topAssets"
          :key="asset.currency"
          class="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <span class="text-purple-300 font-bold">{{ index + 1 }}</span>
            </div>
            <div>
              <div class="text-white font-medium">{{ asset.currency }}</div>
              <div class="text-purple-300 text-xs">{{ asset.percentage }}%</div>
            </div>
          </div>
          <div class="text-white font-medium">{{ formatAmount(asset.value) }}</div>
        </div>
      </div>
    </div>

    <!-- Allocation Chart -->
    <div class="mb-6">
      <div class="text-purple-300 text-sm mb-2">Phân bổ theo asset</div>
      <div ref="allocationChart" class="h-48"></div>
    </div>

    <!-- Performance Chart -->
    <div>
      <div class="text-purple-300 text-sm mb-2">Hiệu suất portfolio (7 ngày)</div>
      <div ref="performanceChart" class="h-48"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch, nextTick } from 'vue';
import { useAccountStore } from '../../../stores/account';
import { useExchangeRatesStore } from '../../../stores/exchangeRates';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';
import * as echarts from 'echarts';

const accountStore = useAccountStore();
const exchangeRatesStore = useExchangeRatesStore();

const exchangeRateUSDTtoVND = ref(24850);

const totalValue = computed(() => {
  let total = 0;
  
  if (accountStore.currencies?.crypto) {
    Object.entries(accountStore.currencies.crypto).forEach(([currency, data]) => {
      const amount = data.value || 0;
      if (!amount) return;

      if (currency === 'USDT') {
        total += amount * exchangeRateUSDTtoVND.value;
      } else if (currency === 'BTC') {
        const btcToUsdt = exchangeRatesStore.getRate('BTC', 'USDT') || 43000;
        total += amount * exchangeRateUSDTtoVND.value * btcToUsdt;
      } else if (currency === 'ETH') {
        const ethToUsdt = exchangeRatesStore.getRate('ETH', 'USDT') || 2650;
        total += amount * exchangeRateUSDTtoVND.value * ethToUsdt;
      }
    });
  }
  
  if (accountStore.currencies?.fiat) {
    if (accountStore.currencies.fiat.VND) {
      total += accountStore.currencies.fiat.VND.value || 0;
    }
    if (accountStore.currencies.fiat.USD) {
      const usdToVnd = exchangeRatesStore.getRate('USD', 'VND') || exchangeRateUSDTtoVND.value;
      total += (accountStore.currencies.fiat.USD.value || 0) * usdToVnd;
    }
  }
  
  return total;
});

const topAssets = computed(() => {
  const assets = [];
  
  if (accountStore.currencies?.crypto) {
    Object.entries(accountStore.currencies.crypto).forEach(([currency, data]) => {
      const amount = data.value || 0;
      if (!amount) return;

      let value = 0;
      if (currency === 'USDT') {
        value = amount * exchangeRateUSDTtoVND.value;
      } else if (currency === 'BTC') {
        const btcToUsdt = exchangeRatesStore.getRate('BTC', 'USDT') || 43000;
        value = amount * exchangeRateUSDTtoVND.value * btcToUsdt;
      } else if (currency === 'ETH') {
        const ethToUsdt = exchangeRatesStore.getRate('ETH', 'USDT') || 2650;
        value = amount * exchangeRateUSDTtoVND.value * ethToUsdt;
      }
      if (value > 0) {
        assets.push({ currency, value });
      }
    });
  }
  
  if (accountStore.currencies?.fiat) {
    Object.entries(accountStore.currencies.fiat).forEach(([currency, data]) => {
      const amount = data.value || 0;
      if (!amount) return;

      let value = 0;
      if (currency === 'VND') {
        value = amount;
      } else if (currency === 'USD') {
        const usdToVnd = exchangeRatesStore.getRate('USD', 'VND') || exchangeRateUSDTtoVND.value;
        value = amount * usdToVnd;
      }
      if (value > 0) {
        assets.push({ currency, value });
      }
    });
  }
  
  assets.sort((a, b) => b.value - a.value);
  const top5 = assets.slice(0, 5);
  const total = top5.reduce((sum, a) => sum + a.value, 0);
  
  return top5.map(asset => ({
    ...asset,
    percentage: total > 0 ? Math.round((asset.value / total) * 100) : 0,
  }));
});

const formatVND = (amount) => {
  return `${formatNumber(amount)} ₫`;
};

const formatAmount = (amount) => {
  const usdValue = exchangeRateUSDTtoVND.value ? amount / exchangeRateUSDTtoVND.value : amount;
  return formatCurrency(usdValue, 'USD');
};

// Chart refs
const allocationChart = ref(null);
const performanceChart = ref(null);
let allocationChartInstance = null;
let performanceChartInstance = null;

// Initialize charts
onMounted(async () => {
  await nextTick();

  // Đồng bộ tỷ giá USDT→VND từ store nếu có
  try {
    await exchangeRatesStore.fetchRates();
    const rate = exchangeRatesStore.getRate('USDT', 'VND');
    if (rate) {
      exchangeRateUSDTtoVND.value = rate;
    }
  } catch (e) {
    console.error('Failed to fetch exchange rates for PortfolioAnalytics:', e);
  }

  initAllocationChart();
  initPerformanceChart();
});

// Watch for data changes
watch(() => topAssets.value, () => {
  updateAllocationChart();
}, { deep: true });

function initAllocationChart() {
  if (!allocationChart.value) return;
  
  allocationChartInstance = echarts.init(allocationChart.value, 'dark');
  updateAllocationChart();
}

function updateAllocationChart() {
  if (!allocationChartInstance) return;
  
  const data = topAssets.value.map(asset => ({
    value: asset.value,
    name: asset.currency,
  }));
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      bottom: '5%',
      left: 'center',
      textStyle: {
        color: '#a78bfa',
      },
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#1e293b',
          borderWidth: 2,
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          color: '#fff',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
          },
        },
        data: data,
        color: [
          '#8b5cf6',
          '#6366f1',
          '#ec4899',
          '#f59e0b',
          '#10b981',
        ],
      },
    ],
  };
  
  allocationChartInstance.setOption(option);
}

function initPerformanceChart() {
  if (!performanceChart.value) return;
  
  performanceChartInstance = echarts.init(performanceChart.value, 'dark');
  updatePerformanceChart();
}

async function updatePerformanceChart() {
  if (!performanceChartInstance) return;
  
  // Fetch real performance data from API - no mock data
  const dates = [];
  const values = [];
  
  try {
    // Try to fetch from portfolio analytics API
    const response = await fetch('/api/portfolio/analytics?period=7D', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      // Use real data from API if available
      if (data.data && data.data.performance_history) {
        data.data.performance_history.forEach(item => {
          dates.push(new Date(item.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }));
          values.push(item.value);
        });
      }
    }
  } catch (error) {
    console.warn('Could not fetch portfolio performance data:', error);
  }
  
  // If no data available, show empty chart with current value only
  if (dates.length === 0) {
    const now = new Date();
    dates.push(now.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }));
    values.push(totalValue.value);
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0];
        return `${param.name}<br/>${formatVND(param.value)}`;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        color: '#a78bfa',
      },
      axisLine: {
        lineStyle: {
          color: '#4c1d95',
        },
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#a78bfa',
        formatter: (value) => {
          if (value >= 1000000) {
            return `${(value / 1000000).toFixed(1)}M`;
          }
          if (value >= 1000) {
            return `${(value / 1000).toFixed(1)}K`;
          }
          return value.toFixed(0);
        },
      },
      axisLine: {
        lineStyle: {
          color: '#4c1d95',
        },
      },
      splitLine: {
        lineStyle: {
          color: '#4c1d95',
          opacity: 0.3,
        },
      },
    },
    series: [
      {
        name: 'Giá trị portfolio',
        type: 'line',
        smooth: true,
        data: values,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
              { offset: 1, color: 'rgba(139, 92, 246, 0.05)' },
            ],
          },
        },
        lineStyle: {
          color: '#8b5cf6',
          width: 2,
        },
        itemStyle: {
          color: '#8b5cf6',
        },
      },
    ],
  };
  
  performanceChartInstance.setOption(option);
}

// Resize charts on window resize
if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => {
    allocationChartInstance?.resize();
    performanceChartInstance?.resize();
  });
}
</script>
