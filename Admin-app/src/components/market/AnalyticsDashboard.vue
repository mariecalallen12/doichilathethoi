<template>
  <div class="analytics-dashboard">
    <h3 class="dashboard-title">
      <i class="fas fa-chart-bar text-blue-400"></i>
      Customization Impact Analytics
    </h3>

    <!-- Time Range Selector -->
    <div class="time-range-selector">
      <button 
        v-for="range in timeRanges" 
        :key="range.value"
        @click="selectedTimeRange = range.value"
        :class="['time-btn', { active: selectedTimeRange === range.value }]"
      >
        {{ range.label }}
      </button>
    </div>

    <!-- Key Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon bg-green-500/20">
          <i class="fas fa-users text-green-400"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Affected Users</div>
          <div class="metric-value">{{ analytics.affectedUsers }}</div>
          <div class="metric-change positive">
            <i class="fas fa-arrow-up"></i>
            {{ analytics.userChange }}% vs last period
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon bg-blue-500/20">
          <i class="fas fa-chart-line text-blue-400"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Trading Volume Impact</div>
          <div class="metric-value">+{{ analytics.volumeImpact }}%</div>
          <div class="metric-change positive">
            <i class="fas fa-arrow-up"></i>
            ${{ formatVolume(analytics.volumeIncrease) }} increase
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon bg-purple-500/20">
          <i class="fas fa-coins text-purple-400"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Deposit Rate</div>
          <div class="metric-value">+{{ analytics.depositRate }}%</div>
          <div class="metric-change positive">
            <i class="fas fa-arrow-up"></i>
            {{ analytics.newDeposits }} new deposits
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon bg-yellow-500/20">
          <i class="fas fa-clock text-yellow-400"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Avg Session Duration</div>
          <div class="metric-value">+{{ analytics.sessionIncrease }}min</div>
          <div class="metric-change positive">
            <i class="fas fa-arrow-up"></i>
            {{ analytics.avgSession }}min total
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon bg-pink-500/20">
          <i class="fas fa-star text-pink-400"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Customer Satisfaction</div>
          <div class="metric-value">{{ analytics.satisfaction }}/5.0</div>
          <div class="metric-change positive">
            <i class="fas fa-arrow-up"></i>
            +{{ analytics.satisfactionChange }} points
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon bg-red-500/20">
          <i class="fas fa-percentage text-red-400"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Conversion Rate</div>
          <div class="metric-value">{{ analytics.conversionRate }}%</div>
          <div class="metric-change positive">
            <i class="fas fa-arrow-up"></i>
            +{{ analytics.conversionIncrease }}% vs baseline
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <!-- User Behavior Chart -->
      <div class="chart-card">
        <h4 class="chart-title">User Behavior Trends</h4>
        <div class="chart-container">
          <canvas ref="userBehaviorChart"></canvas>
        </div>
      </div>

      <!-- Preset Performance -->
      <div class="chart-card">
        <h4 class="chart-title">Preset Performance Comparison</h4>
        <div class="chart-container">
          <canvas ref="presetPerformanceChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Top Performing Customizations -->
    <div class="performance-table">
      <h4 class="table-title">
        <i class="fas fa-trophy text-yellow-400"></i>
        Top Performing Customizations
      </h4>
      
      <div class="table-responsive">
        <table class="performance-table-content">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Customization</th>
              <th>Type</th>
              <th>Impact Score</th>
              <th>Conversion</th>
              <th>Revenue</th>
              <th>Users</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in topPerformers" :key="index">
              <td>
                <div class="rank-badge" :class="getRankClass(index)">
                  {{ index + 1 }}
                </div>
              </td>
              <td>
                <div class="customization-name">{{ item.name }}</div>
              </td>
              <td>
                <span class="type-badge" :class="item.typeClass">
                  {{ item.type }}
                </span>
              </td>
              <td>
                <div class="impact-score">
                  <div class="score-bar">
                    <div 
                      class="score-fill"
                      :style="{ width: item.impactScore + '%' }"
                    ></div>
                  </div>
                  <span class="score-value">{{ item.impactScore }}%</span>
                </div>
              </td>
              <td class="text-green-400 font-semibold">
                +{{ item.conversion }}%
              </td>
              <td class="text-purple-400 font-semibold">
                ${{ formatNumber(item.revenue) }}
              </td>
              <td class="text-blue-400">
                {{ formatNumber(item.users) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- A/B Testing Results -->
    <div class="ab-testing-section">
      <h4 class="section-title">
        <i class="fas fa-flask text-green-400"></i>
        A/B Testing Results
      </h4>

      <div class="ab-tests-grid">
        <div v-for="test in abTests" :key="test.id" class="ab-test-card">
          <div class="test-header">
            <div>
              <div class="test-name">{{ test.name }}</div>
              <div class="test-period">{{ test.period }}</div>
            </div>
            <span class="test-status" :class="test.statusClass">
              {{ test.status }}
            </span>
          </div>

          <div class="test-comparison">
            <div class="variant-result">
              <div class="variant-label">Control (Original)</div>
              <div class="variant-metrics">
                <div class="metric">
                  <span class="label">Conversion:</span>
                  <span class="value">{{ test.control.conversion }}%</span>
                </div>
                <div class="metric">
                  <span class="label">Revenue:</span>
                  <span class="value">${{ formatNumber(test.control.revenue) }}</span>
                </div>
              </div>
            </div>

            <div class="vs-separator">VS</div>

            <div class="variant-result winner">
              <div class="variant-label">
                Variant (Modified)
                <i v-if="test.winner === 'variant'" class="fas fa-crown text-yellow-400 ml-2"></i>
              </div>
              <div class="variant-metrics">
                <div class="metric">
                  <span class="label">Conversion:</span>
                  <span class="value success">{{ test.variant.conversion }}%</span>
                </div>
                <div class="metric">
                  <span class="label">Revenue:</span>
                  <span class="value success">${{ formatNumber(test.variant.revenue) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="test-conclusion">
            <i class="fas fa-lightbulb text-yellow-400"></i>
            <span>{{ test.conclusion }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import Chart from 'chart.js/auto';

const props = defineProps({
  apiBaseUrl: {
    type: String,
    default: 'http://localhost:8001'
  }
});

// State
const selectedTimeRange = ref('7d');
const timeRanges = [
  { label: '24H', value: '24h' },
  { label: '7D', value: '7d' },
  { label: '30D', value: '30d' },
  { label: 'All', value: 'all' }
];

const analytics = ref({
  affectedUsers: 245,
  userChange: 23,
  volumeImpact: 28,
  volumeIncrease: 1250000,
  depositRate: 15,
  newDeposits: 87,
  sessionIncrease: 18,
  avgSession: 45,
  satisfaction: 4.7,
  satisfactionChange: 0.5,
  conversionRate: 32,
  conversionIncrease: 12
});

const topPerformers = ref([
  {
    name: 'VIP Mode',
    type: 'Preset',
    typeClass: 'type-preset',
    impactScore: 95,
    conversion: 35,
    revenue: 125000,
    users: 156
  },
  {
    name: 'Marketing Campaign',
    type: 'Preset',
    typeClass: 'type-preset',
    impactScore: 88,
    conversion: 28,
    revenue: 98000,
    users: 234
  },
  {
    name: 'BTC Manual Override',
    type: 'Custom',
    typeClass: 'type-custom',
    impactScore: 82,
    conversion: 22,
    revenue: 76000,
    users: 189
  },
  {
    name: 'Demo Presentation',
    type: 'Preset',
    typeClass: 'type-preset',
    impactScore: 75,
    conversion: 18,
    revenue: 54000,
    users: 145
  },
  {
    name: 'Global +5% Boost',
    type: 'Global',
    typeClass: 'type-global',
    impactScore: 68,
    conversion: 15,
    revenue: 42000,
    users: 198
  }
]);

const abTests = ref([
  {
    id: 1,
    name: 'Marketing Campaign Effectiveness',
    period: 'Dec 14-20, 2025',
    status: 'Completed',
    statusClass: 'status-completed',
    winner: 'variant',
    control: {
      conversion: 12.5,
      revenue: 45000
    },
    variant: {
      conversion: 16.8,
      revenue: 62000
    },
    conclusion: 'Variant outperformed by 34%. Recommended for permanent use.'
  },
  {
    id: 2,
    name: 'VIP Treatment Impact',
    period: 'Dec 15-21, 2025',
    status: 'Running',
    statusClass: 'status-running',
    winner: 'variant',
    control: {
      conversion: 8.2,
      revenue: 28000
    },
    variant: {
      conversion: 13.5,
      revenue: 48000
    },
    conclusion: 'Strong positive trend. 65% improvement in conversion rate.'
  }
]);

const userBehaviorChart = ref(null);
const presetPerformanceChart = ref(null);
let userChart = null;
let presetChart = null;

// Methods
const formatVolume = (value) => {
  if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M';
  if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K';
  return value.toFixed(0);
};

const formatNumber = (value) => {
  return value.toLocaleString('en-US');
};

const getRankClass = (index) => {
  if (index === 0) return 'rank-gold';
  if (index === 1) return 'rank-silver';
  if (index === 2) return 'rank-bronze';
  return '';
};

const initUserBehaviorChart = () => {
  if (!userBehaviorChart.value) return;

  const ctx = userBehaviorChart.value.getContext('2d');
  
  userChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'With Customizations',
          data: [145, 178, 192, 210, 235, 248, 265],
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Without Customizations',
          data: [120, 125, 130, 128, 135, 140, 145],
          borderColor: '#6b7280',
          backgroundColor: 'rgba(107, 114, 128, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#fff' }
        }
      },
      scales: {
        y: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        x: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      }
    }
  });
};

