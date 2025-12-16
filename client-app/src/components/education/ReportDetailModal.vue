<template>
  <div
    v-if="report"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
    @click.self="close"
  >
    <div class="relative w-full max-w-4xl mx-4 bg-slate-900 rounded-xl overflow-hidden border border-purple-500/20 flex flex-col" style="height: 90vh;">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-purple-500/20">
        <div>
          <h3 class="text-xl font-bold text-white">{{ report.title }}</h3>
          <p class="text-sm text-gray-400">{{ formatDate(report.date) }}</p>
        </div>
        <div class="flex items-center space-x-4">
          <button
            @click="downloadReport"
            class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all"
          >
            <i class="fas fa-download mr-2"></i>Tải xuống PDF
          </button>
          <button
            @click="close"
            class="w-10 h-10 bg-slate-800 hover:bg-slate-700 rounded-full flex items-center justify-center text-white transition-all"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-auto p-6">
        <div class="prose prose-invert max-w-none">
          <p class="text-gray-300 mb-6">{{ report.description }}</p>
          
          <!-- PDF Preview -->
          <div v-if="report.fileUrl" class="mt-6">
            <iframe
              :src="pdfUrl"
              class="w-full border-0 rounded-lg"
              style="min-height: 600px;"
            ></iframe>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};

const pdfUrl = computed(() => {
  if (props.report.fileUrl) {
    return `https://mozilla.github.io/pdf.js/web/viewer.html?file=${encodeURIComponent(props.report.fileUrl)}`;
  }
  return null;
});

const downloadReport = () => {
  if (props.report.fileUrl) {
    const link = document.createElement('a');
    link.href = props.report.fileUrl;
    link.download = `${props.report.title}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};
</script>

<style scoped>
/* Report detail modal styles */
</style>

