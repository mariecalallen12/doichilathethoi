<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6">Yêu Cầu Rút Tiền</h3>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Method Selection -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Phương thức rút</label>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            type="button"
            @click="method = 'crypto'"
            :class="[
              'p-4 rounded-lg border-2 transition-all text-left',
              method === 'crypto'
                ? 'border-purple-500 bg-purple-500/20'
                : 'border-purple-500/30 bg-slate-800/50 hover:border-purple-500/50'
            ]"
          >
            <i class="fab fa-bitcoin text-xl mb-2"></i>
            <div class="text-white font-medium">Ví Crypto</div>
            <div class="text-purple-300 text-xs">USDT, BTC, ETH</div>
          </button>
          <button
            type="button"
            @click="method = 'bank'"
            :class="[
              'p-4 rounded-lg border-2 transition-all text-left',
              method === 'bank'
                ? 'border-purple-500 bg-purple-500/20'
                : 'border-purple-500/30 bg-slate-800/50 hover:border-purple-500/50'
            ]"
          >
            <i class="fas fa-university text-xl mb-2"></i>
            <div class="text-white font-medium">Tài khoản ngân hàng</div>
            <div class="text-purple-300 text-xs">Tất cả ngân hàng VN</div>
          </button>
        </div>
      </div>

      <!-- Crypto Withdrawal -->
      <div v-if="method === 'crypto'" class="space-y-4">
        <div>
          <label class="text-purple-300 text-sm mb-2 block">Loại tiền tệ</label>
          <select
            v-model="currency"
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="USDT">USDT</option>
            <option value="BTC">BTC</option>
            <option value="ETH">ETH</option>
          </select>
        </div>

        <div v-if="currency === 'USDT'">
          <label class="text-purple-300 text-sm mb-2 block">Network</label>
          <select
            v-model="network"
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="ERC20">ERC20</option>
            <option value="TRC20">TRC20</option>
            <option value="BEP20">BEP20</option>
          </select>
        </div>

        <div>
          <label class="text-purple-300 text-sm mb-2 block">Địa chỉ ví</label>
          <input
            v-model="walletAddress"
            type="text"
            placeholder="Nhập địa chỉ ví"
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
          />
        </div>
      </div>

      <!-- Bank Withdrawal -->
      <div v-if="method === 'bank'" class="space-y-4">
        <div>
          <label class="text-purple-300 text-sm mb-2 block">Tài khoản ngân hàng</label>
          <select
            v-model="selectedBankAccount"
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="">Chọn tài khoản</option>
            <option v-for="account in bankAccounts" :key="account.id" :value="account.id">
              {{ account.bankName }} - ****{{ account.accountNumber.slice(-4) }}
            </option>
          </select>
        </div>
      </div>

      <!-- Amount -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Số tiền</label>
        <input
          v-model.number="amount"
          type="number"
          :min="minAmount"
          :max="maxAmount"
          :step="method === 'bank' ? 1000 : 0.00000001"
          placeholder="Nhập số tiền muốn rút"
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
        />
        <div class="text-purple-300 text-xs mt-1">
          Số tiền tối thiểu: {{ formatAmount(minAmount) }}
          <span v-if="maxAmount"> • Tối đa: {{ formatAmount(maxAmount) }}</span>
        </div>
      </div>

      <!-- Fee Calculator -->
      <FeeCalculator :amount="amount" :method="method" />

      <!-- Notes -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Ghi chú (tùy chọn)</label>
        <textarea
          v-model="notes"
          rows="3"
          placeholder="Thêm ghi chú cho yêu cầu rút tiền"
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
        ></textarea>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="!isFormValid || isLoading"
        class="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isLoading">
          <i class="fas fa-spinner fa-spin mr-2"></i>Đang xử lý...
        </span>
        <span v-else>Gửi Yêu Cầu Rút Tiền</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useWithdrawStore } from '../../../stores/withdraw';
import { useAccountStore } from '../../../stores/account';
import { useProfileStore } from '../../../stores/profile';
import FeeCalculator from './FeeCalculator.vue';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const emit = defineEmits(['success']);

const withdrawStore = useWithdrawStore();
const accountStore = useAccountStore();
const profileStore = useProfileStore();

const method = ref('crypto');
const currency = ref('USDT');
const network = ref('ERC20');
const walletAddress = ref('');
const selectedBankAccount = ref('');
const amount = ref(null);
const notes = ref('');
const isLoading = ref(false);
const twoFactorCode = ref('');

const bankAccounts = ref([
  {
    id: '1',
    bankName: 'Vietcombank',
    accountNumber: '1234567890',
    accountHolder: 'Nguyễn Minh Anh',
  },
]);

const minAmount = computed(() => {
  if (method.value === 'bank') return 500000; // 500,000 VND
  if (currency.value === 'BTC') return 30;
  if (currency.value === 'ETH') return 25;
  return 20; // USDT
});

const maxAmount = computed(() => {
  return accountStore.balance?.available || 0;
});

const isFormValid = computed(() => {
  if (!amount.value || amount.value < minAmount.value) return false;
  if (method.value === 'crypto' && !walletAddress.value) return false;
  if (method.value === 'bank' && !selectedBankAccount.value) return false;
  // Nếu tài khoản đã bật 2FA trên backend, yêu cầu mã 2FA
  if (profileStore.profile?.twoFactorEnabled && !twoFactorCode.value.trim()) return false;
  return true;
});

const formatAmount = (amt) => {
  if (method.value === 'bank') {
    return `${formatNumber(amt)} ₫`;
  }
  return formatCurrency(amt, currency.value);
};

const handleSubmit = async () => {
  if (!isFormValid.value) return;

  isLoading.value = true;
  try {
    const withdrawalData = {
      amount: amount.value,
      currency: method.value === 'bank' ? 'VND' : currency.value,
      method: method.value === 'crypto' ? 'crypto_withdrawal' : 'bank_withdrawal',
      walletAddress: method.value === 'crypto' ? walletAddress.value : null,
      bankAccountId: method.value === 'bank' ? selectedBankAccount.value : null,
      network: method.value === 'crypto' && currency.value === 'USDT' ? network.value : null,
      notes: notes.value,
      twoFactorCode: twoFactorCode.value || null,
    };

    await withdrawStore.createWithdrawal(withdrawalData);
    emit('success', withdrawStore.currentWithdrawal);
    
    // Reset form
    amount.value = null;
    walletAddress.value = '';
    selectedBankAccount.value = '';
    notes.value = '';
    twoFactorCode.value = '';
  } catch (error) {
    console.error('Failed to create withdrawal:', error);
  } finally {
    isLoading.value = false;
  }
};
</script>
