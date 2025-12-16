<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Tỷ Giá Hối Đoái</h1>
      <p class="text-purple-300">Tỷ giá USDT với các loại tiền tệ khác</p>
    </div>

    <!-- Rate Cards -->
    <RateCards />

    <!-- Currency Converter -->
    <CurrencyConverter />

    <!-- Rate History Chart -->
    <div class="glass-panel rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4 flex items-center">
        <i class="fas fa-chart-line mr-2 text-purple-400"></i>
        Lịch Sử Tỷ Giá
      </h3>
      <div class="mb-4 flex space-x-2">
        <button
          v-for="period in periods"
          :key="period.value"
          @click="selectedPeriod = period.value"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
            selectedPeriod === period.value
              ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white'
              : 'bg-slate-800/50 text-purple-300 hover:bg-purple-500/20'
          ]"
        >
          {{ period.label }}
        </button>
      </div>
      <div ref="rateHistoryChart" class="h-96"></div>
    </div>

    <!-- Update Status -->
    <div class="glass-panel rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div
            :class="[
              'w-3 h-3 rounded-full',
              updateStatus === 'fresh' ? 'bg-green-500' : updateStatus === 'recent' ? 'bg-yellow-500' : 'bg-red-500'
            ]"
          ></div>
          <div class="text-purple-300 text-sm">
            Cập nhật lần cuối: {{ formatLastUpdate }}
          </div>
        </div>
        <div class="text-purple-300 text-xs">
          Nguồn: Binance • Tự động cập nhật mỗi phút
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch, nextTick } from 'vue';
import { useExchangeRatesStore } from '../../stores/exchangeRates';
import RateCards from '../../components/personal/rates/RateCards.vue';
import CurrencyConverter from '../../components/personal/rates/CurrencyConverter.vue';
import * as echarts from 'echarts';

const exchangeRatesStore = useExchangeRatesStore();
const updateStatus = computed(() => exchangeRatesStore.updateStatus);
const selectedPeriod = ref('7d');
const rateHistoryChart = ref(null);
let chartInstance = null;

const periods = [
  { label: '1 Ngày', value: '1d' },
  { label: '7 Ngày', value: '7d' },
  { label: '30 Ngày', value: '30d' },
  { label: '1 Năm', value: '1y' },
];

const formatLastUpdate = computed(() => {
  const date = exchangeRatesStore.lastUpdate;
  return date.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
});

function initRateHistoryChart() {
  if (!rateHistoryChart.value) return;
  
  chartInstance = echarts.init(rateHistoryChart.value, 'dark');
  updateRateHistoryChart();
}

async function updateRateHistoryChart() {
  if (!chartInstance) return;
  
  // Get rates from store
  const rates = exchangeRatesStore.rates;
  const usdtToVndRate = rates.find(r => r.from === 'USDT' && r.to === 'VND');
  
  if (!usdtToVndRate) return;
  
  // Generate historical data based on period
  const days = selectedPeriod.value === '1d' ? 24 : 
               selectedPeriod.value === '7d' ? 7 :
               selectedPeriod.value === '30d' ? 30 : 365;
  
  const dates = [];
  const values = [];
  const now = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    if (selectedPeriod.value === '1d') {
      date.setHours(date.getHours() - i);
      dates.push(date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }));
    } else {
      date.setDate(date.getDate() - i);
      dates.push(date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }));
    }
    
    // Fetch real historical data from API - no mock data
    // If historical data not available, use current rate
    try {
      const response = await fetch(`/api/market/historical-data/USDTVND?timeframe=1h&limit=7`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        if (data.data && data.data.length > 0) {
          // Use real historical data
          const historicalRate = data.data[data.data.length - i - 1]?.close || usdtToVndRate.rate;
          values.push(historicalRate);
        } else {
          values.push(usdtToVndRate.rate);
        }
      } else {
        values.push(usdtToVndRate.rate);
      }
    } catch (error) {
      // Fallback to current rate if API fails
      values.push(usdtToVndRate.rate);
    }
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0];
        return `${param.name}<br/>${param.seriesName}: ${param.value.toLocaleString('vi-VN')} VND`;
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
        rotate: selectedPeriod.value === '1d' ? 45 : 0,
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
        formatter: (value) => value.toLocaleString('vi-VN'),
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
        name: 'USDT → VND',
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
  
  chartInstance.setOption(option);
}

watch(selectedPeriod, () => {
  updateRateHistoryChart();
});

watch(() => exchangeRatesStore.rates, () => {
  updateRateHistoryChart();
}, { deep: true });

onMounted(async () => {
  exchangeRatesStore.startAutoRefresh();
  await nextTick();
  initRateHistoryChart();
});

// Resize chart on window resize
if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => {
    chartInstance?.resize();
  });
}
</script>

