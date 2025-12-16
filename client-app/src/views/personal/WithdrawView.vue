<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Rút Tiền</h1>
      <p class="text-purple-300">Rút tiền từ tài khoản của bạn</p>
    </div>

    <!-- Two Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Withdraw Form -->
      <div class="lg:col-span-2">
        <WithdrawForm @success="handleSuccess" />
      </div>

      <!-- Withdraw History -->
      <div class="lg:col-span-1">
        <WithdrawHistory />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import WithdrawForm from '../../components/personal/withdraw/WithdrawForm.vue';
import WithdrawHistory from '../../components/personal/withdraw/WithdrawHistory.vue';

const handleSuccess = (withdrawal) => {
  // Show success message or redirect
  console.log('Withdrawal created:', withdrawal);
};
</script>