const initPresetPerformanceChart = () => {
  if (!presetPerformanceChart.value) return;

  const ctx = presetPerformanceChart.value.getContext('2d');
  
  presetChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['VIP Mode', 'Marketing', 'Demo', 'Risk Test', 'Conservative'],
      datasets: [
        {
          label: 'Conversion Rate (%)',
          data: [35, 28, 18, 8, 12],
          backgroundColor: '#22c55e'
        },
        {
          label: 'User Engagement',
          data: [42, 38, 25, 15, 20],
          backgroundColor: '#3b82f6'
        },
        {
          label: 'Revenue Impact',
          data: [48, 35, 22, 10, 18],
          backgroundColor: '#a855f7'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#fff' }
        }
      },
      scales: {
        y: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        x: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      }
    }
  });
};

// Lifecycle
onMounted(() => {
  initUserBehaviorChart();
  initPresetPerformanceChart();
});

watch(selectedTimeRange, () => {
  // Reload data based on selected time range
  console.log('Time range changed:', selectedTimeRange.value);
});
</script>

<style scoped>
.analytics-dashboard {
  padding: 2rem;
}

.dashboard-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.time-range-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.75rem;
  width: fit-content;
}

.time-btn {
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  background: transparent;
  color: #9ca3af;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.time-btn.active {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.metric-content {
  flex: 1;
}

