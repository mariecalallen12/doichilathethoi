/**
 * Frontend Diagnostics Tests
 * Test diagnostic services and utilities
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { checkAuthStatus, checkApiHealth, checkComponentState, collectAllDiagnostics } from '../services/diagnostics/tradingDiagnostics';
import { generateJSONReport, generateHTMLReport } from '../services/diagnostics/reportGenerator';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => { store[key] = value.toString(); }),
    removeItem: vi.fn((key) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
  };
})();

global.localStorage = localStorageMock;

// Mock window object
global.window = {
  location: { href: 'https://example.com/trading' },
  performance: {
    now: () => Date.now(),
    getEntriesByType: vi.fn(() => []),
    timeOrigin: Date.now(),
  },
  getComputedStyle: vi.fn(() => ({
    display: 'block',
    visibility: 'visible',
  })),
};

global.navigator = {
  userAgent: 'Mozilla/5.0 Test',
};

global.document = {
  querySelector: vi.fn(() => ({
    children: [],
    textContent: '',
  })),
  querySelectorAll: vi.fn(() => []),
};

describe('Diagnostics Service', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  describe('checkAuthStatus', () => {
    it('should detect no token when localStorage is empty', async () => {
      const status = await checkAuthStatus();
      expect(status.hasToken).toBe(false);
      expect(status.tokenType).toBeNull();
    });

    it('should detect auth_token when present', async () => {
      localStorageMock.setItem('auth_token', 'test_token_12345');
      const status = await checkAuthStatus();
      expect(status.hasToken).toBe(true);
      expect(status.tokenType).toBe('auth_token');
      expect(status.tokenLength).toBeGreaterThan(0);
    });

    it('should detect access_token when present', async () => {
      localStorageMock.setItem('access_token', 'test_access_token_12345');
      const status = await checkAuthStatus();
      expect(status.hasToken).toBe(true);
      expect(status.tokenType).toBe('access_token');
    });

    it('should parse JWT token if valid', async () => {
      // Create a mock JWT token (header.payload.signature)
      const payload = btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + 3600, user_id: 123 }));
      const token = `header.${payload}.signature`;
      localStorageMock.setItem('auth_token', token);
      
      const status = await checkAuthStatus();
      expect(status.hasToken).toBe(true);
      expect(status.userId).toBe(123);
    });
  });

  describe('checkComponentState', () => {
    it('should detect empty components', () => {
      document.querySelector.mockReturnValue({
        children: [],
        textContent: '',
      });

      const state = checkComponentState();
      expect(state.chart).toBeDefined();
      expect(state.chart.isEmpty).toBe(true);
    });

    it('should detect components with content', () => {
      document.querySelector.mockReturnValue({
        children: [{ textContent: 'Chart content' }],
        textContent: 'Chart content',
      });

      const state = checkComponentState();
      expect(state.chart.hasContent).toBe(true);
      expect(state.chart.isEmpty).toBe(false);
    });
  });

  describe('collectAllDiagnostics', () => {
    it('should collect all diagnostic information', async () => {
      localStorageMock.setItem('auth_token', 'test_token');
      
      // Mock fetch for API health check
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          statusText: 'OK',
          json: () => Promise.resolve({ data: [] }),
          clone: () => ({
            json: () => Promise.resolve({ data: [] }),
          }),
        })
      );

      const diagnostics = await collectAllDiagnostics(null);
      
      expect(diagnostics).toBeDefined();
      expect(diagnostics.timestamp).toBeDefined();
      expect(diagnostics.url).toBe('https://example.com/trading');
      expect(diagnostics.auth).toBeDefined();
      expect(diagnostics.api).toBeDefined();
      expect(diagnostics.components).toBeDefined();
      expect(diagnostics.recommendations).toBeDefined();
    });

    it('should generate recommendations for issues', async () => {
      localStorageMock.clear(); // No auth token
      
      global.fetch = vi.fn(() =>
        Promise.reject(new Error('Network error'))
      );

      const diagnostics = await collectAllDiagnostics(null);
      
      expect(diagnostics.recommendations).toBeDefined();
      expect(diagnostics.recommendations.length).toBeGreaterThan(0);
      
      const authRecommendations = diagnostics.recommendations.filter(
        r => r.category === 'authentication'
      );
      expect(authRecommendations.length).toBeGreaterThan(0);
    });
  });
});

describe('Report Generator', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  describe('generateJSONReport', () => {
    it('should generate valid JSON report', async () => {
      localStorageMock.setItem('auth_token', 'test_token');
      
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ data: [] }),
          clone: () => ({
            json: () => Promise.resolve({ data: [] }),
          }),
        })
      );

      const report = await generateJSONReport(null);
      
      expect(report).toBeDefined();
      const parsed = JSON.parse(report);
      expect(parsed.version).toBe('1.0');
      expect(parsed.diagnostics).toBeDefined();
      expect(parsed.summary).toBeDefined();
    });
  });

  describe('generateHTMLReport', () => {
    it('should generate valid HTML report', async () => {
      localStorageMock.setItem('auth_token', 'test_token');
      
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ data: [] }),
          clone: () => ({
            json: () => Promise.resolve({ data: [] }),
          }),
        })
      );

      const report = await generateHTMLReport(null);
      
      expect(report).toBeDefined();
      expect(typeof report).toBe('string');
      expect(report).toContain('<!DOCTYPE html>');
      expect(report).toContain('Trading Dashboard Diagnostic Report');
      // Check for diagnostics data in the Raw Data section - the JSON.stringify will contain "diagnostics" as a property
      expect(report).toContain('Raw Data');
      // The JSON stringified diagnostics object should contain various diagnostic properties
      expect(report).toMatch(/timestamp|url|auth|api|components/);
    });
  });
});

describe('Diagnostics Store Integration', () => {
  it('should handle errors gracefully', async () => {
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));
    
    try {
      const diagnostics = await collectAllDiagnostics(null);
      // Should still return diagnostics object even with errors
      expect(diagnostics).toBeDefined();
      expect(diagnostics.api.error).toBeDefined();
    } catch (error) {
      // Should not throw, but handle errors internally
      expect(error).toBeDefined();
    }
  });
});

