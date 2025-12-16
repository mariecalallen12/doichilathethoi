import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const messageRate = new Rate('messages_received');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 1000 },   // Ramp up to 1000 connections
    { duration: '1m', target: 1000 },    // Stay at 1000
    { duration: '30s', target: 5000 },   // Ramp up to 5000
    { duration: '2m', target: 5000 },    // Stay at 5000
    { duration: '30s', target: 10000 },  // Ramp up to 10000
    { duration: '5m', target: 10000 },   // Stay at 10000 for 5 minutes
    { duration: '30s', target: 0 },      // Ramp down
  ],
  thresholds: {
    errors: ['rate<0.01'],              // Less than 1% errors
    'ws_connecting': ['p(95)<200'],     // 95% connection time < 200ms
    'ws_session_duration': ['p(95)<5000'], // 95% of sessions < 5s
    'messages_received': ['rate>0.8'],   // At least 80% message rate
  },
};

// WebSocket URL - adjust based on your environment
const WS_URL = __ENV.WS_URL || 'ws://localhost:8000/ws';
const API_BASE = __ENV.API_BASE || 'http://localhost:8000/api';

// Get auth token (simplified - in production, use proper auth)
let authToken = null;

export function setup() {
  // Optionally get auth token here
  // For now, we'll test without auth if WebSocket doesn't require it
  return { wsUrl: WS_URL };
}

export default function (data) {
  const url = `${data.wsUrl}?token=${authToken || ''}`;
  let messageCount = 0;
  let errorCount = 0;

  const response = ws.connect(url, {}, function (socket) {
    socket.on('open', function () {
      // Subscribe to channels
      socket.send(JSON.stringify({
        type: 'subscribe',
        channel: 'prices',
        symbol: 'BTCUSDT',
      }));
      
      socket.send(JSON.stringify({
        type: 'subscribe',
        channel: 'orderbook',
        symbol: 'BTCUSDT',
      }));
      
      socket.send(JSON.stringify({
        type: 'subscribe',
        channel: 'trades',
        symbol: 'BTCUSDT',
      }));

      // Send ping every 30 seconds
      const pingInterval = setInterval(() => {
        socket.send(JSON.stringify({ type: 'ping' }));
      }, 30000);

      socket.setTimeout(() => {
        clearInterval(pingInterval);
        socket.close();
      }, 300000); // Close after 5 minutes
    });

    socket.on('message', function (data) {
      messageCount++;
      messageRate.add(1);
      
      try {
        const message = JSON.parse(data);
        check(message, {
          'message is valid JSON': (m) => typeof m === 'object',
        });
      } catch (e) {
        errorCount++;
        errorRate.add(1);
      }
    });

    socket.on('error', function (e) {
      errorCount++;
      errorRate.add(1);
      console.error('WebSocket error:', e);
    });

    socket.on('close', function () {
      // Connection closed
    });
  });

  const success = check(response, {
    'WebSocket connection successful': (r) => r && r.status === 101,
  });

  if (!success) {
    errorRate.add(1);
  }

  // Sleep for a bit to simulate real usage
  sleep(1);
}

export function teardown(data) {
  // Cleanup if needed
}

