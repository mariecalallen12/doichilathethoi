<template>
  <section class="mb-8">
    <div class="market-card p-6">
      <h2 class="text-xl font-bold text-white mb-6">Phân tích thị trường</h2>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Left Column: Text Analysis -->
        <div class="space-y-6">
          <article class="bg-slate-800/50 p-6 rounded-lg border border-purple-500/20">
            <div class="flex items-center space-x-3 mb-4">
              <div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full flex items-center justify-center">
                <i class="fas fa-user-tie text-white"></i>
              </div>
              <div>
                <h3 class="text-white font-semibold">Chuyên gia: Nguyễn Văn A</h3>
                <p class="text-gray-400 text-sm">Senior Market Analyst</p>
              </div>
            </div>
            <h4 class="text-white font-bold mb-2">Xu hướng thị trường tuần này</h4>
            <p class="text-gray-300 text-sm leading-relaxed mb-4">
              Thị trường Forex đang cho thấy dấu hiệu tích cực với cặp EUR/USD có khả năng tiếp tục tăng trong tuần tới. 
              Các chỉ số kỹ thuật cho thấy momentum đang mạnh lên, đặc biệt là sau khi Fed công bố quyết định về lãi suất.
            </p>
            <div class="flex items-center space-x-4 text-sm">
              <span class="text-green-400">
                <i class="fas fa-arrow-up mr-1"></i>
                Khuyến nghị: Mua
              </span>
              <span class="text-gray-400">
                <i class="far fa-clock mr-1"></i>
                2 giờ trước
              </span>
            </div>
          </article>
          
          <article class="bg-slate-800/50 p-6 rounded-lg border border-purple-500/20">
            <div class="flex items-center space-x-3 mb-4">
              <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
                <i class="fas fa-chart-line text-white"></i>
              </div>
              <div>
                <h3 class="text-white font-semibold">Phân tích kỹ thuật</h3>
                <p class="text-gray-400 text-sm">Technical Analysis</p>
              </div>
            </div>
            <h4 class="text-white font-bold mb-2">Bitcoin: Kháng cự tại $45,000</h4>
            <p class="text-gray-300 text-sm leading-relaxed mb-4">
              BTC đang test mức kháng cự quan trọng tại $45,000. Nếu vượt qua được mức này, 
              có thể tiếp tục tăng lên $48,000. Tuy nhiên, cần chú ý đến volume giao dịch và các chỉ báo RSI.
            </p>
            <div class="flex items-center space-x-4 text-sm">
              <span class="text-yellow-400">
                <i class="fas fa-exclamation-triangle mr-1"></i>
                Cảnh báo: Rủi ro trung bình
              </span>
            </div>
          </article>
        </div>
        
        <!-- Right Column: Charts -->
        <div class="space-y-6">
          <div class="bg-slate-800/50 p-6 rounded-lg border border-purple-500/20">
            <h3 class="text-white font-semibold mb-4">Dự đoán xu hướng</h3>
            <div ref="trendChartContainer" class="w-full h-64"></div>
          </div>
          
          <div class="bg-slate-800/50 p-6 rounded-lg border border-purple-500/20">
            <h3 class="text-white font-semibold mb-4">Phân bổ danh mục đề xuất</h3>
            <div ref="portfolioChartContainer" class="w-full h-64"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const trendChartContainer = ref(null);
const portfolioChartContainer = ref(null);
let trendChart = null;
let portfolioChart = null;

const initializeTrendChart = () => {
  if (!trendChartContainer.value) return;
  
  trendChart = echarts.init(trendChartContainer.value, 'dark');
  
  const option = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['Dự đoán', 'Thực tế'],
      textStyle: {
        color: '#d1d5db',
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
      data: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
      axisLabel: {
        color: '#9ca3af',
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#9ca3af',
      },
    },
    series: [
      {
        name: 'Dự đoán',
        type: 'line',
        smooth: true,
        data: [1.08, 1.082, 1.085, 1.083, 1.086, 1.088, 1.09],
        lineStyle: {
          color: '#8B5CF6',
          width: 2,
        },
        itemStyle: {
          color: '#8B5CF6',
        },
      },
      {
        name: 'Thực tế',
        type: 'line',
        smooth: true,
        data: [1.08, 1.081, 1.084, 1.082, 1.085, null, null],
        lineStyle: {
          color: '#10b981',
          width: 2,
        },
        itemStyle: {
          color: '#10b981',
        },
      },
    ],
  };
  
  trendChart.setOption(option);
};

const initializePortfolioChart = () => {
  if (!portfolioChartContainer.value) return;
  
  portfolioChart = echarts.init(portfolioChartContainer.value, 'dark');
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}% ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: '#d1d5db',
      },
    },
    series: [
      {
        name: 'Phân bổ',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#1a0b2e',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            color: '#fff',
          },
        },
        labelLine: {
          show: false,
        },
        data: [
          { value: 35, name: 'Forex', itemStyle: { color: '#8B5CF6' } },
          { value: 30, name: 'Crypto', itemStyle: { color: '#3B82F6' } },
          { value: 20, name: 'Hàng hóa', itemStyle: { color: '#10B981' } },
          { value: 15, name: 'Chỉ số', itemStyle: { color: '#F59E0B' } },
        ],
      },
    ],
  };
  
  portfolioChart.setOption(option);
};

onMounted(() => {
  initializeTrendChart();
  initializePortfolioChart();
  
  window.addEventListener('resize', () => {
    if (trendChart) trendChart.resize();
    if (portfolioChart) portfolioChart.resize();
  });
});

onUnmounted(() => {
  if (trendChart) trendChart.dispose();
  if (portfolioChart) portfolioChart.dispose();
});
</script>

