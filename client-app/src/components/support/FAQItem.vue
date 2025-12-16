<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl border border-purple-500/20 overflow-hidden">
    <button
      @click="toggle"
      class="w-full p-6 text-left flex items-center justify-between hover:bg-slate-800/50 transition-all"
    >
      <div class="flex-1">
        <h3 class="text-lg font-bold text-white mb-1">{{ faqItem.question }}</h3>
        <div v-if="faqItem.category" class="text-sm text-purple-400">
          {{ getCategoryName(faqItem.category) }}
        </div>
      </div>
      <i
        :class="[
          'fas text-purple-400 transition-transform',
          isOpen ? 'fa-chevron-up' : 'fa-chevron-down'
        ]"
      ></i>
    </button>
    
    <div
      v-if="isOpen"
      class="px-6 pb-6 text-gray-300"
    >
      <div class="prose prose-invert max-w-none" v-html="faqItem.answer"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  faqItem: {
    type: Object,
    required: true
  }
});

const isOpen = ref(false);

const toggle = () => {
  isOpen.value = !isOpen.value;
};

const getCategoryName = (categoryId) => {
  const names = {
    'account': 'Tài Khoản',
    'trading': 'Giao Dịch',
    'deposit': 'Nạp Tiền',
    'withdraw': 'Rút Tiền',
    'technical': 'Kỹ Thuật'
  };
  return names[categoryId] || categoryId;
};
</script>

<style scoped>
/* FAQ item styles */
</style>

