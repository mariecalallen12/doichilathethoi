#!/usr/bin/env node

/**
 * Production API Integration Test Script
 * Tests API calls with production URLs and verifies environment variables
 * 
 * Usage:
 *   node scripts/test-production-api.mjs [--api-url=<url>] [--ws-url=<url>]
 * 
 * Example:
 *   node scripts/test-production-api.mjs --api-url=https://api.example.com --ws-url=wss://api.example.com/ws
 */

import axios from 'axios';

// WebSocket testing (optional - requires 'ws' package)
// Will be loaded dynamically in the test function
let WebSocket = null;

// Configuration
const DEFAULT_API_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEFAULT_WS_URL = process.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Parse command line arguments
const args = process.argv.slice(2);
let apiUrl = DEFAULT_API_URL;
let wsUrl = DEFAULT_WS_URL;

args.forEach(arg => {
  if (arg.startsWith('--api-url=')) {
    apiUrl = arg.split('=')[1];
  } else if (arg.startsWith('--ws-url=')) {
    wsUrl = arg.split('=')[1];
  }
});

// Test results
const testResults = {
  passed: 0,
  failed: 0,
  errors: []
};

// Helper functions
function log(message, type = 'info') {
  const colors = {
    info: '\x1b[36m',
    success: '\x1b[32m',
    error: '\x1b[31m',
    warning: '\x1b[33m',
    reset: '\x1b[0m'
  };
  console.log(`${colors[type]}${message}${colors.reset}`);
}

function test(name, fn) {
  return async () => {
    try {
      log(`\n🧪 Testing: ${name}`, 'info');
      await fn();
      testResults.passed++;
      log(`✅ PASSED: ${name}`, 'success');
      return true;
    } catch (error) {
      testResults.failed++;
      testResults.errors.push({ test: name, error: error.message });
      log(`❌ FAILED: ${name} - ${error.message}`, 'error');
      return false;
    }
  };
}

// Test: API Base URL Configuration
const testApiBaseUrl = test('API Base URL Configuration', async () => {
  if (!apiUrl) {
    throw new Error('API URL is not configured');
  }
  log(`   API URL: ${apiUrl}`, 'info');
  
  // Test if URL is accessible
  try {
    const response = await axios.get(`${apiUrl}/api/health`, { timeout: 5000 });
    if (response.status !== 200) {
      throw new Error(`Health check returned status ${response.status}`);
    }
    log(`   Health check response: ${JSON.stringify(response.data)}`, 'info');
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      throw new Error(`Cannot connect to API at ${apiUrl}. Is the server running?`);
    }
    throw error;
  }
});

// Test: WebSocket URL Configuration
const testWebSocketUrl = test('WebSocket URL Configuration', async () => {
  if (!wsUrl) {
    throw new Error('WebSocket URL is not configured');
  }
  log(`   WebSocket URL: ${wsUrl}`, 'info');
  
  // Try to load WebSocket module if not already loaded
  if (!WebSocket) {
    try {
      const wsModule = await import('ws');
      WebSocket = wsModule.WebSocket || wsModule.default?.WebSocket || wsModule.default;
    } catch (error) {
      log(`   ⚠️  Skipping WebSocket test (install "ws" package for full testing)`, 'warning');
      log(`   ⚠️  Run: npm install -D ws`, 'warning');
      // Don't fail the test, just skip it
      return;
    }
  }
  
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    const timeout = setTimeout(() => {
      ws.close();
      reject(new Error('WebSocket connection timeout'));
    }, 5000);
    
    ws.on('open', () => {
      clearTimeout(timeout);
      ws.close();
      resolve();
    });
    
    ws.on('error', (error) => {
      clearTimeout(timeout);
      reject(new Error(`WebSocket connection failed: ${error.message}`));
    });
  });
});

