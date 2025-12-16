import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
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

export const useProfileStore = defineStore('profile', () => {
  const profile = ref({
    fullName: '',
    phone: '',
    email: '',
    dateOfBirth: '',
    nationality: '',
    address: '',
    profilePicture: null,
  });

  const bankAccounts = ref([]);
  const trustedDevices = ref([]);
  const auditTrail = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchProfile() {
    isLoading.value = true;
    error.value = null;

    try {
      // Get client profile
      const response = await api.get('/client/profile');
      
      // Handle nested response structure
      const data = response.data.data || response.data;
      
      if (data.profile) {
        profile.value = {
          fullName: data.profile.display_name || data.profile.full_name || '',
          phone: data.profile.phone_number || '',
          email: data.profile.email || '',
          dateOfBirth: data.profile.date_of_birth || '',
          nationality: data.profile.nationality || '',
          address: data.profile.address || '',
          profilePicture: data.profile.avatar_url || null,
        };
      } else if (data.display_name || data.email) {
        // Direct profile object
        profile.value = {
          fullName: data.display_name || data.full_name || '',
          phone: data.phone_number || '',
          email: data.email || '',
          dateOfBirth: data.date_of_birth || '',
          nationality: data.nationality || '',
          address: data.address || '',
          profilePicture: data.avatar_url || null,
        };
      }
      
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch profile';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateProfile(profileData) {
    isLoading.value = true;
    error.value = null;

    try {
      // Map frontend format to backend format
      const backendData = {
        display_name: profileData.fullName,
        phone_number: profileData.phone,
        date_of_birth: profileData.dateOfBirth,
        nationality: profileData.nationality,
        address: profileData.address,
      };
      
      // Update client profile
      const response = await api.put('/client/profile', backendData);
      
      // Update local profile
      const data = response.data.data || response.data;
      if (data.profile || data.display_name) {
        await fetchProfile(); // Refresh profile
      }
      
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to update profile';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchBankAccounts() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/users/bank-accounts');
      bankAccounts.value = response.data.data?.bankAccounts || [];
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch bank accounts';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function addBankAccount(accountData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/bank-accounts', accountData);
      bankAccounts.value.push(response.data.data?.bankAccount);
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to add bank account';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTrustedDevices() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/users/trusted-devices');
      trustedDevices.value = response.data.data?.devices || [];
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch trusted devices';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchAuditTrail() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/users/audit-trail');
      auditTrail.value = response.data.data?.auditTrail || [];
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch audit trail';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    profile,
    bankAccounts,
    trustedDevices,
    auditTrail,
    isLoading,
    error,
    fetchProfile,
    updateProfile,
    fetchBankAccounts,
    addBankAccount,
    fetchTrustedDevices,
    fetchAuditTrail,
  };
});

