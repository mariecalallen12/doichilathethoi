<template>
  <div class="glass-panel rounded-lg p-1">
    <div class="flex space-x-1">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="$emit('change-tab', tab.id)"
        :class="[
          'flex-1 px-4 py-3 rounded-lg font-medium transition-all',
          activeTab === tab.id
            ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white'
            : 'text-purple-300 hover:text-white hover:bg-purple-500/10'
        ]"
      >
        <i :class="[tab.icon, 'mr-2']"></i>
        {{ tab.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  activeTab: {
    type: String,
    required: true,
  },
});

defineEmits(['change-tab']);

const tabs = [
  {
    id: 'deposits',
    label: 'Nạp/Rút',
    icon: 'fas fa-exchange-alt',
  },
  {
    id: 'orders',
    label: 'Đặt Lệnh',
    icon: 'fas fa-list',
  },
];
</script>

