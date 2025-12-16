/**
 * Unit tests for Legal store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useLegalStore } from '../../stores/legal';

// Mock the API
vi.mock('../../services/api/legal', () => ({
  legalApi: {
    getTerms: vi.fn(),
    getPrivacy: vi.fn(),
    getRiskWarning: vi.fn(),
    submitComplaint: vi.fn(),
    getComplaints: vi.fn(),
  },
}));

describe('Legal Store', () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useLegalStore();
  });

  it('should initialize with empty state', () => {
    expect(store.terms).toBeNull();
    expect(store.privacy).toBeNull();
    expect(store.riskWarning).toBeNull();
    expect(store.complaints).toEqual([]);
  });

  it('should have fetchTerms method', () => {
    expect(typeof store.fetchTerms).toBe('function');
  });

  it('should have fetchPrivacy method', () => {
    expect(typeof store.fetchPrivacy).toBe('function');
  });

  it('should have fetchRiskWarning method', () => {
    expect(typeof store.fetchRiskWarning).toBe('function');
  });

  it('should have submitComplaint method', () => {
    expect(typeof store.submitComplaint).toBe('function');
  });
});

