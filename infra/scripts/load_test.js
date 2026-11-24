// HeartXAI 2.0 — K6 Concurrent Synthetic Load Test Script (Milestone 19)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '15s', target: 10 },
    { duration: '30s', target: 25 },
    { duration: '15s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<250'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  const liveRes = http.get(`${BASE_URL}/health/live`);
  check(liveRes, {
    'health live status is 200': (r) => r.status === 200,
  });

  const countriesRes = http.get(`${BASE_URL}/api/v1/directory/countries`);
  check(countriesRes, {
    'countries endpoint status is 200': (r) => r.status === 200,
  });

  sleep(0.5);
}
