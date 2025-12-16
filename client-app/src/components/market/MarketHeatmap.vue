<template>
  <section class="mb-8">
    <div class="market-card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-white">Market Heatmap</h2>
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2 text-sm">
            <div class="w-4 h-4 bg-red-500 rounded"></div>
            <span class="text-gray-400">Giảm</span>
          </div>
          <div class="flex items-center space-x-2 text-sm">
            <div class="w-4 h-4 bg-green-500 rounded"></div>
            <span class="text-gray-400">Tăng</span>
          </div>
        </div>
      </div>
      
      <div ref="heatmapContainer" class="w-full h-96 rounded-lg overflow-hidden"></div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useMarketStore } from '../../stores/market';
import * as echarts from 'echarts';

const marketStore = useMarketStore();
const heatmapContainer = ref(null);
let heatmapChart = null;

const generateHeatmapData = () => {
  const instruments = marketStore.instruments;
  const data = instruments.map((instrument, index) => {
    const marketCap = (instrument.volume || 0) * (instrument.price || 0);
    const changePercent = instrument.changePercent || 0;
    
    return {
      name: instrument.symbol,
      value: [
        index % 5, // x position
        Math.floor(index / 5), // y position
        marketCap, // size
        changePercent, // color
      ],
      itemStyle: {
        color: changePercent >= 0 ? '#10b981' : '#ef4444',
      },
      label: {
        show: true,
        formatter: '{b}\n{c3}%',
        color: '#fff',
        fontSize: 10,
      },
    };
  });
  
  return data;
};

const initializeHeatmap = () => {
  if (!heatmapContainer.value) return;
  
  heatmapChart = echarts.init(heatmapContainer.value, 'dark');
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const data = params.data;
        return `
          <div class="p-2">
            <div class="font-bold text-white">${data.name}</div>
            <div class="text-sm text-gray-300">Thay đổi: ${data.value[3]}%</div>
            <div class="text-sm text-gray-300">Market Cap: ${formatNumber(data.value[2])}</div>
          </div>
        `;
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
      data: Array.from({ length: 5 }, (_, i) => i),
      show: false,
    },
    yAxis: {
      type: 'category',
      data: Array.from({ length: Math.ceil(marketStore.instruments.length / 5) }, (_, i) => i),
      show: false,
    },
    visualMap: {
      min: -10,
      max: 10,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#ef4444', '#6b7280', '#10b981'],
      },
      show: false,
    },
    series: [
      {
        name: 'Market Heatmap',
        type: 'scatter',
        data: generateHeatmapData(),
        symbolSize: (val) => {
          const maxSize = Math.max(...marketStore.instruments.map(i => (i.volume || 0) * (i.price || 0)));
          return Math.max(30, (val[2] / maxSize) * 150);
        },
        itemStyle: {
          borderColor: '#1a0b2e',
          borderWidth: 2,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(139, 92, 246, 0.5)',
          },
        },
      },
    ],
  };
  
  heatmapChart.setOption(option);
  
  // Handle resize
  window.addEventListener('resize', handleResize);
};

const formatNumber = (num) => {
  if (num >= 1000000000) return `${(num / 1000000000).toFixed(2)}B`;
  if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(2)}K`;
  return num.toFixed(2);
};

const handleResize = () => {
  if (heatmapChart) {
    heatmapChart.resize();
  }
};

watch(() => marketStore.instruments, () => {
  if (heatmapChart) {
    heatmapChart.setOption({
      series: [{
        data: generateHeatmapData(),
      }],
    });
  }
}, { deep: true });

onMounted(() => {
  initializeHeatmap();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (heatmapChart) {
    heatmapChart.dispose();
  }
});
</script>

