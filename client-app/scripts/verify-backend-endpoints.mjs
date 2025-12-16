#!/usr/bin/env node
/**
 * Script to verify all backend endpoints for Education, Analysis, Support, and Legal modules
 */

import axios from 'axios';

const BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const API_BASE = `${BASE_URL}/api`;

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
  console.log('\n' + '='.repeat(60));
  log(title, 'cyan');
  console.log('='.repeat(60));
}

async function testEndpoint(method, path, description, requiresAuth = false) {
  try {
    const url = `${API_BASE}${path}`;
    const config = {
      method,
      url,
      timeout: 5000,
      validateStatus: () => true, // Don't throw on any status
    };

    if (requiresAuth) {
      // Try with a dummy token - will fail auth but shows endpoint exists
      config.headers = { Authorization: 'Bearer test_token' };
    }

    const startTime = Date.now();
    const response = await axios(config);
    const duration = Date.now() - startTime;

    const status = response.status;
    const statusColor = status < 400 ? 'green' : status < 500 ? 'yellow' : 'red';
    const statusText = status < 400 ? '✓' : status === 401 ? '⚠ (Auth Required)' : status === 404 ? '✗ (Not Found)' : '✗';

    log(`  ${statusText} ${description}`, statusColor);
    log(`    ${method} ${path} - Status: ${status} (${duration}ms)`, 'blue');

    return {
      success: status < 400 || status === 401,
      status,
      duration,
      exists: status !== 404,
    };
  } catch (error) {
    log(`  ✗ ${description}`, 'red');
    log(`    Error: ${error.message}`, 'red');
    return {
      success: false,
      status: 0,
      duration: 0,
      exists: false,
      error: error.message,
    };
  }
}

