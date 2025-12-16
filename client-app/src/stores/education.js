import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { educationApi } from '../services/api/education';

export const useEducationStore = defineStore('education', () => {
  // State
  const videos = ref([]);
  const ebooks = ref([]);
  const calendar = ref([]);
  const reports = ref([]);
  const progress = ref({});
  const isLoading = ref(false);
  const error = ref(null);

  // Selected items
  const selectedVideo = ref(null);
  const selectedEbook = ref(null);
  const selectedReport = ref(null);

  // Filters
  const videoCategory = ref('all');
  const ebookCategory = ref('all');
  const reportCategory = ref('all');
  const searchQuery = ref('');

  // Computed
  const filteredVideos = computed(() => {
    let result = videos.value;

    if (videoCategory.value !== 'all') {
      result = result.filter(v => v.category === videoCategory.value);
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(v => 
        v.title.toLowerCase().includes(query) ||
        v.description.toLowerCase().includes(query)
      );
    }

    return result;
  });

  const filteredEbooks = computed(() => {
    let result = ebooks.value;

    if (ebookCategory.value !== 'all') {
      result = result.filter(e => e.category === ebookCategory.value);
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(e => 
        e.title.toLowerCase().includes(query) ||
        e.description.toLowerCase().includes(query)
      );
    }

    return result;
  });

  const filteredReports = computed(() => {
    let result = reports.value;

    if (reportCategory.value !== 'all') {
      result = result.filter(r => r.category === reportCategory.value);
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(r => 
        r.title.toLowerCase().includes(query) ||
        r.description.toLowerCase().includes(query)
      );
    }

    return result;
  });

  // Actions
  async function fetchVideos() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await educationApi.getVideos();
      videos.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch videos';
      console.error('Error fetching videos:', err);
      // Fallback data
      videos.value = getFallbackVideos();
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchVideoById(id) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await educationApi.getVideoById(id);
      selectedVideo.value = response.data || response;
      return selectedVideo.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch video';
      console.error('Error fetching video:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchEbooks() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await educationApi.getEbooks();
      ebooks.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch ebooks';
      console.error('Error fetching ebooks:', err);
      // Fallback data
      ebooks.value = getFallbackEbooks();
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchEbookById(id) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await educationApi.getEbookById(id);
      selectedEbook.value = response.data || response;
      return selectedEbook.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch ebook';
      console.error('Error fetching ebook:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCalendar(startDate, endDate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await educationApi.getCalendar(startDate, endDate);
      calendar.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch calendar';
      console.error('Error fetching calendar:', err);
      // Fallback data
      calendar.value = getFallbackCalendar();
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchReports() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await educationApi.getReports();
      reports.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch reports';
      console.error('Error fetching reports:', err);
      // Fallback data
      reports.value = getFallbackReports();
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchReportById(id) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await educationApi.getReportById(id);
      selectedReport.value = response.data || response;
      return selectedReport.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch report';
      console.error('Error fetching report:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateProgress(itemId, itemType, progressData) {
    try {
      const response = await educationApi.updateProgress(itemId, itemType, progressData);
      if (!progress.value[itemType]) {
        progress.value[itemType] = {};
      }
      progress.value[itemType][itemId] = response.data || response;
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to update progress';
      console.error('Error updating progress:', err);
      throw err;
    }
  }

  function setVideoCategory(category) {
    videoCategory.value = category;
  }

  function setEbookCategory(category) {
    ebookCategory.value = category;
  }

  function setReportCategory(category) {
    reportCategory.value = category;
  }

  function setSearchQuery(query) {
    searchQuery.value = query;
  }

  // Fallback data
  function getFallbackVideos() {
    return [
      {
        id: '1',
        title: 'Forex Trading Basics',
        description: 'Learn the fundamentals of forex trading',
        category: 'forex',
        duration: 1200,
        thumbnail: '/assets/images/edu-video.jpg',
        videoUrl: 'https://example.com/video1.mp4',
        level: 'beginner',
        views: 1250,
        rating: 4.5
      },
      {
        id: '2',
        title: 'Technical Analysis Masterclass',
        description: 'Advanced technical analysis techniques',
        category: 'analysis',
        duration: 2400,
        thumbnail: '/assets/images/edu-video.jpg',
        videoUrl: 'https://example.com/video2.mp4',
        level: 'advanced',
        views: 890,
        rating: 4.8
      }
    ];
  }

  function getFallbackEbooks() {
    return [
      {
        id: '1',
        title: 'Complete Trading Guide',
        description: 'Comprehensive guide to trading',
        category: 'trading',
        pages: 150,
        fileUrl: '/assets/ebooks/trading-guide.pdf',
        thumbnail: '/assets/images/edu-ebook.jpg',
        downloadCount: 2500
      }
    ];
  }

  function getFallbackCalendar() {
    return [
      {
        id: '1',
        title: 'US Non-Farm Payrolls',
        date: new Date().toISOString(),
        country: 'US',
        importance: 'high',
        currency: 'USD',
        impact: 'high'
      }
    ];
  }

  function getFallbackReports() {
    return [
      {
        id: '1',
        title: 'Weekly Market Analysis',
        description: 'Comprehensive weekly market analysis',
        category: 'analysis',
        date: new Date().toISOString(),
        fileUrl: '/assets/reports/weekly-analysis.pdf',
        thumbnail: '/assets/images/edu-analysis.jpg'
      }
    ];
  }

  return {
    // State
    videos,
    ebooks,
    calendar,
    reports,
    progress,
    isLoading,
    error,
    selectedVideo,
    selectedEbook,
    selectedReport,
    videoCategory,
    ebookCategory,
    reportCategory,
    searchQuery,
    // Computed
    filteredVideos,
    filteredEbooks,
    filteredReports,
    // Actions
    fetchVideos,
    fetchVideoById,
    fetchEbooks,
    fetchEbookById,
    fetchCalendar,
    fetchReports,
    fetchReportById,
    updateProgress,
    setVideoCategory,
    setEbookCategory,
    setReportCategory,
    setSearchQuery
  };
});

