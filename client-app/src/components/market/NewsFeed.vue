<template>
  <section class="mb-8">
    <div class="market-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-white">Tin tức tài chính</h2>
        <button
          @click="refreshNews"
          class="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg text-purple-300 transition-colors text-sm"
        >
          <i class="fas fa-sync-alt mr-2" :class="{ 'animate-spin': loading }"></i>
          Làm mới
        </button>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <article
          v-for="news in filteredNews"
          :key="news.id"
          @click="selectNews(news)"
          class="news-card p-4 cursor-pointer"
        >
          <div class="relative mb-3 h-40 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-lg overflow-hidden">
            <div class="absolute inset-0 flex items-center justify-center">
              <i class="fas fa-newspaper text-4xl text-purple-400/50"></i>
            </div>
            <div
              v-if="news.thumbnail"
              class="absolute inset-0 bg-cover bg-center"
              :style="{ backgroundImage: `url(${news.thumbnail})` }"
            ></div>
            <div class="absolute top-2 right-2">
              <span
                class="px-2 py-1 text-xs font-semibold rounded"
                :class="getImpactClass(news.impact)"
              >
                {{ getImpactLabel(news.impact) }}
              </span>
            </div>
          </div>
          
          <h3 class="text-white font-semibold mb-2 line-clamp-2">{{ news.title }}</h3>
          <p class="text-gray-400 text-sm mb-3 line-clamp-2">{{ news.summary }}</p>
          
          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>
              <i class="far fa-clock mr-1"></i>
              {{ formatRelativeTime(news.publishedAt) }}
            </span>
            <span class="capitalize">{{ getCategoryLabel(news.category) }}</span>
          </div>
        </article>
      </div>
      
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import { useNewsStore } from '../../stores/news';
import { formatRelativeTime } from '../../utils/marketFormatters';

const newsStore = useNewsStore();
const loading = computed(() => newsStore.loading);
const filteredNews = computed(() => newsStore.filteredNews.slice(0, 6));

const refreshNews = () => {
  newsStore.fetchNews();
};

const selectNews = (news) => {
  console.log('Selected news:', news);
  // Can emit event or navigate to news detail page
};

const getImpactClass = (impact) => {
  const classes = {
    high: 'bg-red-500/20 text-red-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    low: 'bg-blue-500/20 text-blue-400',
  };
  return classes[impact] || classes.low;
};

const getImpactLabel = (impact) => {
  const labels = {
    high: 'Tác động cao',
    medium: 'Tác động trung bình',
    low: 'Tác động thấp',
  };
  return labels[impact] || 'Tác động thấp';
};

const getCategoryLabel = (category) => {
  const labels = {
    monetary: 'Tiền tệ',
    crypto: 'Crypto',
    economic: 'Kinh tế',
    commodity: 'Hàng hóa',
  };
  return labels[category] || category;
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

