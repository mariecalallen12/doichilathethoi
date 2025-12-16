<template>
  <section class="mb-8">
    <div class="market-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-white">Chỉ số kinh tế</h2>
        <div class="text-sm text-gray-400">
          <i class="far fa-clock mr-1"></i>
          Cập nhật: {{ formatLastUpdate(lastUpdate) }}
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="indicator in indicators"
          :key="indicator.id"
          class="indicator-card p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <h3 class="text-white font-semibold">{{ indicator.name }}</h3>
              <p class="text-gray-400 text-xs">{{ indicator.description }}</p>
            </div>
            <div
              class="w-12 h-12 rounded-lg flex items-center justify-center"
              :class="getStatusBgClass(indicator.status)"
            >
              <i :class="getStatusIcon(indicator.status)" class="text-xl"></i>
            </div>
          </div>
          
          <div class="mb-3">
            <div class="flex items-baseline space-x-2">
              <span class="text-2xl font-bold text-white">{{ indicator.value }}</span>
              <span class="text-gray-400">{{ indicator.unit }}</span>
            </div>
            <div class="flex items-center space-x-2 mt-1">
              <span
                class="text-sm font-semibold"
                :class="getChangeColor(indicator.change)"
              >
                {{ formatChange(indicator.change) }}
              </span>
              <span class="text-xs text-gray-500">({{ formatPercentChange(indicator.changePercent) }})</span>
            </div>
          </div>
          
          <div class="h-16">
            <div ref="sparklineContainer" :id="`sparkline-${indicator.id}`" class="w-full h-full"></div>
          </div>
          
          <div class="mt-2 text-xs text-gray-500">
            <i class="fas fa-globe mr-1"></i>
            {{ indicator.country }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useIndicatorsStore } from '../../stores/indicators';
import { formatPercentChange, formatMarketDate } from '../../utils/marketFormatters';
import * as echarts from 'echarts';

const indicatorsStore = useIndicatorsStore();
const indicators = computed(() => indicatorsStore.indicators);
const lastUpdate = computed(() => indicatorsStore.lastUpdate);
const sparklineCharts = ref({});

const formatLastUpdate = (date) => {
  if (!date) return 'N/A';
  return formatMarketDate(date);
};

const formatChange = (change) => {
  if (change === 0) return '0.00';
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}`;
};

const getChangeColor = (change) => {
  if (change > 0) return 'text-green-400';
  if (change < 0) return 'text-red-400';
  return 'text-gray-400';
};

const getStatusBgClass = (status) => {
  const classes = {
    positive: 'bg-green-500/20',
    negative: 'bg-red-500/20',
    neutral: 'bg-gray-500/20',
  };
  return classes[status] || classes.neutral;
};

const getStatusIcon = (status) => {
  const icons = {
    positive: 'fas fa-arrow-up text-green-400',
    negative: 'fas fa-arrow-down text-red-400',
    neutral: 'fas fa-minus text-gray-400',
  };
  return icons[status] || icons.neutral;
};

const initializeSparkline = (indicator) => {
  const containerId = `sparkline-${indicator.id}`;
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const chart = echarts.init(container, 'dark');
  
  const option = {
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
    },
    xAxis: {
      type: 'category',
      data: indicator.trend.map((_, i) => i),
      show: false,
    },
    yAxis: {
      type: 'value',
      show: false,
    },
    series: [
      {
        data: indicator.trend,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: indicator.status === 'positive' ? '#10b981' : indicator.status === 'negative' ? '#ef4444' : '#6b7280',
          width: 2,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: indicator.status === 'positive' ? 'rgba(16, 185, 129, 0.3)' : indicator.status === 'negative' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(107, 114, 128, 0.3)',
              },
              {
                offset: 1,
                color: 'transparent',
              },
            ],
          },
        },
      },
    ],
  };
  
  chart.setOption(option);
  sparklineCharts.value[indicator.id] = chart;
};

const initializeAllSparklines = async () => {
  await nextTick();
  indicators.value.forEach(indicator => {
    initializeSparkline(indicator);
  });
};

watch(() => indicators.value, () => {
  initializeAllSparklines();
}, { deep: true });

onMounted(() => {
  indicatorsStore.fetchIndicators();
  initializeAllSparklines();
  
  // Handle resize
  window.addEventListener('resize', () => {
    Object.values(sparklineCharts.value).forEach(chart => {
      if (chart) chart.resize();
    });
  });
});
</script>

