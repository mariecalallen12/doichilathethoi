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
      v-if="ebook"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
      @click.self="close"
    >
      <div class="relative w-full max-w-6xl mx-4 bg-slate-900 rounded-xl overflow-hidden border border-purple-500/20 flex flex-col shadow-2xl" style="height: 90vh;">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-purple-500/20 bg-slate-800/50">
          <div class="flex-1 min-w-0">
            <h3 class="text-xl font-bold text-white truncate">{{ ebook.title }}</h3>
            <div class="flex items-center space-x-4 mt-1 text-sm text-gray-400">
              <span v-if="ebook.pages">
                <i class="fas fa-file-pdf mr-1 text-red-400"></i>{{ ebook.pages }} trang
              </span>
              <span v-if="ebook.size">
                <i class="fas fa-hdd mr-1"></i>{{ formatFileSize(ebook.size) }}
              </span>
            </div>
          </div>
          <div class="flex items-center space-x-2 ml-4">
            <button
              @click="downloadEbook"
              class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all flex items-center space-x-2"
              aria-label="Tải xuống ebook"
            >
              <i class="fas fa-download"></i>
              <span class="hidden sm:inline">Tải xuống</span>
            </button>
            <button
              @click="close"
              class="w-10 h-10 bg-slate-800 hover:bg-slate-700 rounded-full flex items-center justify-center text-white transition-all hover:scale-110"
              aria-label="Đóng ebook"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <!-- PDF Viewer -->
        <div class="flex-1 overflow-hidden relative">
          <!-- Loading State -->
          <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-slate-800">
            <div class="text-center">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400 mb-4"></div>
              <p class="text-purple-200">Đang tải ebook...</p>
              <p class="text-gray-400 text-sm mt-2">{{ loadingProgress }}%</p>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="absolute inset-0 flex items-center justify-center bg-slate-800">
            <div class="text-center max-w-md px-4">
              <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
              <p class="text-red-400 mb-4">{{ error }}</p>
              <div class="flex flex-col sm:flex-row gap-2 justify-center">
                <button
                  @click="retryLoad"
                  class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all"
                >
                  <i class="fas fa-redo mr-2"></i>Thử lại
                </button>
                <button
                  @click="downloadEbook"
                  class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-all"
                >
                  <i class="fas fa-download mr-2"></i>Tải xuống
                </button>
              </div>
            </div>
          </div>

          <!-- PDF Container -->
          <div v-else class="h-full overflow-auto">
            <div ref="pdfContainer" class="pdf-container p-4">
              <canvas
                v-for="(page, index) in pdfPages"
                :key="index"
                :ref="el => { if (el) canvasRefs[index] = el }"
                class="pdf-page mb-4 mx-auto shadow-lg"
              ></canvas>
            </div>
          </div>

          <!-- Page Navigation -->
          <div v-if="!loading && !error && totalPages > 0" class="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/70 rounded-lg px-4 py-2 flex items-center space-x-4">
            <button
              @click="previousPage"
              :disabled="currentPage <= 1"
              class="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-all"
              aria-label="Trang trước"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="text-white text-sm">
              Trang {{ currentPage }} / {{ totalPages }}
            </span>
            <button
              @click="nextPage"
              :disabled="currentPage >= totalPages"
              class="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-all"
              aria-label="Trang sau"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t border-purple-500/20 flex flex-col sm:flex-row items-center justify-between bg-slate-800/50">
          <div class="flex items-center space-x-4 text-sm text-gray-400 mb-2 sm:mb-0">
            <span v-if="ebook.downloadCount" class="flex items-center">
              <i class="fas fa-download mr-1 text-purple-400"></i>{{ formatNumber(ebook.downloadCount) }} lượt tải
            </span>
            <span v-if="ebook.rating" class="flex items-center">
              <i class="fas fa-star text-yellow-400 mr-1"></i>{{ ebook.rating }}
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-400">Tiến độ:</span>
            <div class="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-purple-400 to-indigo-400 transition-all"
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
            <span class="text-sm text-purple-400 font-semibold">{{ progress }}%</span>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useEducationStore } from '../../stores/education';
import * as pdfjsLib from 'pdfjs-dist';

// Set worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

