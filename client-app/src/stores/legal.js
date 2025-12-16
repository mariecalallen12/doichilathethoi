import { defineStore } from 'pinia';
import { ref } from 'vue';
import { legalApi } from '../services/api/legal';

export const useLegalStore = defineStore('legal', () => {
  // State
  const terms = ref(null);
  const privacy = ref(null);
  const riskWarning = ref(null);
  const complaints = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // Actions
  async function fetchTerms(version = null) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await legalApi.getTerms(version);
      terms.value = response.data || response;
      return terms.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch terms';
      console.error('Error fetching terms:', err);
      // Fallback
      terms.value = getFallbackTerms();
      return terms.value;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchPrivacy(version = null) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await legalApi.getPrivacy(version);
      privacy.value = response.data || response;
      return privacy.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch privacy policy';
      console.error('Error fetching privacy:', err);
      // Fallback
      privacy.value = getFallbackPrivacy();
      return privacy.value;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchRiskWarning() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await legalApi.getRiskWarning();
      riskWarning.value = response.data || response;
      return riskWarning.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch risk warning';
      console.error('Error fetching risk warning:', err);
      // Fallback
      riskWarning.value = getFallbackRiskWarning();
      return riskWarning.value;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchComplaints() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await legalApi.getComplaints();
      complaints.value = response.data || response;
      return complaints.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch complaints';
      console.error('Error fetching complaints:', err);
      complaints.value = [];
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  async function submitComplaint(complaintData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await legalApi.submitComplaint(complaintData);
      // Refresh complaints list
      await fetchComplaints();
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to submit complaint';
      console.error('Error submitting complaint:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function getComplaintById(complaintId) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await legalApi.getComplaintById(complaintId);
      return response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch complaint';
      console.error('Error fetching complaint:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateComplaint(complaintId, updateData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await legalApi.updateComplaint(complaintId, updateData);
      // Refresh complaints list
      await fetchComplaints();
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to update complaint';
      console.error('Error updating complaint:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // Fallback data
  function getFallbackTerms() {
    return {
      version: '1.0',
      effective_date: new Date().toISOString(),
      content: '<h1>Điều Khoản Sử Dụng</h1><p>Nội dung điều khoản sử dụng...</p>'
    };
  }

  function getFallbackPrivacy() {
    return {
      version: '1.0',
      effective_date: new Date().toISOString(),
      content: '<h1>Chính Sách Bảo Mật</h1><p>Nội dung chính sách bảo mật...</p>'
    };
  }

  function getFallbackRiskWarning() {
    return {
      content: '<h1>Cảnh Báo Rủi Ro</h1><p>Giao dịch CFD và Forex có rủi ro cao...</p>'
    };
  }

  return {
    // State
    terms,
    privacy,
    riskWarning,
    complaints,
    isLoading,
    error,
    // Actions
    fetchTerms,
    fetchPrivacy,
    fetchRiskWarning,
    fetchComplaints,
    submitComplaint,
    getComplaintById,
    updateComplaint
  };
});

