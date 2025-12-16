import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useEducationStore } from '../../stores/education';
import { educationApi } from '../../services/api/education';

// Mock the API
vi.mock('../../services/api/education', () => ({
  educationApi: {
    getVideos: vi.fn(),
    getEbooks: vi.fn(),
    getReports: vi.fn(),
    getCalendar: vi.fn(),
    updateProgress: vi.fn(),
  },
}));

describe('Education Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('initializes with empty state', () => {
    const store = useEducationStore();
    expect(store.videos).toEqual([]);
    expect(store.ebooks).toEqual([]);
    expect(store.calendar).toEqual([]);
    expect(store.reports).toEqual([]);
    expect(store.isLoading).toBe(false);
  });

  it('fetches videos successfully', async () => {
    const mockVideos = [
      { id: 1, title: 'Video 1', category: 'forex' },
      { id: 2, title: 'Video 2', category: 'crypto' },
    ];

    educationApi.getVideos.mockResolvedValue({
      data: mockVideos,
      success: true,
    });

    const store = useEducationStore();
    await store.fetchVideos();

    expect(store.videos).toEqual(mockVideos);
    expect(store.isLoading).toBe(false);
  });

  it('filters videos by category', () => {
    const store = useEducationStore();
    store.videos = [
      { id: 1, title: 'Video 1', category: 'forex' },
      { id: 2, title: 'Video 2', category: 'crypto' },
    ];

    store.setVideoCategory('forex');
    expect(store.filteredVideos).toHaveLength(1);
    expect(store.filteredVideos[0].category).toBe('forex');
  });

  it('filters videos by search query', () => {
    const store = useEducationStore();
    store.videos = [
      { id: 1, title: 'Forex Basics', description: 'Learn forex' },
      { id: 2, title: 'Crypto Trading', description: 'Learn crypto' },
    ];

    store.setSearchQuery('Forex');
    expect(store.filteredVideos).toHaveLength(1);
    expect(store.filteredVideos[0].title).toContain('Forex');
  });
});