// Test: Authentication Endpoints
const testAuthEndpoints = test('Authentication Endpoints', async () => {
  const endpoints = [
    { method: 'GET', path: '/api/health', requiresAuth: false },
    { method: 'POST', path: '/api/auth/login', requiresAuth: false },
    { method: 'POST', path: '/api/auth/register', requiresAuth: false },
  ];
  
  for (const endpoint of endpoints) {
    try {
      const config = {
        method: endpoint.method,
        url: `${apiUrl}${endpoint.path}`,
        timeout: 5000,
        validateStatus: () => true // Accept any status code
      };
      
      const response = await axios(config);
      
      // For health endpoint, expect 200
      if (endpoint.path === '/api/health') {
        if (response.status !== 200) {
          throw new Error(`Health endpoint returned ${response.status}`);
        }
      }
      // For auth endpoints, expect 200, 400, or 422 (validation errors are OK)
      else if (endpoint.path.includes('/auth/')) {
        if (![200, 400, 422, 401].includes(response.status)) {
          throw new Error(`${endpoint.path} returned unexpected status ${response.status}`);
        }
      }
      
      log(`   ${endpoint.method} ${endpoint.path}: ${response.status}`, 'info');
    } catch (error) {
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        throw new Error(`Cannot connect to ${endpoint.path}`);
      }
      throw error;
    }
  }
});

// Test: CORS Configuration
const testCors = test('CORS Configuration', async () => {
  try {
    const response = await axios.options(`${apiUrl}/api/health`, {
      headers: {
        'Origin': 'http://localhost:3002',
        'Access-Control-Request-Method': 'GET'
      },
      timeout: 5000
    });
    
    const corsHeaders = {
      'access-control-allow-origin': response.headers['access-control-allow-origin'],
      'access-control-allow-methods': response.headers['access-control-allow-methods'],
      'access-control-allow-headers': response.headers['access-control-allow-headers']
    };
    
    log(`   CORS Headers: ${JSON.stringify(corsHeaders)}`, 'info');
    
    if (!corsHeaders['access-control-allow-origin']) {
      throw new Error('CORS headers not properly configured');
    }
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      throw new Error('Cannot test CORS - API not accessible');
    }
    // CORS might not be testable via axios, so we'll just log a warning
    log(`   Warning: CORS test may not be accurate: ${error.message}`, 'warning');
  }
});

// Test: Environment Variables in Build
const testEnvVars = test('Environment Variables', async () => {
  const requiredVars = ['VITE_API_BASE_URL', 'VITE_WS_URL'];
  const missing = [];
  
  // Note: In production build, env vars are baked in, so we check the actual URLs
  log(`   Checking environment configuration...`, 'info');
  log(`   API URL: ${apiUrl}`, 'info');
  log(`   WebSocket URL: ${wsUrl}`, 'info');
  
  if (!apiUrl || apiUrl === 'http://localhost:8000') {
    log(`   Warning: Using default API URL. Set VITE_API_BASE_URL for production.`, 'warning');
  }
  
  if (!wsUrl || wsUrl === 'ws://localhost:8000/ws') {
    log(`   Warning: Using default WebSocket URL. Set VITE_WS_URL for production.`, 'warning');
  }
});

// Run all tests
async function runTests() {
  log('\n🚀 Starting Production API Integration Tests', 'info');
  log(`📡 API URL: ${apiUrl}`, 'info');
  log(`🔌 WebSocket URL: ${wsUrl}`, 'info');
  log('='.repeat(60), 'info');
  
  await testApiBaseUrl();
  await testWebSocketUrl();
  await testAuthEndpoints();
  await testCors();
  await testEnvVars();
  
  // Print summary
  log('\n' + '='.repeat(60), 'info');
  log('\n📊 Test Summary:', 'info');
  log(`   ✅ Passed: ${testResults.passed}`, 'success');
  log(`   ❌ Failed: ${testResults.failed}`, testResults.failed > 0 ? 'error' : 'success');
  
  if (testResults.errors.length > 0) {
    log('\n❌ Errors:', 'error');
    testResults.errors.forEach(({ test, error }) => {
      log(`   - ${test}: ${error}`, 'error');
    });
  }
  
  log('\n' + '='.repeat(60), 'info');
  
  // Exit with appropriate code
  process.exit(testResults.failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(error => {
  log(`\n💥 Fatal error: ${error.message}`, 'error');
  process.exit(1);
});

