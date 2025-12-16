<script setup>
import Card from '../ui/Card.vue';
import Badge from '../ui/Badge.vue';

const props = defineProps({
  activities: {
    type: Array,
    default: () => [
      {
        id: 1,
        type: 'user_registration',
        message: 'Người dùng mới đăng ký',
        user: 'user@example.com',
        time: '2 phút trước',
        icon: 'fa-user-plus',
        color: 'text-green-400',
      },
      {
        id: 2,
        type: 'large_trade',
        message: 'Giao dịch lớn',
        amount: '$50,000',
        time: '5 phút trước',
        icon: 'fa-exchange-alt',
        color: 'text-blue-400',
      },
      {
        id: 3,
        type: 'deposit_approval',
        message: 'Phê duyệt nạp tiền',
        amount: '$10,000',
        time: '10 phút trước',
        icon: 'fa-check-circle',
        color: 'text-green-400',
      },
      {
        id: 4,
        type: 'system_backup',
        message: 'Backup hệ thống',
        time: '15 phút trước',
        icon: 'fa-database',
        color: 'text-purple-primary',
      },
      {
        id: 5,
        type: 'warning',
        message: 'Cảnh báo khối lượng giao dịch cao',
        time: '20 phút trước',
        icon: 'fa-exclamation-triangle',
        color: 'text-yellow-400',
      },
    ],
  },
});
</script>

<template>
  <Card title="Hoạt động gần đây">
    <div class="space-y-3 max-h-96 overflow-y-auto">
      <div
        v-for="activity in activities"
        :key="activity.id"
        class="flex items-start gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all"
      >
        <div
          :class="[
            'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
            activity.color.replace('text-', 'bg-').replace('-400', '-500/20'),
          ]"
        >
          <i :class="[`fas ${activity.icon}`, activity.color, 'text-lg']"></i>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-white text-sm font-medium">{{ activity.message }}</p>
          <div class="flex items-center gap-2 mt-1">
            <span v-if="activity.user" class="text-white/60 text-xs">{{ activity.user }}</span>
            <span v-if="activity.amount" class="text-white/60 text-xs">{{ activity.amount }}</span>
            <span class="text-white/40 text-xs">{{ activity.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </Card>
</template>

