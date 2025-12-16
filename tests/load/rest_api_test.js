import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const latencyP95 = new Rate('latency_p95');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 100 },   // Ramp up to 100 VUs
    { duration: '1m', target: 100 },     // Stay at 100
    { duration: '30s', target: 500 },    // Ramp up to 500
    { duration: '2m', target: 500 },     // Stay at 500
    { duration: '30s', target: 0 },      // Ramp down
  ],
  thresholds: {
    errors: ['rate<0.01'],              // Less than 1% errors
    http_req_duration: ['p(95)<500'],   // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],     // Less than 1% failed requests
  },
};

const API_BASE = __ENV.API_BASE || 'http://localhost:8000/api';
let authToken = null;

export function setup() {
  // Get auth token
  const loginRes = http.post(`${API_BASE}/auth/login`, JSON.stringify({
    email: __ENV.ADMIN_EMAIL || 'admin@example.com',
    password: __ENV.ADMIN_PASSWORD || 'admin123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  if (loginRes.status === 200) {
    const data = JSON.parse(loginRes.body);
    authToken = data.access_token;
  }

  return { apiBase: API_BASE, token: authToken };
}

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };

  // Test snapshot endpoint
  const snapshotRes = http.get(`${data.apiBase}/sim/snapshot`, { headers });
  const snapshotSuccess = check(snapshotRes, {
    'snapshot status is 200': (r) => r.status === 200,
    'snapshot has data': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.prices && Object.keys(data.prices).length > 0;
      } catch {
        return false;
      }
    },
  });

  if (!snapshotSuccess) {
    errorRate.add(1);
  }

  // Test orderbook endpoint
  const orderbookRes = http.get(`${data.apiBase}/sim/orderbook?symbol=BTCUSDT`, { headers });
  check(orderbookRes, {
    'orderbook status is 200': (r) => r.status === 200,
  });

  // Test scenarios endpoint
  const scenariosRes = http.get(`${data.apiBase}/sim/scenarios`, { headers });
  check(scenariosRes, {
    'scenarios status is 200': (r) => r.status === 200,
  });

  // Check latency
  const p95 = snapshotRes.timings.duration;
  if (p95 < 500) {
    latencyP95.add(1);
  }

  sleep(1);
}

