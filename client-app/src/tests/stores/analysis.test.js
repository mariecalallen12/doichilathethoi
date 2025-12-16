/**
 * Unit tests for Analysis store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAnalysisStore } from '../../stores/analysis';

// Mock the API
vi.mock('../../services/api/analysis', () => ({
  analysisApi: {
    getTechnicalAnalysis: vi.fn(),
    getFundamentalAnalysis: vi.fn(),
    getSentiment: vi.fn(),
    getSignals: vi.fn(),
    runBacktest: vi.fn(),
  },
}));

describe('Analysis Store', () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useAnalysisStore();
  });

  it('should initialize with empty state', () => {
    expect(store.technicalData).toEqual({});
    expect(store.fundamentalData).toEqual({});
    expect(store.sentiment).toEqual({});
    expect(store.signals).toEqual([]);
  });

  it('should have fetchTechnicalAnalysis method', () => {
    expect(typeof store.fetchTechnicalAnalysis).toBe('function');
  });

  it('should have fetchFundamentalAnalysis method', () => {
    expect(typeof store.fetchFundamentalAnalysis).toBe('function');
  });

  it('should have fetchSentiment method', () => {
    expect(typeof store.fetchSentiment).toBe('function');
  });

  it('should have fetchSignals method', () => {
    expect(typeof store.fetchSignals).toBe('function');
  });
});