async function main() {
  log('\n🔍 Backend Endpoints Verification Script', 'cyan');
  log(`Testing against: ${BASE_URL}\n`, 'blue');

  const results = {
    education: [],
    analysis: [],
    support: [],
    legal: [],
  };

  // ========== Education Endpoints ==========
  logSection('📚 Education Module Endpoints');

  results.education.push(await testEndpoint('GET', '/education/videos', 'Get videos list'));
  results.education.push(await testEndpoint('GET', '/education/videos/1', 'Get video by ID'));
  results.education.push(await testEndpoint('GET', '/education/ebooks', 'Get ebooks list'));
  results.education.push(await testEndpoint('GET', '/education/ebooks/1', 'Get ebook by ID'));
  results.education.push(await testEndpoint('GET', '/education/calendar', 'Get economic calendar'));
  results.education.push(await testEndpoint('GET', '/education/reports', 'Get reports list'));
  results.education.push(await testEndpoint('GET', '/education/reports/1', 'Get report by ID'));
  results.education.push(await testEndpoint('POST', '/education/progress', 'Update progress', true));

  // ========== Analysis Endpoints ==========
  logSection('📈 Analysis Module Endpoints');

  results.analysis.push(await testEndpoint('GET', '/analysis/technical/BTCUSDT', 'Get technical analysis'));
  results.analysis.push(await testEndpoint('GET', '/analysis/fundamental/BTCUSDT', 'Get fundamental analysis'));
  results.analysis.push(await testEndpoint('GET', '/analysis/sentiment', 'Get market sentiment'));
  results.analysis.push(await testEndpoint('GET', '/analysis/signals', 'Get trading signals'));
  results.analysis.push(await testEndpoint('POST', '/analysis/backtest', 'Run backtest', true));

  // ========== Support Endpoints ==========
  logSection('🆘 Support Module Endpoints');

  results.support.push(await testEndpoint('GET', '/support/articles', 'Get articles list'));
  results.support.push(await testEndpoint('GET', '/support/articles/1', 'Get article by ID'));
  results.support.push(await testEndpoint('GET', '/support/categories', 'Get categories'));
  results.support.push(await testEndpoint('POST', '/support/search', 'Search articles'));
  results.support.push(await testEndpoint('POST', '/support/contact', 'Submit contact form'));
  results.support.push(await testEndpoint('GET', '/support/offices', 'Get offices'));
  results.support.push(await testEndpoint('GET', '/support/channels', 'Get channels'));
  results.support.push(await testEndpoint('GET', '/support/faq', 'Get FAQ list'));
  results.support.push(await testEndpoint('GET', '/support/faq/general', 'Get FAQ by category'));
  results.support.push(await testEndpoint('POST', '/support/faq/search', 'Search FAQ'));

  // ========== Legal Endpoints ==========
  logSection('⚖️ Legal Module Endpoints');

  results.legal.push(await testEndpoint('GET', '/legal/terms', 'Get terms of service'));
  results.legal.push(await testEndpoint('GET', '/legal/terms/version/1.0', 'Get terms by version'));
  results.legal.push(await testEndpoint('GET', '/legal/privacy', 'Get privacy policy'));
  results.legal.push(await testEndpoint('GET', '/legal/privacy/version/1.0', 'Get privacy by version'));
  results.legal.push(await testEndpoint('GET', '/legal/risk-warning', 'Get risk warning'));
  results.legal.push(await testEndpoint('GET', '/legal/complaints', 'Get complaints list', true));
  results.legal.push(await testEndpoint('POST', '/legal/complaints', 'Submit complaint', true));
  results.legal.push(await testEndpoint('GET', '/legal/complaints/1', 'Get complaint by ID', true));
  results.legal.push(await testEndpoint('PUT', '/legal/complaints/1', 'Update complaint', true));

  // ========== Summary ==========
  logSection('📊 Summary');

  const modules = [
    { name: 'Education', results: results.education, expected: 8 },
    { name: 'Analysis', results: results.analysis, expected: 5 },
    { name: 'Support', results: results.support, expected: 10 },
    { name: 'Legal', results: results.legal, expected: 9 },
  ];

  let totalEndpoints = 0;
  let totalExisting = 0;
  let totalWorking = 0;

  modules.forEach(({ name, results: moduleResults, expected }) => {
    const existing = moduleResults.filter(r => r.exists).length;
    const working = moduleResults.filter(r => r.success).length;
    totalEndpoints += moduleResults.length;
    totalExisting += existing;
    totalWorking += working;

    const statusColor = existing === expected ? 'green' : existing > 0 ? 'yellow' : 'red';
    log(`\n${name}:`, 'cyan');
    log(`  Endpoints tested: ${moduleResults.length}`, 'blue');
    log(`  Endpoints existing: ${existing}/${expected}`, statusColor);
    log(`  Endpoints working: ${working}/${expected}`, working === expected ? 'green' : 'yellow');
  });

  log('\n' + '='.repeat(60), 'cyan');
  log('Overall Summary:', 'cyan');
  log(`  Total endpoints tested: ${totalEndpoints}`, 'blue');
  log(`  Endpoints existing: ${totalExisting}/${totalEndpoints}`, totalExisting === totalEndpoints ? 'green' : 'yellow');
  log(`  Endpoints working: ${totalWorking}/${totalEndpoints}`, totalWorking === totalEndpoints ? 'green' : 'yellow');
  log('='.repeat(60) + '\n', 'cyan');

  // Exit with appropriate code
  const allExist = totalExisting === totalEndpoints;
  const allWork = totalWorking === totalEndpoints;
  
  if (!allExist) {
    log('⚠️  Some endpoints are missing (404)', 'yellow');
    process.exit(1);
  } else if (!allWork) {
    log('⚠️  Some endpoints have issues (non-200 status)', 'yellow');
    process.exit(1);
  } else {
    log('✅ All endpoints are working correctly!', 'green');
    process.exit(0);
  }
}

main().catch(error => {
  log(`\n❌ Fatal error: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});

