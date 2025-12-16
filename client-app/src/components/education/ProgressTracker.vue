<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
    <h3 class="text-xl font-bold text-white mb-4">Tiến độ học tập</h3>
    
    <!-- Overall Progress -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-gray-400">Tổng tiến độ</span>
        <span class="text-purple-400 font-bold">{{ overallProgress }}%</span>
      </div>
      <div class="h-3 bg-slate-700 rounded-full overflow-hidden">
        <div
          class="h-full bg-gradient-to-r from-purple-400 to-indigo-400 transition-all"
          :style="{ width: `${overallProgress}%` }"
        ></div>
      </div>
    </div>

    <!-- Category Progress -->
    <div class="space-y-4">
      <div v-for="category in categories" :key="category.id" class="space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <i :class="category.icon" class="text-purple-400"></i>
            <span class="text-gray-300">{{ category.label }}</span>
          </div>
          <span class="text-purple-400 text-sm font-semibold">{{ getCategoryProgress(category.id) }}%</span>
        </div>
        <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-purple-400 to-indigo-400 transition-all"
            :style="{ width: `${getCategoryProgress(category.id)}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="mt-6 grid grid-cols-3 gap-4 pt-6 border-t border-purple-500/20">
      <div class="text-center">
        <div class="text-2xl font-bold text-purple-400">{{ completedCount }}</div>
        <div class="text-xs text-gray-400 mt-1">Đã hoàn thành</div>
      </div>
      <div class="text-center">
        <div class="text-2xl font-bold text-yellow-400">{{ inProgressCount }}</div>
        <div class="text-xs text-gray-400 mt-1">Đang học</div>
      </div>
      <div class="text-center">
        <div class="text-2xl font-bold text-gray-400">{{ notStartedCount }}</div>
        <div class="text-xs text-gray-400 mt-1">Chưa bắt đầu</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useEducationStore } from '../../stores/education';

const educationStore = useEducationStore();

const categories = [
  { id: 'video', label: 'Video Tutorials', icon: 'fas fa-video' },
  { id: 'ebook', label: 'Ebook Strategies', icon: 'fas fa-book' },
  { id: 'calendar', label: 'Lịch Kinh Tế', icon: 'fas fa-calendar' },
  { id: 'report', label: 'Phân Tích Thị Trường', icon: 'fas fa-chart-line' },
];

const overallProgress = computed(() => {
  const total = educationStore.videos.length + educationStore.ebooks.length + educationStore.reports.length;
  if (total === 0) return 0;
  
  const completed = getCompletedCount();
  return Math.round((completed / total) * 100);
});

const getCategoryProgress = (categoryId) => {
  let items = [];
  let progressData = {};
  
  switch (categoryId) {
    case 'video':
      items = educationStore.videos;
      progressData = educationStore.progress.video || {};
      break;
    case 'ebook':
      items = educationStore.ebooks;
      progressData = educationStore.progress.ebook || {};
      break;
    case 'report':
      items = educationStore.reports;
      progressData = educationStore.progress.report || {};
      break;
    default:
      return 0;
  }
  
  if (items.length === 0) return 0;
  
  const completed = items.filter(item => {
    const itemProgress = progressData[item.id];
    return itemProgress && itemProgress.progress === 100;
  }).length;
  
  return Math.round((completed / items.length) * 100);
};

const getCompletedCount = () => {
  let count = 0;
  
  // Videos
  const videoProgress = educationStore.progress.video || {};
  count += educationStore.videos.filter(v => {
    const progress = videoProgress[v.id];
    return progress && progress.progress === 100;
  }).length;
  
  // Ebooks
  const ebookProgress = educationStore.progress.ebook || {};
  count += educationStore.ebooks.filter(e => {
    const progress = ebookProgress[e.id];
    return progress && progress.progress === 100;
  }).length;
  
  // Reports
  const reportProgress = educationStore.progress.report || {};
  count += educationStore.reports.filter(r => {
    const progress = reportProgress[r.id];
    return progress && progress.progress === 100;
  }).length;
  
  return count;
};

const completedCount = computed(() => getCompletedCount());

const inProgressCount = computed(() => {
  let count = 0;
  const allProgress = educationStore.progress;
  
  // Check all items
  [...educationStore.videos, ...educationStore.ebooks, ...educationStore.reports].forEach(item => {
    const type = item.id.startsWith('video') ? 'video' : item.id.startsWith('ebook') ? 'ebook' : 'report';
    const progress = allProgress[type]?.[item.id];
    if (progress && progress.progress > 0 && progress.progress < 100) {
      count++;
    }
  });
  
  return count;
});

const notStartedCount = computed(() => {
  const total = educationStore.videos.length + educationStore.ebooks.length + educationStore.reports.length;
  return total - completedCount.value - inProgressCount.value;
});
</script>

<style scoped>
/* Progress tracker styles */
</style>

