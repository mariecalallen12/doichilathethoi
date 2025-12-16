<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header Navigation -->
    <AnalysisHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Phân Tích Thị Trường
        </h1>
        <p class="text-purple-200/80 text-lg">
          Công cụ phân tích kỹ thuật và cơ bản chuyên nghiệp
        </p>
      </div>

      <!-- Symbol Selector -->
      <div class="mb-6">
        <select
          v-model="selectedSymbol"
          @change="handleSymbolChange"
          class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
        >
          <option value="EUR/USD">EUR/USD</option>
          <option value="GBP/USD">GBP/USD</option>
          <option value="USD/JPY">USD/JPY</option>
          <option value="BTC/USD">BTC/USD</option>
          <option value="ETH/USD">ETH/USD</option>
          <option value="GOLD">GOLD</option>
        </select>
      </div>

      <!-- Navigation Tabs -->
      <div class="mb-8">
        <div class="flex flex-wrap gap-2 border-b border-purple-500/20 pb-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="selectTab(tab.id)"
            class="px-6 py-3 rounded-t-lg transition-all duration-300 flex items-center space-x-2"
            :class="{
              'text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text border-b-2 border-purple-400': activeTab === tab.id,
              'text-gray-400 hover:text-purple-300': activeTab !== tab.id
            }"
          >
            <i :class="tab.icon" class="text-lg"></i>
            <span class="font-medium">{{ tab.label }}</span>
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, provide, watch } from 'vue';
import { useAnalysisStore } from '../../stores/analysis';
import AnalysisHeader from './AnalysisHeader.vue';

const analysisStore = useAnalysisStore();
const activeTab = ref('technical');
const selectedSymbol = ref(analysisStore.selectedSymbol);

const tabs = [
  { id: 'technical', label: 'Phân Tích Kỹ Thuật', icon: 'fas fa-chart-line' },
  { id: 'fundamental', label: 'Phân Tích Cơ Bản', icon: 'fas fa-chart-bar' },
  { id: 'sentiment', label: 'Tâm Lý Thị Trường', icon: 'fas fa-smile' },
  { id: 'signals', label: 'Tín Hiệu Giao Dịch', icon: 'fas fa-bell' },
  { id: 'charts', label: 'Công Cụ Biểu Đồ', icon: 'fas fa-chart-area' },
];

const selectTab = (tabId) => {
  activeTab.value = tabId;
  // Scroll to section
  const element = document.getElementById(tabId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

const handleSymbolChange = () => {
  analysisStore.setSelectedSymbol(selectedSymbol.value);
  // Refetch data for new symbol
  analysisStore.fetchTechnicalAnalysis();
  analysisStore.fetchFundamentalAnalysis();
};

watch(() => analysisStore.selectedSymbol, (newSymbol) => {
  selectedSymbol.value = newSymbol;
});

provide('activeTab', activeTab);
provide('selectedSymbol', selectedSymbol);
</script>

<style scoped>
.tab-content {
  min-height: 60vh;
}
</style>

