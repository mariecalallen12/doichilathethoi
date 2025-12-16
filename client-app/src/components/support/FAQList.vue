<template>
  <div class="space-y-4">
    <FAQItem
      v-for="item in faqItems"
      :key="item.id"
      :faq-item="item"
    />

    <div v-if="faqItems.length === 0" class="text-center py-12 text-gray-400">
      Không tìm thấy câu hỏi nào
    </div>
  </div>
</template>

<script setup>
import FAQItem from './FAQItem.vue';

defineProps({
  faqItems: {
    type: Array,
    default: () => []
  }
});
</script>

<style scoped>
/* FAQ list styles */
</style>

