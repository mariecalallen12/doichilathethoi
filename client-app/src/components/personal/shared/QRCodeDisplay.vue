<template>
  <div class="flex flex-col items-center space-y-4">
    <div class="glass-panel rounded-lg p-6">
      <canvas ref="qrCanvas" class="w-48 h-48"></canvas>
    </div>
    <div class="text-center">
      <div class="text-purple-300 text-sm mb-2">Địa chỉ ví</div>
      <div class="flex items-center space-x-2 bg-slate-800/50 rounded-lg px-4 py-2">
        <code class="text-white text-sm font-mono break-all">{{ address }}</code>
        <button
          @click="copyAddress"
          class="ml-2 p-2 text-purple-300 hover:text-white transition-colors"
          :title="copied ? 'Đã sao chép' : 'Sao chép địa chỉ'"
        >
          <i :class="copied ? 'fas fa-check' : 'fas fa-copy'"></i>
        </button>
      </div>
      <div v-if="copied" class="mt-2 text-green-400 text-xs">Đã sao chép vào clipboard!</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  address: {
    type: String,
    required: true,
  },
  size: {
    type: Number,
    default: 192,
  },
});

const qrCanvas = ref(null);
const copied = ref(false);

const generateQRCode = async () => {
  if (!qrCanvas.value || !props.address) return;

  try {
    // Simple QR code generation using canvas
    // For production, use a proper QR code library like qrcode
    const canvas = qrCanvas.value;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = props.size;
    canvas.height = props.size;
    
    // Clear canvas
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw QR code pattern (simplified - in production use a QR library)
    ctx.fillStyle = '#000000';
    const cellSize = props.size / 25;
    
    // Draw a simple pattern (replace with actual QR code generation)
    for (let i = 0; i < 25; i++) {
      for (let j = 0; j < 25; j++) {
        if ((i + j) % 3 === 0 || (i * j) % 7 === 0) {
          ctx.fillRect(i * cellSize, j * cellSize, cellSize, cellSize);
        }
      }
    }
    
    // Note: This is a placeholder. In production, use:
    // import QRCode from 'qrcode';
    // QRCode.toCanvas(canvas, props.address, { width: props.size });
  } catch (error) {
    console.error('Error generating QR code:', error);
  }
};

const copyAddress = async () => {
  try {
    await navigator.clipboard.writeText(props.address);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (error) {
    console.error('Failed to copy address:', error);
  }
};

onMounted(() => {
  generateQRCode();
});

watch(() => props.address, () => {
  generateQRCode();
});
</script>

