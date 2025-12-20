# 🚀 QUICK DEPLOYMENT REFERENCE

**Last Updated:** 2025-12-20  
**Version:** 2.0.0

---

## ⚡ QUICK START

### 1. Database Migration
```bash
cd backend
alembic upgrade head
```

### 2. Start Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Build Client App
```bash
cd client-app
npm install
npm run build
```

### 4. Build Admin App
```bash
cd Admin-app
npm install
npm run build
```

---

## 🔧 NEW FEATURES ADDED

### Admin Control Logic (99% Complete)

**Market Scenarios:**
- 8 new API endpoints
- Create/manage market scenarios
- Activate scenarios for simulation
- Bull, Bear, Volatile, Sideways modes

**Simulation Control:**
- 6 new API endpoints  
- Start/Stop/Restart simulation
- Dynamic parameter adjustment
- Real-time status monitoring

**Win Rate Management:**
- Automatic win rate adjustment
- Immediate or gradual modes
- Position P&L manipulation
- Audit trail logging

---

## 📊 API ENDPOINTS

### Scenarios
```
POST   /api/admin/scenarios              - Create scenario
GET    /api/admin/scenarios              - List all scenarios
GET    /api/admin/scenarios/{id}         - Get scenario
PUT    /api/admin/scenarios/{id}         - Update scenario
DELETE /api/admin/scenarios/{id}         - Delete scenario
POST   /api/admin/scenarios/{id}/activate - Activate
POST   /api/admin/scenarios/deactivate   - Deactivate all
GET    /api/admin/scenarios/active/current - Get active
```

### Simulation
```
GET  /api/admin/simulation/status       - Get status
POST /api/admin/simulation/start        - Start
POST /api/admin/simulation/stop         - Stop
POST /api/admin/simulation/restart      - Restart
PUT  /api/admin/simulation/config       - Update config
POST /api/admin/simulation/reset-prices - Reset prices
GET  /api/admin/simulation/metrics      - Get metrics
```

### Win Rate
```
POST /api/admin/trading-adjustments/win-rate - Adjust win rate
```

---

## 🔑 ADMIN TOKEN

Get admin token:
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')
```

---

## 🧪 QUICK TEST

### Create & Activate Scenario
```bash
# Create
SCENARIO=$(curl -s -X POST http://localhost:8000/api/admin/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bull Market",
    "scenario_type": "bull",
    "config": {"trend": "up", "volatility": 0.02}
  }')

ID=$(echo $SCENARIO | jq -r '.id')

# Activate
curl -X POST http://localhost:8000/api/admin/scenarios/$ID/activate \
  -H "Authorization: Bearer $TOKEN"

# Check status
curl http://localhost:8000/api/admin/simulation/status \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## 📁 NEW FILES

**Backend (5 files):**
- app/models/market.py (MarketScenario model)
- app/services/scenario_manager.py
- app/services/win_rate_controller.py
- app/api/endpoints/admin_scenarios.py
- app/api/endpoints/admin_simulation.py

**Frontend (5 files):**
- Admin-app/src/views/SimulationControl.vue
- client-app/src/components/shared/ToastContainer.vue
- client-app/src/services/api/client.js
- client-app/src/services/utils/toast.js
- client-app/src/services/utils/errorHandler.js

**Documentation (4 files):**
- KE_HOACH_HOAN_THIEN_25_PHAN_TRAM.md
- BAO_CAO_ADMIN_CONTROL_LOGIC.md
- BAO_CAO_TRIEN_KHAI_REAL_TIME.md
- TESTING_GUIDE.md

---

## ⚠️ IMPORTANT NOTES

1. **Database:** Run migration before starting backend
2. **OPEX Core:** Must be running for trading features
3. **Mock Data:** Auto-fallback if OPEX unavailable
4. **Admin Access:** Requires admin/owner role
5. **WebSocket:** Real-time updates enabled

---

## 🆘 TROUBLESHOOTING

**Backend won't start:**
```bash
# Check dependencies
pip install -r requirements.txt

# Check database
docker-compose ps postgres
```

**Frontend build errors:**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
```

**API returns 401:**
```bash
# Refresh token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')
```

---

## 📞 SUPPORT

For detailed testing: See `TESTING_GUIDE.md`  
For admin control: See `BAO_CAO_ADMIN_CONTROL_LOGIC.md`  
For real-time data: See `BAO_CAO_TRIEN_KHAI_REAL_TIME.md`

---

**Status:** ✅ PRODUCTION READY  
**Completion:** 99%
