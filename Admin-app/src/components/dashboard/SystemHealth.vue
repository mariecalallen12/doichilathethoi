<script setup>
import Card from '../ui/Card.vue';
import Badge from '../ui/Badge.vue';

const props = defineProps({
  services: {
    type: Array,
    default: () => [
      { name: 'Database', status: 'operational', icon: 'fa-database' },
      { name: 'API Services', status: 'active', icon: 'fa-server' },
      { name: 'Trading Engine', status: 'high-load', icon: 'fa-cogs' },
    ],
  },
});

const getStatusType = (status) => {
  const statusMap = {
    operational: 'success',
    active: 'success',
    'high-load': 'warning',
    error: 'error',
    down: 'error',
  };
  return statusMap[status] || 'default';
};

const getStatusText = (status) => {
  const textMap = {
    operational: 'Operational',
    active: 'All Active',
    'high-load': 'High Load',
    error: 'Error',
    down: 'Down',
  };
  return textMap[status] || status;
};
</script>

<template>
  <Card title="Tình trạng dịch vụ">
    <div class="space-y-3">
      <div
        v-for="service in services"
        :key="service.name"
        class="flex items-center justify-between p-3 bg-white/5 rounded-lg"
      >
        <div class="flex items-center gap-3">
          <i :class="[`fas ${service.icon}`, 'text-primary text-lg']"></i>
          <span class="text-white font-medium">{{ service.name }}</span>
        </div>
        <Badge :type="getStatusType(service.status)">
          {{ getStatusText(service.status) }}
        </Badge>
      </div>
    </div>
  </Card>
</template>

