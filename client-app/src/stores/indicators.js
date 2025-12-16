import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { indicatorsApi } from '../services/api/indicators';

export const useIndicatorsStore = defineStore('indicators', () => {
  const indicators = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const lastUpdate = ref(null);

  // No mock data - indicators will be fetched from real API only
  // indicators.value starts as empty array and will be populated by fetchIndicators()

  const indicatorsByCountry = computed(() => {
    const grouped = {};
    indicators.value.forEach(indicator => {
      if (!grouped[indicator.country]) {
        grouped[indicator.country] = [];
      }
      grouped[indicator.country].push(indicator);
    });
    return grouped;
  });

  async function fetchIndicators() {
    loading.value = true;
    error.value = null;
    try {
      const data = await indicatorsApi.getIndicators();
      indicators.value = data;
      lastUpdate.value = new Date();
    } catch (err) {
      error.value = err.message;
      console.error('Failed to fetch indicators:', err);
    } finally {
      loading.value = false;
    }
  }

  function getIndicatorById(id) {
    return indicators.value.find(ind => ind.id === id);
  }

  function getIndicatorsByCountry(country) {
    return indicators.value.filter(ind => ind.country === country);
  }

  return {
    indicators,
    indicatorsByCountry,
    loading,
    error,
    lastUpdate,
    fetchIndicators,
    getIndicatorById,
    getIndicatorsByCountry,
  };
});

