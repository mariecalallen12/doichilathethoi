<template>
  <section id="sentiment" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Tâm Lý Thị Trường</h2>
      <p class="text-purple-200/80">Chỉ số Fear & Greed và tâm lý xã hội</p>
    </div>

    <!-- Loading State -->
    <div v-if="analysisStore.isLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
      <p class="text-purple-200 mt-4">Đang tải dữ liệu...</p>
    </div>

    <!-- Fear & Greed Index -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
        <h3 class="text-xl font-bold text-white mb-4">Fear & Greed Index</h3>
        <div class="relative">
          <div class="h-32 bg-slate-700 rounded-lg flex items-center justify-center relative overflow-hidden">
            <div
              class="absolute inset-0 transition-all"
              :class="getFearGreedColor(fearGreedIndex)"
              :style="{ width: fearGreedIndex + '%' }"
            ></div>
            <div class="relative z-10 text-center">
              <div class="text-4xl font-bold text-white mb-2">{{ fearGreedIndex }}</div>
              <div class="text-sm text-gray-300">{{ getFearGreedLabel(fearGreedIndex) }}</div>
            </div>
          </div>
          <div class="flex justify-between mt-2 text-xs text-gray-400">
            <span>Extreme Fear</span>
            <span>Neutral</span>
            <span>Extreme Greed</span>
          </div>
        </div>
      </div>

      <!-- Social Sentiment -->
      <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
        <h3 class="text-xl font-bold text-white mb-4">Tâm Lý Mạng Xã Hội</h3>
        <div class="space-y-4">
          <div v-for="(value, platform) in socialSentiment" :key="platform">
            <div class="flex items-center justify-between mb-2">
              <span class="text-gray-300 capitalize">{{ formatPlatform(platform) }}</span>
              <span class="text-purple-400 font-bold">{{ (value * 100).toFixed(0) }}%</span>
            </div>
            <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-purple-400 to-indigo-400 transition-all"
                :style="{ width: (value * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Market Sentiment Summary -->
    <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
      <h3 class="text-xl font-bold text-white mb-4">Tổng Kết Tâm Lý</h3>
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div
            class="px-4 py-2 rounded-lg text-lg font-bold"
            :class="getMarketSentimentClass(marketSentiment)"
          >
            {{ getMarketSentimentLabel(marketSentiment) }}
          </div>
          <div class="text-gray-400">
            Dựa trên phân tích tổng hợp
          </div>
        </div>
        <div class="text-sm text-gray-400">
          Cập nhật: {{ formatDate(new Date()) }}
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useAnalysisStore } from '../../stores/analysis';

const analysisStore = useAnalysisStore();

const sentiment = computed(() => analysisStore.sentiment || {});

const fearGreedIndex = computed(() => sentiment.value.fear_greed_index || 50);

const socialSentiment = computed(() => {
  return sentiment.value.social_sentiment || {
    twitter: 0.5,
    reddit: 0.5,
    overall: 0.5
  };
});

const marketSentiment = computed(() => sentiment.value.market_sentiment || 'neutral');

const getFearGreedColor = (index) => {
  if (index < 25) return 'bg-red-600';
  if (index < 45) return 'bg-orange-500';
  if (index < 55) return 'bg-yellow-500';
  if (index < 75) return 'bg-green-500';
  return 'bg-emerald-600';
};

const getFearGreedLabel = (index) => {
  if (index < 25) return 'Extreme Fear';
  if (index < 45) return 'Fear';
  if (index < 55) return 'Neutral';
  if (index < 75) return 'Greed';
  return 'Extreme Greed';
};

const formatPlatform = (platform) => {
  const labels = {
    twitter: 'Twitter',
    reddit: 'Reddit',
    overall: 'Tổng thể'
  };
  return labels[platform] || platform;
};

const getMarketSentimentClass = (sentiment) => {
  const classes = {
    bullish: 'bg-green-500/20 text-green-400',
    bearish: 'bg-red-500/20 text-red-400',
    neutral: 'bg-yellow-500/20 text-yellow-400'
  };
  return classes[sentiment] || 'bg-gray-500/20 text-gray-400';
};

const getMarketSentimentLabel = (sentiment) => {
  const labels = {
    bullish: 'Tăng Giá',
    bearish: 'Giảm Giá',
    neutral: 'Trung Lập'
  };
  return labels[sentiment] || sentiment;
};

const formatDate = (date) => {
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

onMounted(() => {
  analysisStore.fetchSentiment();
});
</script>

<style scoped>
/* Sentiment indicators styles */
</style>

