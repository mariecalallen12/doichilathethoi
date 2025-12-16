<template>
  <section class="mb-6">
    <div class="flex flex-wrap gap-2 border-b border-purple-500/20 pb-4">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="selectTab(tab.id)"
        class="asset-tab px-6 py-3 rounded-t-lg transition-all duration-300 flex items-center space-x-2"
        :class="{
          'active text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text': selectedTab === tab.id,
          'text-gray-400 hover:text-purple-300': selectedTab !== tab.id
        }"
      >
        <i :class="tab.icon" class="text-lg"></i>
        <span class="font-medium">{{ tab.label }}</span>
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useMarketStore } from '../../stores/market';

const marketStore = useMarketStore();
const selectedTab = ref('all');

const tabs = [
  { id: 'all', label: 'Tất cả', icon: 'fas fa-th-large' },
  { id: 'forex', label: 'Forex', icon: 'fas fa-exchange-alt' },
  { id: 'crypto', label: 'Cryptocurrency', icon: 'fab fa-bitcoin' },
  { id: 'commodity', label: 'Hàng hóa', icon: 'fas fa-gem' },
  { id: 'index', label: 'Chỉ số', icon: 'fas fa-chart-bar' },
];

const selectTab = (tabId) => {
  selectedTab.value = tabId;
  marketStore.setCategory(tabId);
};

watch(() => marketStore.selectedCategory, (newCategory) => {
  selectedTab.value = newCategory;
});
</script>

<style scoped>
.asset-tab {
  position: relative;
}

.asset-tab.active {
  color: transparent;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>

