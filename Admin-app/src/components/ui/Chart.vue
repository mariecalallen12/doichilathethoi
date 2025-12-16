<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'vue-chartjs';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const props = defineProps({
  type: {
    type: String,
    default: 'line',
    validator: (value) => ['line', 'bar', 'pie', 'doughnut'].includes(value),
  },
  data: {
    type: Object,
    default: () => ({}),
  },
  options: {
    type: Object,
    default: () => ({}),
  },
  height: {
    type: String,
    default: '300px',
  },
});

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: 'rgba(255, 255, 255, 0.8)',
      },
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'rgba(255, 255, 255, 1)',
      bodyColor: 'rgba(255, 255, 255, 0.8)',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
    },
  },
  scales: {
    x: {
      ticks: {
        color: 'rgba(255, 255, 255, 0.6)',
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.05)',
      },
    },
    y: {
      ticks: {
        color: 'rgba(255, 255, 255, 0.6)',
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.05)',
      },
    },
  },
};

const chartData = ref({
  labels: [],
  datasets: [],
});

const chartOptions = ref({});

const updateChartData = () => {
  if (props.data && props.data.labels && props.data.datasets) {
    chartData.value = {
      labels: props.data.labels,
      datasets: props.data.datasets.map((dataset) => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || 'rgba(0, 102, 204, 0.2)',
        borderColor: dataset.borderColor || 'rgba(0, 102, 204, 1)',
        borderWidth: dataset.borderWidth || 2,
        fill: dataset.fill !== undefined ? dataset.fill : props.type === 'line',
      })),
    };
  } else {
    // Default empty data
    chartData.value = {
      labels: [],
      datasets: [],
    };
  }

  chartOptions.value = {
    ...defaultOptions,
    ...props.options,
  };
};

watch(
  () => [props.data, props.options],
  () => {
    updateChartData();
  },
  { deep: true, immediate: true }
);

onMounted(() => {
  updateChartData();
});
</script>

<template>
  <div :style="{ height }" class="w-full">
    <Line
      v-if="type === 'line' && chartData.labels.length > 0"
      :data="chartData"
      :options="chartOptions"
    />
    <Bar
      v-else-if="type === 'bar' && chartData.labels.length > 0"
      :data="chartData"
      :options="chartOptions"
    />
    <Pie
      v-else-if="type === 'pie' && chartData.labels.length > 0"
      :data="chartData"
      :options="chartOptions"
    />
    <Doughnut
      v-else-if="type === 'doughnut' && chartData.labels.length > 0"
      :data="chartData"
      :options="chartOptions"
    />
    <div
      v-else
      class="w-full h-full flex items-center justify-center bg-white/5 rounded-lg p-4"
  >
    <div class="text-center text-white/40">
      <i class="fas fa-chart-line text-4xl mb-2"></i>
        <p class="text-sm">Đang tải dữ liệu biểu đồ...</p>
      </div>
    </div>
  </div>
</template>