const props = defineProps({
  ebook: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const educationStore = useEducationStore();
const loading = ref(true);
const error = ref(null);
const progress = ref(0);
const loadingProgress = ref(0);
const pdfContainer = ref(null);
const canvasRefs = ref([]);
const pdfDoc = ref(null);
const totalPages = ref(0);
const currentPage = ref(1);
const pdfPages = ref([]);
const scale = ref(1.5);

const loadPDF = async () => {
  if (!props.ebook.fileUrl && !props.ebook.url) {
    error.value = 'Không tìm thấy file PDF';
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;
    loadingProgress.value = 0;

    const url = props.ebook.fileUrl || props.ebook.url;
    const loadingTask = pdfjsLib.getDocument({
      url: url,
      withCredentials: false
    });

    loadingTask.onProgress = (progressData) => {
      if (progressData.total > 0) {
        loadingProgress.value = Math.round((progressData.loaded / progressData.total) * 100);
      }
    };

    pdfDoc.value = await loadingTask.promise;
    totalPages.value = pdfDoc.value.numPages;
    pdfPages.value = Array.from({ length: totalPages.value }, (_, i) => i + 1);

    // Load progress if exists
    const progressData = educationStore.progress.ebook?.[props.ebook.id];
    if (progressData) {
      progress.value = progressData.progress || 0;
      currentPage.value = Math.max(1, Math.min(totalPages.value, Math.round((progress.value / 100) * totalPages.value)));
    }

    await nextTick();
    await renderPages();

    loading.value = false;
  } catch (err) {
    console.error('Error loading PDF:', err);
    error.value = 'Không thể tải file PDF. Vui lòng kiểm tra kết nối mạng hoặc tải xuống để đọc.';
    loading.value = false;
  }
};

const renderPages = async () => {
  if (!pdfDoc.value) return;

  const startPage = Math.max(1, currentPage.value - 1);
  const endPage = Math.min(totalPages.value, currentPage.value + 1);

  for (let pageNum = startPage; pageNum <= endPage; pageNum++) {
    try {
      const page = await pdfDoc.value.getPage(pageNum);
      const viewport = page.getViewport({ scale: scale.value });
      
      const canvas = canvasRefs.value[pageNum - 1];
      if (!canvas) continue;

      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      const renderContext = {
        canvasContext: context,
        viewport: viewport
      };

      await page.render(renderContext).promise;

      // Update progress based on pages read
      const pageProgress = Math.round((pageNum / totalPages.value) * 100);
      if (pageNum === currentPage.value) {
        progress.value = pageProgress;
      }
    } catch (err) {
      console.error(`Error rendering page ${pageNum}:`, err);
    }
  }
};

const nextPage = async () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    await renderPages();
    updateProgress();
    pdfContainer.value?.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const previousPage = async () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    await renderPages();
    updateProgress();
    pdfContainer.value?.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const updateProgress = () => {
  const pageProgress = Math.round((currentPage.value / totalPages.value) * 100);
  progress.value = pageProgress;
};

const retryLoad = () => {
  loadPDF();
};

const close = async () => {
  // Save progress when closing
  if (props.ebook.id && progress.value > 0) {
    try {
      await educationStore.updateProgress(props.ebook.id, 'ebook', {
        progress: progress.value,
        current_page: currentPage.value,
        last_opened: new Date().toISOString()
      });
    } catch (err) {
      console.error('Error saving progress:', err);
    }
  }
  emit('close');
};

const downloadEbook = () => {
  const url = props.ebook.fileUrl || props.ebook.url;
  if (url) {
    const link = document.createElement('a');
    link.href = url;
    link.download = `${props.ebook.title || 'ebook'}.pdf`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
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

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

// Handle ESC key
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    close();
  } else if (event.key === 'ArrowRight' && !loading.value && !error.value) {
    nextPage();
  } else if (event.key === 'ArrowLeft' && !loading.value && !error.value) {
    previousPage();
  }
};

watch(() => props.ebook, () => {
  if (props.ebook) {
    loadPDF();
  }
}, { immediate: true });

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
  document.body.style.overflow = 'hidden';
  loadPDF();
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
  document.body.style.overflow = '';
});
</script>

<style scoped>
.pdf-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f5f5f5;
}

.pdf-page {
  display: block;
  max-width: 100%;
  height: auto;
  background: white;
  border: 1px solid #ddd;
}

@media (max-width: 768px) {
  .pdf-page {
    width: 100%;
  }
}
</style>

