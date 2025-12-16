<template>
  <section id="fundamental" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Phân Tích Cơ Bản</h2>
      <p class="text-purple-200/80">Dữ liệu kinh tế và tài chính</p>
    </div>

    <!-- Loading State -->
    <div v-if="analysisStore.isLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
      <p class="text-purple-200 mt-4">Đang tải dữ liệu...</p>
    </div>

    <!-- Economic Indicators -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
      <div
        v-for="(value, key) in economicIndicators"
        :key="key"
        class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-white">{{ formatIndicatorName(key) }}</h3>
          <span
            class="px-2 py-1 rounded text-xs font-semibold"
            :class="getChangeClass(value.change)"
          >
            {{ value.change >= 0 ? '+' : '' }}{{ value.change }}%
          </span>
        </div>
        <div class="text-3xl font-bold text-purple-400 mb-2">{{ value.value }}%</div>
        <div class="text-sm text-gray-400">Giá trị hiện tại</div>
      </div>
    </div>

    <!-- News Sentiment -->
    <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20 mb-6">
      <h3 class="text-xl font-bold text-white mb-4">Tâm Lý Tin Tức</h3>
      <div class="flex items-center space-x-4">
        <div class="flex-1">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-400">Tổng thể</span>
            <span
              class="px-3 py-1 rounded text-sm font-semibold"
              :class="getSentimentClass(fundamentalData.news_sentiment)"
            >
              {{ getSentimentLabel(fundamentalData.news_sentiment) }}
            </span>
          </div>
          <div class="h-3 bg-slate-700 rounded-full overflow-hidden">
            <div
              class="h-full transition-all"
              :class="getSentimentBarClass(fundamentalData.news_sentiment)"
              :style="{ width: getSentimentWidth(fundamentalData.news_sentiment) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Analyst Ratings -->
    <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
      <h3 class="text-xl font-bold text-white mb-4">Đánh Giá Của Chuyên Gia</h3>
      <div class="grid grid-cols-3 gap-4">
        <div class="text-center p-4 bg-green-500/20 rounded-lg">
          <div class="text-3xl font-bold text-green-400">{{ analystRatings.buy || 0 }}</div>
          <div class="text-sm text-gray-400 mt-2">Mua</div>
        </div>
        <div class="text-center p-4 bg-yellow-500/20 rounded-lg">
          <div class="text-3xl font-bold text-yellow-400">{{ analystRatings.hold || 0 }}</div>
          <div class="text-sm text-gray-400 mt-2">Giữ</div>
        </div>
        <div class="text-center p-4 bg-red-500/20 rounded-lg">
          <div class="text-3xl font-bold text-red-400">{{ analystRatings.sell || 0 }}</div>
          <div class="text-sm text-gray-400 mt-2">Bán</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useAnalysisStore } from '../../stores/analysis';

const analysisStore = useAnalysisStore();

const fundamentalData = computed(() => analysisStore.fundamentalData || {});

const economicIndicators = computed(() => {
  return fundamentalData.value.economic_indicators || {};
});

const analystRatings = computed(() => {
  return fundamentalData.value.analyst_ratings || { buy: 0, hold: 0, sell: 0 };
});

const formatIndicatorName = (key) => {
  const names = {
    gdp: 'GDP',
    inflation: 'Lạm Phát',
    interest_rate: 'Lãi Suất'
  };
  return names[key] || key;
};

const getChangeClass = (change) => {
  if (change >= 0) return 'bg-green-500/20 text-green-400';
  return 'bg-red-500/20 text-red-400';
};

const getSentimentClass = (sentiment) => {
  const classes = {
    positive: 'bg-green-500/20 text-green-400',
    neutral: 'bg-yellow-500/20 text-yellow-400',
    negative: 'bg-red-500/20 text-red-400'
  };
  return classes[sentiment] || 'bg-gray-500/20 text-gray-400';
};

const getSentimentLabel = (sentiment) => {
  const labels = {
    positive: 'Tích Cực',
    neutral: 'Trung Lập',
    negative: 'Tiêu Cực'
  };
  return labels[sentiment] || sentiment;
};

const getSentimentBarClass = (sentiment) => {
  const classes = {
    positive: 'bg-gradient-to-r from-green-400 to-emerald-400',
    neutral: 'bg-gradient-to-r from-yellow-400 to-amber-400',
    negative: 'bg-gradient-to-r from-red-400 to-rose-400'
  };
  return classes[sentiment] || 'bg-gray-400';
};

const getSentimentWidth = (sentiment) => {
  const widths = {
    positive: 75,
    neutral: 50,
    negative: 25
  };
  return widths[sentiment] || 50;
};

onMounted(() => {
  analysisStore.fetchFundamentalAnalysis();
});
</script>

<style scoped>
/* Fundamental analysis styles */
</style>

