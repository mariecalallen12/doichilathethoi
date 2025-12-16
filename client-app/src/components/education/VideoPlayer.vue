<template>
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="video"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
      @click.self="close"
    >
      <div class="relative w-full max-w-6xl mx-4 bg-slate-900 rounded-xl overflow-hidden border border-purple-500/20 shadow-2xl">
        <!-- Close Button -->
        <button
          @click="close"
          class="absolute top-4 right-4 z-10 w-10 h-10 bg-black/70 hover:bg-black/90 rounded-full flex items-center justify-center text-white transition-all hover:scale-110"
          aria-label="Đóng video"
        >
          <i class="fas fa-times"></i>
        </button>

        <!-- Loading State -->
        <div v-if="loading" class="relative w-full" style="padding-top: 56.25%">
          <div class="absolute inset-0 flex items-center justify-center bg-slate-800">
            <div class="text-center">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400 mb-4"></div>
              <p class="text-purple-200">Đang tải video...</p>
            </div>
          </div>
        </div>

        <!-- Video Container with Plyr -->
        <div v-else class="relative w-full" style="padding-top: 56.25%">
          <video
            ref="videoElement"
            :src="video.videoUrl || video.url"
            class="absolute top-0 left-0 w-full h-full"
            @ended="handleVideoEnded"
            @loadedmetadata="handleVideoLoaded"
            @error="handleVideoError"
          ></video>
        </div>

        <!-- Video Info -->
        <div class="p-6">
          <h3 class="text-2xl font-bold text-white mb-2">{{ video.title }}</h3>
          <p class="text-gray-400 mb-4">{{ video.description }}</p>
          
          <!-- Video Meta -->
          <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500">
            <span v-if="video.views" class="flex items-center">
              <i class="fas fa-eye mr-1 text-purple-400"></i>{{ formatNumber(video.views) }} lượt xem
            </span>
            <span v-if="video.rating" class="flex items-center">
              <i class="fas fa-star text-yellow-400 mr-1"></i>{{ video.rating }}
            </span>
            <span v-if="video.duration" class="flex items-center">
              <i class="fas fa-clock mr-1 text-purple-400"></i>{{ formatDuration(video.duration) }}
            </span>
            <span v-if="video.category" class="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
              {{ video.category }}
            </span>
          </div>

          <!-- Progress Indicator -->
          <div v-if="videoProgress > 0" class="mt-4">
            <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-purple-400 to-indigo-400 transition-all"
                :style="{ width: `${videoProgress}%` }"
              ></div>
            </div>
            <p class="text-xs text-gray-400 mt-1">Tiến độ: {{ videoProgress }}%</p>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useEducationStore } from '../../stores/education';
import Plyr from 'plyr';
import 'plyr/dist/plyr.css';

const props = defineProps({
  video: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const educationStore = useEducationStore();
const videoElement = ref(null);
const player = ref(null);
const loading = ref(true);
const videoProgress = ref(0);
const error = ref(null);

const initPlayer = () => {
  if (videoElement.value && !player.value) {
    player.value = new Plyr(videoElement.value, {
      controls: [
        'play-large',
        'restart',
        'rewind',
        'play',
        'fast-forward',
        'progress',
        'current-time',
        'duration',
        'mute',
        'volume',
        'settings',
        'pip',
        'airplay',
        'fullscreen'
      ],
      settings: ['captions', 'quality', 'speed'],
      keyboard: { focused: true, global: false },
      tooltips: { controls: true, seek: true },
      ratio: '16:9'
    });

    // Restore progress if exists
    const progressData = educationStore.progress.video?.[props.video.id];
    if (progressData && progressData.current_time) {
      player.value.currentTime = progressData.current_time;
      videoProgress.value = progressData.progress || 0;
    }

    // Track progress
    player.value.on('timeupdate', () => {
      if (player.value.duration > 0) {
        const progress = Math.round((player.value.currentTime / player.value.duration) * 100);
        videoProgress.value = progress;
      }
    });

    player.value.on('ready', () => {
      loading.value = false;
    });

    player.value.on('error', (e) => {
      console.error('Plyr error:', e);
      error.value = 'Không thể tải video. Vui lòng thử lại sau.';
      loading.value = false;
    });
  }
};

const handleVideoLoaded = () => {
  loading.value = false;
  if (!player.value) {
    initPlayer();
  }
};

const handleVideoError = () => {
  loading.value = false;
  error.value = 'Không thể tải video. Vui lòng kiểm tra kết nối mạng.';
};

const close = () => {
  // Save progress when closing
  if (player.value && props.video.id) {
    const currentTime = player.value.currentTime;
    const duration = player.value.duration;
    const progress = duration > 0 ? Math.round((currentTime / duration) * 100) : 0;
    
    educationStore.updateProgress(props.video.id, 'video', {
      progress,
      current_time: currentTime,
      last_watched: new Date().toISOString()
    }).catch(err => {
      console.error('Error saving progress:', err);
    });

    // Destroy player
    if (player.value) {
      player.value.destroy();
      player.value = null;
    }
  }
  emit('close');
};

const handleVideoEnded = async () => {
  if (props.video.id) {
    try {
      await educationStore.updateProgress(props.video.id, 'video', {
        progress: 100,
        status: 'completed',
        completed_at: new Date().toISOString()
      });
      videoProgress.value = 100;
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  }
};

const formatDuration = (seconds) => {
  if (!seconds) return '0:00';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

// Handle ESC key
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    close();
  }
};

watch(() => props.video, () => {
  if (props.video && videoElement.value) {
    loading.value = true;
    error.value = null;
    if (player.value) {
      player.value.destroy();
      player.value = null;
    }
    setTimeout(() => {
      initPlayer();
    }, 100);
  }
}, { immediate: true });

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
  document.body.style.overflow = 'hidden';
  if (videoElement.value) {
    initPlayer();
  }
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
  document.body.style.overflow = '';
  if (player.value) {
    player.value.destroy();
    player.value = null;
  }
});
</script>

<style scoped>
/* Plyr custom styles */
:deep(.plyr) {
  border-radius: 0;
}

:deep(.plyr__video-wrapper) {
  background: #000;
}

:deep(.plyr__control--overlaid) {
  background: rgba(139, 92, 246, 0.8);
}

:deep(.plyr__control--overlaid:hover) {
  background: rgba(139, 92, 246, 1);
}
</style>

