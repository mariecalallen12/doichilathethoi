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
import { ref, onMounted } from 'vue';
import { useSupportStore } from '../../stores/support';

const emit = defineEmits(['category-selected']);

const supportStore = useSupportStore();
const selectedCategory = ref('all');
const categories = ref([
  { id: 'all', name: 'Tất cả' },
  ...supportStore.categories
]);

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId;
  emit('category-selected', categoryId);
};

onMounted(() => {
  supportStore.fetchCategories();
  watch(() => supportStore.categories, (newCategories) => {
    categories.value = [
      { id: 'all', name: 'Tất cả' },
      ...newCategories
    ];
  });
});
</script>

<script>
import { watch } from 'vue';
</script>

<style scoped>
/* Category filter styles */
</style>

