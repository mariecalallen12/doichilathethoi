import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { newsApi } from '../services/api/news';

export const useNewsStore = defineStore('news', () => {
  const newsItems = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const filters = ref({
    category: 'all',
    impact: 'all',
    timeframe: '24h',
  });

  // No mock data - news will be fetched from real API only
  // newsItems.value starts as empty array and will be populated by fetchNews()

  const filteredNews = computed(() => {
    let filtered = [...newsItems.value];

    if (filters.value.category !== 'all') {
      filtered = filtered.filter(item => item.category === filters.value.category);
    }

    if (filters.value.impact !== 'all') {
      filtered = filtered.filter(item => item.impact === filters.value.impact);
    }

    return filtered.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
  });

  async function fetchNews() {
    loading.value = true;
    error.value = null;
    try {
      const data = await newsApi.getNews(filters.value);
      newsItems.value = data;
    } catch (err) {
      error.value = err.message;
      console.error('Failed to fetch news:', err);
    } finally {
      loading.value = false;
    }
  }

  function setFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function getNewsById(id) {
    return newsItems.value.find(item => item.id === id);
  }

  return {
    newsItems,
    filteredNews,
    loading,
    error,
    filters,
    fetchNews,
    setFilters,
    getNewsById,
  };
});

