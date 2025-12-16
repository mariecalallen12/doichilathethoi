<template>
  <section id="charts" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Công Cụ Biểu Đồ</h2>
      <p class="text-purple-200/80">Phân tích đa khung thời gian và backtesting</p>
    </div>

    <!-- Multi-Timeframe Analysis -->
    <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20 mb-6">
      <h3 class="text-xl font-bold text-white mb-4">Phân Tích Đa Khung Thời Gian</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          v-for="tf in timeframes"
          :key="tf"
          class="bg-slate-700/50 rounded-lg p-4 cursor-pointer hover:bg-slate-700 transition-all"
          :class="{ 'ring-2 ring-purple-400': selectedTimeframe === tf }"
          @click="selectTimeframe(tf)"
        >
          <div class="text-center">
            <div class="text-lg font-bold text-white mb-1">{{ tf }}</div>
            <div class="text-xs text-gray-400">Khung thời gian</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Backtesting Interface -->
    <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20 mb-6">
      <h3 class="text-xl font-bold text-white mb-4">Backtesting</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm text-gray-400 mb-2">Ngày bắt đầu</label>
          <input
            v-model="backtestData.start_date"
            type="date"
            class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">Ngày kết thúc</label>
          <input
            v-model="backtestData.end_date"
            type="date"
            class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">Vốn ban đầu</label>
          <input
            v-model.number="backtestData.initial_capital"
            type="number"
            class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white"
            placeholder="10000"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">Chiến lược</label>
          <select
            v-model="backtestData.strategy"
            class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white"
          >
            <option value="moving_average">Moving Average</option>
            <option value="rsi">RSI Strategy</option>
            <option value="macd">MACD Strategy</option>
            <option value="custom">Custom</option>
          </select>
        </div>
      </div>
      <button
        @click="runBacktest"
        :disabled="isRunningBacktest"
        class="mt-6 w-full md:w-auto px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50"
      >
        <i class="fas fa-play mr-2"></i>
        {{ isRunningBacktest ? 'Đang chạy...' : 'Chạy Backtest' }}
      </button>
    </div>

    <!-- Backtest Results -->
    <div v-if="backtestResults" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
      <h3 class="text-xl font-bold text-white mb-4">Kết Quả Backtest</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <div class="text-sm text-gray-400 mb-1">Tổng lợi nhuận</div>
          <div class="text-2xl font-bold" :class="backtestResults.total_return >= 0 ? 'text-green-400' : 'text-red-400'">
            {{ backtestResults.total_return >= 0 ? '+' : '' }}{{ backtestResults.total_return.toFixed(2) }}%
          </div>
        </div>
        <div>
          <div class="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
          <div class="text-2xl font-bold text-purple-400">{{ backtestResults.sharpe_ratio?.toFixed(2) || 'N/A' }}</div>
        </div>
        <div>
          <div class="text-sm text-gray-400 mb-1">Max Drawdown</div>
          <div class="text-2xl font-bold text-red-400">{{ backtestResults.max_drawdown?.toFixed(2) || 'N/A' }}%</div>
        </div>
        <div>
          <div class="text-sm text-gray-400 mb-1">Số giao dịch</div>
          <div class="text-2xl font-bold text-white">{{ backtestResults.total_trades || 0 }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAnalysisStore } from '../../stores/analysis';

const analysisStore = useAnalysisStore();
const selectedTimeframe = ref('1h');
const isRunningBacktest = ref(false);
const backtestResults = ref(null);

const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];

const backtestData = ref({
  start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0],
  initial_capital: 10000,
  strategy: 'moving_average'
});

const selectTimeframe = (tf) => {
  selectedTimeframe.value = tf;
  analysisStore.setTimeFrame(tf);
  // Update chart with new timeframe
};

const runBacktest = async () => {
  isRunningBacktest.value = true;
  try {
    const results = await analysisStore.runBacktest(backtestData.value);
    backtestResults.value = results;
  } catch (error) {
    console.error('Error running backtest:', error);
    // Show error message
  } finally {
    isRunningBacktest.value = false;
  }
};
</script>

<style scoped>
/* Chart analysis tools styles */
</style>

