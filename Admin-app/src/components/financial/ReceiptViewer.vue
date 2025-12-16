<script setup>
import Modal from '../ui/Modal.vue';

const props = defineProps({
  show: Boolean,
  receiptUrl: String,
});

const emit = defineEmits(['close', 'update:show']);
</script>

<template>
  <Modal
    :show="show"
    title="Xem hóa đơn/biên lai"
    size="lg"
    @update:show="emit('update:show', $event)"
    @close="emit('close')"
  >
    <div v-if="receiptUrl" class="flex items-center justify-center">
      <img :src="receiptUrl" alt="Receipt" class="max-w-full max-h-96 rounded-lg" />
    </div>
    <div v-else class="text-center py-8 text-white/60">
      Không có hình ảnh hóa đơn
    </div>
  </Modal>
</template>

