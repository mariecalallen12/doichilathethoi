/**
 * Unit tests for Support store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useSupportStore } from '../../stores/support';

// Mock the API
vi.mock('../../services/api/support', () => ({
  supportApi: {
    getArticles: vi.fn(),
    getArticleById: vi.fn(),
    getCategories: vi.fn(),
    searchArticles: vi.fn(),
    submitContact: vi.fn(),
    getFaq: vi.fn(),
    searchFaq: vi.fn(),
  },
}));

describe('Support Store', () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useSupportStore();
  });

  it('should initialize with empty state', () => {
    expect(store.articles).toEqual([]);
    expect(store.categories).toEqual([]);
    expect(store.faqItems).toEqual([]);
  });

  it('should have fetchArticles method', () => {
    expect(typeof store.fetchArticles).toBe('function');
  });

  it('should have fetchCategories method', () => {
    expect(typeof store.fetchCategories).toBe('function');
  });

  it('should have fetchFaq method', () => {
    expect(typeof store.fetchFaq).toBe('function');
  });

  it('should have searchArticles method', () => {
    expect(typeof store.searchArticles).toBe('function');
  });
});

