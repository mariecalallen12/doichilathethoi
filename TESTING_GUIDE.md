# 🧪 TESTING GUIDE - Admin Control Logic

**Date:** 2025-12-20  
**Version:** 1.0.0

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Backend Testing](#backend-testing)
3. [API Endpoint Testing](#api-endpoint-testing)
4. [Frontend Testing](#frontend-testing)
5. [Integration Testing](#integration-testing)
6. [Performance Testing](#performance-testing)

---

## 1️⃣ PREREQUISITES

### Required Tools
```bash
# Python packages
pip install pytest pytest-asyncio httpx

# HTTP testing
apt-get install curl jq

# Optional: Postman or Insomnia
```

### Environment Setup
```bash
# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/digital_utopia"
export REDIS_URL="redis://localhost:6379/0"

# Start services
docker-compose up -d postgres redis
```

---

## 2️⃣ BACKEND TESTING

### A. Syntax Validation
```bash
cd backend

# Check all Python files
python3 -m py_compile app/services/scenario_manager.py
python3 -m py_compile app/services/win_rate_controller.py
python3 -m py_compile app/api/endpoints/admin_scenarios.py
python3 -m py_compile app/api/endpoints/admin_simulation.py

# Should output nothing if OK
```

### B. Import Testing
```bash
cd backend
python3 << 'PYEOF'
from app.services.scenario_manager import ScenarioManager, get_scenario_manager
from app.services.win_rate_controller import WinRateController
from app.models.market import MarketScenario
print("✅ All imports successful")
PYEOF
```

### C. Unit Tests
```bash
# Run unit tests
pytest tests/test_scenario_manager.py -v
pytest tests/test_win_rate_controller.py -v
pytest tests/test_admin_endpoints.py -v
```

---

## 3️⃣ API ENDPOINT TESTING

### Prerequisites
```bash
# Start backend
cd backend
uvicorn main:app --reload --port 8000

# Get admin token (replace with actual credentials)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')
```

### A. Scenario Endpoints

#### 1. Create Scenario
```bash
curl -X POST http://localhost:8000/api/admin/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bull Market Test",
    "description": "Testing bull market scenario",
    "scenario_type": "bull",
    "config": {
      "trend": "up",
      "volatility": 0.02,
      "volume_multiplier": 1.5
    }
  }' | jq .

# Expected: 200 OK
# Response should include: id, name, scenario_type, config
```

#### 2. List Scenarios
```bash
curl -X GET http://localhost:8000/api/admin/scenarios \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Response: array of scenarios
```

#### 3. Get Specific Scenario
```bash
SCENARIO_ID=1  # Replace with actual ID

curl -X GET http://localhost:8000/api/admin/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Response: scenario object
```

#### 4. Update Scenario
```bash
curl -X PUT http://localhost:8000/api/admin/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bull Market Updated",
    "config": {
      "trend": "up",
      "volatility": 0.03
    }
  }' | jq .

# Expected: 200 OK
```

#### 5. Activate Scenario
```bash
curl -X POST http://localhost:8000/api/admin/scenarios/$SCENARIO_ID/activate \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Response should indicate scenario activated
```

#### 6. Check Active Scenario
```bash
curl -X GET http://localhost:8000/api/admin/scenarios/active/current \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Response: active scenario or null
```

#### 7. Deactivate Scenario
```bash
curl -X POST http://localhost:8000/api/admin/scenarios/deactivate \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
```

#### 8. Delete Scenario
```bash
curl -X DELETE http://localhost:8000/api/admin/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
```

---

### B. Simulation Control Endpoints

#### 1. Get Status
```bash
curl -X GET http://localhost:8000/api/admin/simulation/status \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Response includes: is_running, current_scenario, symbols, current_prices
```

#### 2. Start Simulation
```bash
curl -X POST http://localhost:8000/api/admin/simulation/start \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Check status: is_running should be true
```

#### 3. Stop Simulation
```bash
curl -X POST http://localhost:8000/api/admin/simulation/stop \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Check status: is_running should be false
```

#### 4. Restart Simulation
```bash
curl -X POST http://localhost:8000/api/admin/simulation/restart \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
```

#### 5. Update Config
```bash
curl -X PUT http://localhost:8000/api/admin/simulation/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "volatility": 0.01,
    "trend": "up",
    "volume_multiplier": 2.0
  }' | jq .

# Expected: 200 OK
# Verify config updated in status endpoint
```

#### 6. Reset Prices
```bash
curl -X POST http://localhost:8000/api/admin/simulation/reset-prices \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Response includes reset prices
```

#### 7. Get Metrics
```bash
curl -X GET http://localhost:8000/api/admin/simulation/metrics \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 OK
# Response includes: total_trades_generated, trades_per_symbol, price_changes
```

---

### C. Win Rate Endpoints

#### 1. Adjust Win Rate
```bash
USER_ID=1  # Replace with actual user ID

curl -X POST http://localhost:8000/api/admin/trading-adjustments/win-rate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": '$USER_ID',
    "target_win_rate": 75.0,
    "mode": "immediate"
  }' | jq .

# Expected: 200 OK
# Response includes: previous_win_rate, new_win_rate, positions_adjusted
```

---

## 4️⃣ FRONTEND TESTING

### A. Admin UI Testing

#### 1. SimulationControl.vue
```bash
# Open in browser
http://localhost:3000/admin/simulation-control

# Test actions:
- [ ] Page loads without errors
- [ ] Status cards display correctly
- [ ] Start button works
- [ ] Stop button works
- [ ] Restart button works
- [ ] Reset prices works
- [ ] Config update works
- [ ] Auto-refresh every 5s
```

---

## 5️⃣ INTEGRATION TESTING

### Scenario: Complete Workflow

```bash
# 1. Create scenario
RESPONSE=$(curl -s -X POST http://localhost:8000/api/admin/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Integration Test",
    "scenario_type": "volatile",
    "config": {"trend": "sideways", "volatility": 0.05}
  }')

SCENARIO_ID=$(echo $RESPONSE | jq -r '.id')
echo "Created scenario: $SCENARIO_ID"

# 2. Activate scenario
curl -s -X POST http://localhost:8000/api/admin/scenarios/$SCENARIO_ID/activate \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Start simulation
curl -s -X POST http://localhost:8000/api/admin/simulation/start \
  -H "Authorization: Bearer $TOKEN" | jq .

# 4. Wait and check status
sleep 5
curl -s -X GET http://localhost:8000/api/admin/simulation/status \
  -H "Authorization: Bearer $TOKEN" | jq .

# Verify:
# - is_running = true
# - current_scenario.id = $SCENARIO_ID
# - current_prices changing

# 5. Check metrics
curl -s -X GET http://localhost:8000/api/admin/simulation/metrics \
  -H "Authorization: Bearer $TOKEN" | jq .

# Verify:
# - total_trades_generated > 0
# - price_changes exist

# 6. Stop simulation
curl -s -X POST http://localhost:8000/api/admin/simulation/stop \
  -H "Authorization: Bearer $TOKEN" | jq .

# 7. Deactivate scenario
curl -s -X POST http://localhost:8000/api/admin/scenarios/deactivate \
  -H "Authorization: Bearer $TOKEN" | jq .

# 8. Delete scenario
curl -s -X DELETE http://localhost:8000/api/admin/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "✅ Integration test complete!"
```

---

## 6️⃣ PERFORMANCE TESTING

### Load Test: Concurrent Requests
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test scenarios endpoint
ab -n 100 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/scenarios

# Expected: < 100ms average response time

# Test simulation status
ab -n 1000 -c 50 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/simulation/status

# Expected: < 50ms average response time
```

---

## ✅ TEST RESULTS CHECKLIST

- [ ] All syntax checks pass
- [ ] All imports successful
- [ ] FastAPI app starts
- [ ] All routes registered
- [ ] Scenario CRUD works
- [ ] Scenario activation works
- [ ] Simulation start/stop works
- [ ] Simulation config update works
- [ ] Win rate adjustment works
- [ ] Frontend UI loads
- [ ] Integration workflow works
- [ ] Performance acceptable

---

## 🐛 TROUBLESHOOTING

### Issue: Import errors
```bash
# Solution: Check PYTHONPATH
export PYTHONPATH=/root/forexxx/backend:$PYTHONPATH
```

### Issue: Database connection failed
```bash
# Solution: Check PostgreSQL running
docker-compose ps postgres
docker-compose logs postgres
```

### Issue: 401 Unauthorized
```bash
# Solution: Refresh token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')
```

### Issue: Scenario not activating
```bash
# Solution: Check TradeBroadcaster
curl http://localhost:8000/api/admin/simulation/status \
  -H "Authorization: Bearer $TOKEN" | jq '.current_scenario'
```

---

**Last Updated:** 2025-12-20  
**Author:** GitHub Copilot CLI
