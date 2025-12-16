<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header Navigation -->
    <EducationHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Tài Nguyên Giáo Dục
        </h1>
        <p class="text-purple-200/80 text-lg">
          Nâng cao kỹ năng giao dịch với tài liệu chuyên nghiệp
        </p>
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
import { ref, provide } from 'vue';
import EducationHeader from './EducationHeader.vue';

const activeTab = ref('videos');

const tabs = [
  { id: 'videos', label: 'Video Tutorials', icon: 'fas fa-video' },
  { id: 'ebooks', label: 'Ebook Strategies', icon: 'fas fa-book' },
  { id: 'calendar', label: 'Lịch Kinh Tế', icon: 'fas fa-calendar' },
  { id: 'reports', label: 'Phân Tích Thị Trường', icon: 'fas fa-chart-line' },
];

const selectTab = (tabId) => {
  activeTab.value = tabId;
  // Scroll to section
  const element = document.getElementById(tabId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

provide('activeTab', activeTab);
</script>

<style scoped>
.tab-content {
  min-height: 60vh;
}
</style>

