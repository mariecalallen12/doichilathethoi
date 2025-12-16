<script setup>
defineProps({
  headers: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['page-change', 'sort']);
</script>

<template>
  <div class="w-full overflow-x-auto">
    <table class="w-full">
      <thead>
        <tr class="border-b border-white/10">
          <th
            v-for="header in headers"
            :key="header.key"
            :class="[
              'px-4 py-3 text-left text-sm font-semibold text-white/80',
              header.sortable && 'cursor-pointer hover:text-white',
            ]"
            @click="header.sortable && emit('sort', header.key)"
          >
            <div class="flex items-center gap-2">
              {{ header.label }}
              <i
                v-if="header.sortable"
                class="fas fa-sort text-white/40 text-xs"
              ></i>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading" class="border-b border-white/5">
          <td :colspan="headers.length" class="px-4 py-8 text-center">
            <div class="flex items-center justify-center">
              <i class="fas fa-spinner fa-spin text-primary text-2xl"></i>
            </div>
          </td>
        </tr>
        <tr
          v-else-if="data.length === 0"
          class="border-b border-white/5"
        >
          <td :colspan="headers.length" class="px-4 py-8 text-center text-white/60">
            Không có dữ liệu
          </td>
        </tr>
        <slot v-else :data="data" />
      </tbody>
    </table>

    <!-- Pagination -->
    <div
      v-if="pagination && pagination.total > pagination.limit"
      class="flex items-center justify-between mt-4 px-4"
    >
      <div class="text-sm text-white/60">
        Hiển thị {{ (pagination.page - 1) * pagination.limit + 1 }} -
        {{ Math.min(pagination.page * pagination.limit, pagination.total) }}
        trong tổng số {{ pagination.total }}
      </div>
      <div class="flex items-center gap-2">
        <button
          :disabled="pagination.page === 1"
          :class="[
            'px-3 py-1.5 rounded-lg bg-white/10 text-white border border-white/20',
            'hover:bg-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed',
          ]"
          @click="emit('page-change', pagination.page - 1)"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        <span class="px-4 py-1.5 text-white">
          Trang {{ pagination.page }} / {{ Math.ceil(pagination.total / pagination.limit) }}
        </span>
        <button
          :disabled="pagination.page >= Math.ceil(pagination.total / pagination.limit)"
          :class="[
            'px-3 py-1.5 rounded-lg bg-white/10 text-white border border-white/20',
            'hover:bg-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed',
          ]"
          @click="emit('page-change', pagination.page + 1)"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