.metric-label {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.25rem;
}

.metric-change {
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.metric-change.positive {
  color: #22c55e;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
}

.chart-container {
  height: 300px;
}

.performance-table {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.table-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.table-responsive {
  overflow-x: auto;
}

.performance-table-content {
  width: 100%;
  border-collapse: collapse;
}

.performance-table-content thead tr {
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.performance-table-content th {
  padding: 1rem;
  text-align: left;
  color: #9ca3af;
  font-weight: 600;
  font-size: 0.875rem;
}

.performance-table-content td {
  padding: 1rem;
  color: white;
}

.rank-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.1);
}

.rank-gold {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #fff;
}

.rank-silver {
  background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
  color: #1f2937;
}

.rank-bronze {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: #fff;
}

.customization-name {
  font-weight: 600;
}

.type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-preset {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.type-custom {
  background: rgba(168, 85, 247, 0.2);
  color: #a78bfa;
}

.type-global {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.impact-score {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.score-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6 0%, #6366f1 100%);
  border-radius: 1rem;
}

.score-value {
  font-weight: 600;
  min-width: 45px;
}

.ab-testing-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ab-tests-grid {
  display: grid;
  gap: 1.5rem;
}

.ab-test-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1.5rem;
}

.test-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
}

.test-period {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.test-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-completed {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.status-running {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.test-comparison {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.variant-result {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 1rem;
}

.variant-label {
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.variant-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric {
  display: flex;
  justify-content: space-between;
}

.metric .label {
  color: #9ca3af;
  font-size: 0.875rem;
}

.metric .value {
  color: white;
  font-weight: 600;
}

.metric .value.success {
  color: #22c55e;
}

.vs-separator {
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #6b7280;
}

.test-conclusion {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #86efac;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .test-comparison {
    grid-template-columns: 1fr;
  }

  .vs-separator {
    transform: rotate(90deg);
  }
}
</style>
