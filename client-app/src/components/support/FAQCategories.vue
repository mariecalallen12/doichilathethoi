<template>
  <div class="mb-6 flex flex-wrap gap-2">
    <button
      v-for="category in categories"
      :key="category.id"
      @click="selectCategory(category.id)"
      class="px-4 py-2 rounded-lg transition-all"
      :class="{
        'bg-purple-600 text-white': selectedCategory === category.id,
        'bg-slate-800/50 text-gray-300 hover:bg-slate-700': selectedCategory !== category.id
      }"
    >
      {{ category.name }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useSupportStore } from '../../stores/support';

const emit = defineEmits(['category-selected']);

const supportStore = useSupportStore();
const selectedCategory = ref('all');
const categories = ref([
  { id: 'all', name: 'Tất cả' },
  { id: 'account', name: 'Tài Khoản' },
  { id: 'trading', name: 'Giao Dịch' },
  { id: 'deposit', name: 'Nạp Tiền' },
  { id: 'withdraw', name: 'Rút Tiền' },
  { id: 'technical', name: 'Kỹ Thuật' }
]);

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId;
  emit('category-selected', categoryId);
};

watch(() => supportStore.categories, (newCategories) => {
  if (newCategories && newCategories.length > 0) {
    categories.value = [
      { id: 'all', name: 'Tất cả' },
      ...newCategories
    ];
  }
}, { immediate: true });

onMounted(() => {
  supportStore.fetchCategories();
});
</script>

<style scoped>
/* FAQ categories styles */
</style>

