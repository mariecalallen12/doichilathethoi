<template>
  <div
    class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl overflow-hidden border border-purple-500/20 hover:border-purple-400/40 transition-all cursor-pointer transform hover:scale-105"
    @click="$emit('click', course)"
  >
    <!-- Thumbnail -->
    <div class="relative h-48 bg-gradient-to-br from-purple-600/20 to-indigo-600/20">
      <img
        v-if="course.thumbnail"
        :src="course.thumbnail"
        :alt="course.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <i :class="type === 'video' ? 'fas fa-video' : 'fas fa-book'" class="text-4xl text-purple-400/50"></i>
      </div>
      
      <!-- Play Button for Videos -->
      <div v-if="type === 'video'" class="absolute inset-0 flex items-center justify-center">
        <div class="w-16 h-16 bg-purple-600/80 rounded-full flex items-center justify-center hover:bg-purple-500 transition-all">
          <i class="fas fa-play text-white text-xl ml-1"></i>
        </div>
      </div>

      <!-- Duration Badge -->
      <div v-if="type === 'video' && course.duration" class="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded text-xs text-white">
        {{ formatDuration(course.duration) }}
      </div>

      <!-- Level Badge -->
      <div v-if="course.level" class="absolute top-2 left-2 px-2 py-1 rounded text-xs font-semibold"
        :class="{
          'bg-green-500/80 text-white': course.level === 'beginner',
          'bg-yellow-500/80 text-white': course.level === 'intermediate',
          'bg-red-500/80 text-white': course.level === 'advanced'
        }">
        {{ getLevelLabel(course.level) }}
      </div>
    </div>

    <!-- Content -->
    <div class="p-4">
      <h3 class="text-white font-bold text-lg mb-2 line-clamp-2">{{ course.title }}</h3>
      <p class="text-gray-400 text-sm mb-4 line-clamp-2">{{ course.description }}</p>
      
      <!-- Meta Info -->
      <div class="flex items-center justify-between text-sm text-gray-500">
        <div class="flex items-center space-x-4">
          <span v-if="type === 'video' && course.views">
            <i class="fas fa-eye mr-1"></i>{{ formatNumber(course.views) }}
          </span>
          <span v-if="course.rating">
            <i class="fas fa-star text-yellow-400 mr-1"></i>{{ course.rating }}
          </span>
        </div>
        <span v-if="type === 'ebook' && course.pages" class="text-purple-400">
          {{ course.pages }} trang
        </span>
      </div>

      <!-- Progress Bar -->
      <div v-if="progress > 0" class="mt-4">
        <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-purple-400 to-indigo-400 transition-all"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
        <p class="text-xs text-gray-400 mt-1">Tiến độ: {{ progress }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useEducationStore } from '../../stores/education';

const props = defineProps({
  course: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    default: 'video', // 'video' or 'ebook'
    validator: (value) => ['video', 'ebook'].includes(value)
  }
});

defineEmits(['click']);

const educationStore = useEducationStore();

const progress = computed(() => {
  if (!props.course.id) return 0;
  const progressData = educationStore.progress[props.type];
  if (!progressData || !progressData[props.course.id]) return 0;
  return progressData[props.course.id].progress || 0;
});

const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

const getLevelLabel = (level) => {
  const labels = {
    beginner: 'Cơ bản',
    intermediate: 'Trung bình',
    advanced: 'Nâng cao'
  };
  return labels[level] || level;
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

