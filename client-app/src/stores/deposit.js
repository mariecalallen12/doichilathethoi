import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { getErrorMessage } from '../services/utils/errorHandler';
import { success as showSuccessToast, error as showErrorToast } from '../services/utils/toast';
import { getApiBaseUrl } from '../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const useDepositStore = defineStore('deposit', () => {
  const deposits = ref([]);
  const currentDeposit = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  async function createDeposit(depositData) {
    isLoading.value = true;
    error.value = null;

    try {
      // Map frontend format to backend format
      const backendData = {
        amount: depositData.amount,
        currency: depositData.currency || { value: depositData.currency || 'usdt' },
        method: depositData.method || { value: depositData.method || 'crypto_deposit' },
        walletAddress: depositData.walletAddress,
        bankAccount: depositData.bankAccount,
        transactionId: depositData.transactionId,
        notes: depositData.notes
      };
      
      const response = await api.post('/financial/deposits', backendData);
      // Handle nested response structure
      if (response.data.data && response.data.data.deposit) {
        currentDeposit.value = response.data.data.deposit;
      } else if (response.data.deposit) {
        currentDeposit.value = response.data.deposit;
      }
      const result = response.data;
      showSuccessToast('Tạo yêu cầu nạp tiền thành công');
      return result;
    } catch (err) {
      const message = getErrorMessage(err);
      error.value = message;
      showErrorToast(message);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchDeposits(filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/financial/deposits', { params: filters });
      deposits.value = response.data.data?.deposits || [];
      return response.data;
    } catch (err) {
      const message = getErrorMessage(err);
      error.value = message;
      showErrorToast(message);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function getDepositById(depositId) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get(`/financial/deposits/${depositId}`);
      currentDeposit.value = response.data.data?.deposit;
      return response.data;
    } catch (err) {
      const message = getErrorMessage(err);
      error.value = message;
      showErrorToast(message);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    deposits,
    currentDeposit,
    isLoading,
    error,
    createDeposit,
    fetchDeposits,
    getDepositById,
  };
});
