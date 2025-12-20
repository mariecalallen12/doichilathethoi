# 📋 KẾ HOẠCH HOÀN THIỆN 25% CÒN LẠI

**Ngày:** 2025-12-19  
**Mục tiêu:** Hoàn thành 100% Admin Control Logic  
**Thời gian ước tính:** ~14 hours  

---

## 📊 TỔNG QUAN CÔNG VIỆC

### Chia thành 4 giai đoạn chính:

```
Phase 1: Market Scenario System      (~4h) 🔴 HIGH
Phase 2: Simulation Control UI        (~3h) 🔴 HIGH  
Phase 3: Win Rate Backend Logic       (~2h) 🟡 MEDIUM
Phase 4: Display Controls & Testing   (~5h) 🟢 LOW
```

---

## PHASE 1: MARKET SCENARIO SYSTEM (4 hours)

### Task 1.1: Tạo MarketScenario Model (30 min)
**File:** `backend/app/models/market.py`

```python
class MarketScenario(Base, TimestampMixin):
    __tablename__ = "market_scenarios"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    scenario_type = Column(String(50))  # bull, bear, volatile, sideways
    
    # Configuration
    config = Column(JSONB, default={})
    # {
    #   "trend": "up/down/sideways",
    #   "volatility": 0.01-0.10,
    #   "volume_multiplier": 1.0-5.0,
    #   "price_change_per_interval": 0.001
    # }
    
    is_active = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    creator = relationship("User", backref="created_scenarios")
```

**Migration:**
```bash
cd backend
alembic revision --autogenerate -m "add_market_scenarios_table"
alembic upgrade head
```

---

### Task 1.2: Tạo ScenarioManager Service (1 hour)
**File:** `backend/app/services/scenario_manager.py`

```python
class ScenarioManager:
    def __init__(self):
        self.current_scenario: Optional[Dict] = None
        self.broadcaster: Optional[TradeBroadcaster] = None
        
    def apply_scenario(self, scenario_id: int, db: Session):
        """Apply a market scenario to simulation"""
        scenario = db.query(MarketScenario).filter_by(id=scenario_id).first()
        if not scenario:
            raise ValueError("Scenario not found")
            
        config = scenario.config
        
        # Update trade broadcaster parameters
        if self.broadcaster:
            self.broadcaster.set_volatility(config.get("volatility", 0.005))
            self.broadcaster.set_trend(config.get("trend", "sideways"))
            self.broadcaster.set_volume_multiplier(config.get("volume_multiplier", 1.0))
        
        # Mark scenario as active
        db.query(MarketScenario).update({"is_active": False})
        scenario.is_active = True
        db.commit()
        
        self.current_scenario = scenario.config
        return scenario
        
    def stop_scenario(self, db: Session):
        """Stop active scenario, return to normal"""
        db.query(MarketScenario).update({"is_active": False})
        db.commit()
        self.current_scenario = None
        
        # Reset broadcaster to defaults
        if self.broadcaster:
            self.broadcaster.reset_to_defaults()
            
    def get_active_scenario(self, db: Session):
        """Get currently active scenario"""
        return db.query(MarketScenario).filter_by(is_active=True).first()
```

---

### Task 1.3: Tạo Admin Endpoints cho Scenarios (1 hour)
**File:** `backend/app/api/endpoints/admin_scenarios.py`

```python
router = APIRouter(tags=["admin-scenarios"])

@router.post("/scenarios")
async def create_scenario(
    request: CreateScenarioRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Create a new market scenario"""
    scenario = MarketScenario(
        name=request.name,
        description=request.description,
        scenario_type=request.scenario_type,
        config=request.config,
        created_by=user.id
    )
    db.add(scenario)
    db.commit()
    return {"success": True, "scenario": scenario}

@router.get("/scenarios")
async def list_scenarios(
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Get all market scenarios"""
    scenarios = db.query(MarketScenario).all()
    return {"scenarios": scenarios}

@router.put("/scenarios/{scenario_id}")
async def update_scenario(
    scenario_id: int,
    request: UpdateScenarioRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Update a scenario"""
    scenario = db.query(MarketScenario).filter_by(id=scenario_id).first()
    if not scenario:
        raise HTTPException(404, "Scenario not found")
    
    for key, value in request.dict(exclude_unset=True).items():
        setattr(scenario, key, value)
    db.commit()
    return {"success": True, "scenario": scenario}

@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Delete a scenario"""
    scenario = db.query(MarketScenario).filter_by(id=scenario_id).first()
    if scenario:
        db.delete(scenario)
        db.commit()
    return {"success": True}

@router.post("/scenarios/{scenario_id}/activate")
async def activate_scenario(
    scenario_id: int,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Activate a scenario"""
    from ...services.scenario_manager import get_scenario_manager
    
    manager = get_scenario_manager()
    scenario = manager.apply_scenario(scenario_id, db)
    return {"success": True, "scenario": scenario}

@router.post("/scenarios/deactivate")
async def deactivate_scenario(
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Deactivate current scenario"""
    from ...services.scenario_manager import get_scenario_manager
    
    manager = get_scenario_manager()
    manager.stop_scenario(db)
    return {"success": True}
```

**Register in main.py:**
```python
from app.api.endpoints import admin_scenarios
app.include_router(admin_scenarios.router, prefix="/api/admin", tags=["admin-scenarios"])
```

---

### Task 1.4: Tạo Admin UI cho Scenarios (1.5 hours)
**File:** `Admin-app/src/views/MarketScenarios.vue`

```vue
<template>
  <div class="market-scenarios p-6">
    <h1 class="text-3xl font-bold mb-6">Market Scenarios</h1>
    
    <!-- Create Scenario Button -->
    <button @click="showCreateModal = true" class="btn-primary mb-6">
      Create New Scenario
    </button>
    
    <!-- Scenarios List -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="scenario in scenarios" :key="scenario.id" 
           class="scenario-card bg-slate-800 p-6 rounded-lg">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-semibold">{{ scenario.name }}</h3>
            <span class="text-sm text-gray-400">{{ scenario.scenario_type }}</span>
          </div>
          <span v-if="scenario.is_active" class="badge-active">Active</span>
        </div>
        
        <p class="text-gray-300 mb-4">{{ scenario.description }}</p>
        
        <div class="config-preview mb-4">
          <div class="flex justify-between text-sm">
            <span>Trend:</span>
            <span>{{ scenario.config.trend }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span>Volatility:</span>
            <span>{{ (scenario.config.volatility * 100).toFixed(1) }}%</span>
          </div>
          <div class="flex justify-between text-sm">
            <span>Volume:</span>
            <span>{{ scenario.config.volume_multiplier }}x</span>
          </div>
        </div>
        
        <div class="flex gap-2">
          <button v-if="!scenario.is_active" 
                  @click="activateScenario(scenario.id)"
                  class="btn-success flex-1">
            Activate
          </button>
          <button v-else 
                  @click="deactivateScenario()"
                  class="btn-warning flex-1">
            Deactivate
          </button>
          <button @click="editScenario(scenario)" class="btn-secondary">
            Edit
          </button>
          <button @click="deleteScenario(scenario.id)" class="btn-danger">
            Delete
          </button>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Modal -->
    <ScenarioModal 
      v-if="showCreateModal"
      :scenario="editingScenario"
      @save="handleSaveScenario"
      @close="showCreateModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import toastService from '../services/toast'
import ScenarioModal from '../components/scenarios/ScenarioModal.vue'

const scenarios = ref([])
const showCreateModal = ref(false)
const editingScenario = ref(null)

async function loadScenarios() {
  try {
    const response = await api.get('/api/admin/scenarios')
    scenarios.value = response.data.scenarios
  } catch (error) {
    toastService.error('Failed to load scenarios')
  }
}

async function activateScenario(id) {
  try {
    await api.post(`/api/admin/scenarios/${id}/activate`)
    toastService.success('Scenario activated')
    await loadScenarios()
  } catch (error) {
    toastService.error('Failed to activate scenario')
  }
}

async function deactivateScenario() {
  try {
    await api.post('/api/admin/scenarios/deactivate')
    toastService.success('Scenario deactivated')
    await loadScenarios()
  } catch (error) {
    toastService.error('Failed to deactivate scenario')
  }
}

async function deleteScenario(id) {
  if (!confirm('Are you sure?')) return
  
  try {
    await api.delete(`/api/admin/scenarios/${id}`)
    toastService.success('Scenario deleted')
    await loadScenarios()
  } catch (error) {
    toastService.error('Failed to delete scenario')
  }
}

function editScenario(scenario) {
  editingScenario.value = scenario
  showCreateModal.value = true
}

async function handleSaveScenario(data) {
  try {
    if (data.id) {
      await api.put(`/api/admin/scenarios/${data.id}`, data)
    } else {
      await api.post('/api/admin/scenarios', data)
    }
    toastService.success('Scenario saved')
    showCreateModal.value = false
    editingScenario.value = null
    await loadScenarios()
  } catch (error) {
    toastService.error('Failed to save scenario')
  }
}

onMounted(() => {
  loadScenarios()
})
</script>
```

**Component:** `Admin-app/src/components/scenarios/ScenarioModal.vue`

```vue
<template>
  <div class="modal-overlay">
    <div class="modal-content max-w-2xl">
      <h2 class="text-2xl font-bold mb-6">
        {{ scenario ? 'Edit' : 'Create' }} Scenario
      </h2>
      
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Name</label>
          <input v-model="form.name" required class="form-input" />
        </div>
        
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" class="form-input" rows="3"></textarea>
        </div>
        
        <div class="form-group">
          <label>Type</label>
          <select v-model="form.scenario_type" required class="form-input">
            <option value="bull">Bull Market</option>
            <option value="bear">Bear Market</option>
            <option value="volatile">Volatile</option>
            <option value="sideways">Sideways</option>
          </select>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="form-group">
            <label>Trend</label>
            <select v-model="form.config.trend" class="form-input">
              <option value="up">Up</option>
              <option value="down">Down</option>
              <option value="sideways">Sideways</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Volatility (%)</label>
            <input v-model.number="volatilityPercent" type="number" 
                   min="0.1" max="10" step="0.1" class="form-input" />
          </div>
          
          <div class="form-group">
            <label>Volume Multiplier</label>
            <input v-model.number="form.config.volume_multiplier" 
                   type="number" min="0.1" max="10" step="0.1" class="form-input" />
          </div>
          
          <div class="form-group">
            <label>Price Change/Interval</label>
            <input v-model.number="form.config.price_change_per_interval" 
                   type="number" min="0.0001" max="0.01" step="0.0001" class="form-input" />
          </div>
        </div>
        
        <div class="flex gap-4 mt-6">
          <button type="submit" class="btn-primary flex-1">Save</button>
          <button type="button" @click="$emit('close')" class="btn-secondary flex-1">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  scenario: Object
})

const emit = defineEmits(['save', 'close'])

const form = ref({
  name: '',
  description: '',
  scenario_type: 'bull',
  config: {
    trend: 'up',
    volatility: 0.005,
    volume_multiplier: 1.0,
    price_change_per_interval: 0.001
  }
})

const volatilityPercent = computed({
  get: () => (form.value.config.volatility * 100).toFixed(1),
  set: (val) => { form.value.config.volatility = parseFloat(val) / 100 }
})

watch(() => props.scenario, (newVal) => {
  if (newVal) {
    form.value = { ...newVal }
  }
}, { immediate: true })

function handleSubmit() {
  emit('save', form.value)
}
</script>
```

---

## PHASE 2: SIMULATION CONTROL UI (3 hours)

### Task 2.1: Tạo Simulation Control Endpoints (1 hour)
**File:** `backend/app/api/endpoints/admin_simulation.py`

```python
router = APIRouter(tags=["admin-simulation"])

@router.get("/simulation/status")
async def get_simulation_status(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Get current simulation status"""
    from ...services.trade_broadcaster import get_trade_broadcaster
    from ...services.scenario_manager import get_scenario_manager
    
    broadcaster = get_trade_broadcaster()
    scenario_mgr = get_scenario_manager()
    
    return {
        "is_running": broadcaster.is_running,
        "current_scenario": scenario_mgr.current_scenario,
        "symbols": broadcaster.symbols,
        "current_prices": broadcaster.current_prices,
        "interval_seconds": 2.0,  # From broadcaster config
        "uptime_seconds": calculate_uptime(broadcaster)
    }

@router.post("/simulation/start")
async def start_simulation(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Start market data simulation"""
    from ...services.trade_broadcaster import get_trade_broadcaster
    
    broadcaster = get_trade_broadcaster()
    await broadcaster.start(interval_seconds=2.0)
    return {"success": True, "message": "Simulation started"}

@router.post("/simulation/stop")
async def stop_simulation(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Stop market data simulation"""
    from ...services.trade_broadcaster import get_trade_broadcaster
    
    broadcaster = get_trade_broadcaster()
    await broadcaster.stop()
    return {"success": True, "message": "Simulation stopped"}

@router.post("/simulation/restart")
async def restart_simulation(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Restart simulation"""
    from ...services.trade_broadcaster import get_trade_broadcaster
    
    broadcaster = get_trade_broadcaster()
    await broadcaster.stop()
    await broadcaster.start(interval_seconds=2.0)
    return {"success": True, "message": "Simulation restarted"}

@router.put("/simulation/config")
async def update_simulation_config(
    config: SimulationConfigRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Update simulation configuration"""
    from ...services.trade_broadcaster import get_trade_broadcaster
    
    broadcaster = get_trade_broadcaster()
    
    if config.interval_seconds:
        # Restart with new interval
        was_running = broadcaster.is_running
        await broadcaster.stop()
        if was_running:
            await broadcaster.start(interval_seconds=config.interval_seconds)
    
    if config.symbols:
        broadcaster.symbols = config.symbols
        
    return {"success": True, "config": config}

@router.post("/simulation/reset-prices")
async def reset_prices(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Reset prices to base values"""
    from ...services.trade_broadcaster import get_trade_broadcaster
    
    broadcaster = get_trade_broadcaster()
    broadcaster.current_prices = broadcaster.base_prices.copy()
    return {"success": True, "prices": broadcaster.current_prices}
```

---

### Task 2.2: Tạo Simulation Control UI Component (2 hours)
**File:** `Admin-app/src/components/simulation/SimulationControl.vue`

```vue
<template>
  <div class="simulation-control bg-slate-800 rounded-lg p-6">
    <h2 class="text-2xl font-bold mb-6">Simulation Control</h2>
    
    <!-- Status Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="stat-card">
        <div class="stat-label">Status</div>
        <div class="stat-value">
          <span :class="status.is_running ? 'text-green-400' : 'text-red-400'">
            {{ status.is_running ? 'Running' : 'Stopped' }}
          </span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">Uptime</div>
        <div class="stat-value">{{ formatUptime(status.uptime_seconds) }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">Scenario</div>
        <div class="stat-value text-sm">
          {{ status.current_scenario?.name || 'None' }}
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">Symbols</div>
        <div class="stat-value">{{ status.symbols?.length || 0 }}</div>
      </div>
    </div>
    
    <!-- Control Buttons -->
    <div class="flex gap-4 mb-6">
      <button v-if="!status.is_running" 
              @click="startSimulation"
              class="btn-success">
        ▶ Start
      </button>
      <button v-else 
              @click="stopSimulation"
              class="btn-danger">
        ⏸ Stop
      </button>
      <button @click="restartSimulation" class="btn-warning">
        🔄 Restart
      </button>
      <button @click="resetPrices" class="btn-secondary">
        Reset Prices
      </button>
    </div>
    
    <!-- Current Prices -->
    <div class="prices-grid grid grid-cols-3 gap-4">
      <div v-for="(price, symbol) in status.current_prices" 
           :key="symbol"
           class="price-card bg-slate-700 p-4 rounded">
        <div class="text-sm text-gray-400">{{ symbol }}</div>
        <div class="text-xl font-bold">${{ price.toLocaleString() }}</div>
      </div>
    </div>
    
    <!-- Configuration -->
    <div class="mt-6">
      <h3 class="text-lg font-semibold mb-4">Configuration</h3>
      <div class="grid grid-cols-2 gap-4">
        <div class="form-group">
          <label>Interval (seconds)</label>
          <input v-model.number="config.interval_seconds" 
                 type="number" min="0.5" max="10" step="0.5"
                 class="form-input" />
        </div>
        <div class="form-group">
          <button @click="updateConfig" class="btn-primary mt-6">
            Update Config
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../../services/api'
import toastService from '../../services/toast'

const status = ref({
  is_running: false,
  current_scenario: null,
  symbols: [],
  current_prices: {},
  uptime_seconds: 0,
  interval_seconds: 2.0
})

const config = ref({
  interval_seconds: 2.0
})

let statusInterval = null

async function loadStatus() {
  try {
    const response = await api.get('/api/admin/simulation/status')
    status.value = response.data
  } catch (error) {
    console.error('Failed to load status:', error)
  }
}

async function startSimulation() {
  try {
    await api.post('/api/admin/simulation/start')
    toastService.success('Simulation started')
    await loadStatus()
  } catch (error) {
    toastService.error('Failed to start simulation')
  }
}

async function stopSimulation() {
  try {
    await api.post('/api/admin/simulation/stop')
    toastService.success('Simulation stopped')
    await loadStatus()
  } catch (error) {
    toastService.error('Failed to stop simulation')
  }
}

async function restartSimulation() {
  try {
    await api.post('/api/admin/simulation/restart')
    toastService.success('Simulation restarted')
    await loadStatus()
  } catch (error) {
    toastService.error('Failed to restart simulation')
  }
}

async function resetPrices() {
  try {
    await api.post('/api/admin/simulation/reset-prices')
    toastService.success('Prices reset')
    await loadStatus()
  } catch (error) {
    toastService.error('Failed to reset prices')
  }
}

async function updateConfig() {
  try {
    await api.put('/api/admin/simulation/config', config.value)
    toastService.success('Config updated')
    await loadStatus()
  } catch (error) {
    toastService.error('Failed to update config')
  }
}

function formatUptime(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

onMounted(() => {
  loadStatus()
  statusInterval = setInterval(loadStatus, 5000) // Refresh every 5s
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>
```

---

## PHASE 3: WIN RATE BACKEND LOGIC (2 hours)

### Task 3.1: Tạo WinRateController Service (1 hour)
**File:** `backend/app/services/win_rate_controller.py`

```python
class WinRateController:
    """Service to control user win rate"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def adjust_user_win_rate(
        self,
        user_id: int,
        target_win_rate: float,
        mode: str = "gradual",  # gradual or immediate
        timeframe_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Adjust user's win rate to target
        
        Args:
            user_id: User ID
            target_win_rate: Target win rate (0-100)
            mode: "gradual" or "immediate"
            timeframe_hours: Timeframe for gradual adjustment
        """
        from ..models.portfolio import PortfolioPosition
        from ..models.system import TradingAdjustment
        
        # Get user's open positions
        positions = self.db.query(PortfolioPosition).filter(
            PortfolioPosition.user_id == user_id,
            PortfolioPosition.status == "open"
        ).all()
        
        # Calculate current win rate
        current_win_rate = self._calculate_win_rate(user_id)
        
        # Calculate needed adjustments
        needed_change = target_win_rate - current_win_rate
        
        if mode == "immediate":
            # Adjust positions immediately
            adjusted_positions = []
            for position in positions:
                if needed_change > 0:  # Need more wins
                    # Make position profitable
                    position.unrealized_pnl = abs(position.unrealized_pnl)
                else:  # Need more losses
                    # Make position loss
                    position.unrealized_pnl = -abs(position.unrealized_pnl)
                adjusted_positions.append(position.id)
            
            self.db.commit()
            
        else:  # gradual
            # Plan gradual adjustments over timeframe
            # This would be more complex - adjust a few positions at a time
            pass
        
        # Log adjustment
        adjustment = TradingAdjustment(
            admin_user_id=None,  # Set from request context
            user_id=user_id,
            adjustment_type="win_rate",
            target_value=str(target_win_rate),
            previous_value=str(current_win_rate),
            result=f"Adjusted {len(adjusted_positions)} positions"
        )
        self.db.add(adjustment)
        self.db.commit()
        
        return {
            "user_id": user_id,
            "previous_win_rate": current_win_rate,
            "target_win_rate": target_win_rate,
            "positions_adjusted": len(adjusted_positions),
            "mode": mode
        }
    
    def _calculate_win_rate(self, user_id: int) -> float:
        """Calculate current win rate for user"""
        from ..models.portfolio import PortfolioPosition
        
        positions = self.db.query(PortfolioPosition).filter(
            PortfolioPosition.user_id == user_id,
            PortfolioPosition.status == "closed"
        ).all()
        
        if not positions:
            return 50.0  # Default
        
        winning_positions = [p for p in positions if p.realized_pnl > 0]
        return (len(winning_positions) / len(positions)) * 100
```

---

### Task 3.2: Tạo Win Rate Endpoint (30 min)
**File:** `backend/app/api/endpoints/admin_win_rate.py`

```python
router = APIRouter(tags=["admin-win-rate"])

class WinRateAdjustmentRequest(BaseModel):
    user_id: int
    target_win_rate: float  # 0-100
    mode: str = "gradual"  # gradual or immediate
    timeframe_hours: int = 24

@router.post("/trading-adjustments/win-rate")
async def adjust_win_rate(
    request: WinRateAdjustmentRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Adjust user's win rate"""
    from ...services.win_rate_controller import WinRateController
    
    controller = WinRateController(db)
    result = await controller.adjust_user_win_rate(
        user_id=request.user_id,
        target_win_rate=request.target_win_rate,
        mode=request.mode,
        timeframe_hours=request.timeframe_hours
    )
    
    return {
        "success": True,
        "adjustment": result
    }

@router.get("/users/{user_id}/win-rate")
async def get_user_win_rate(
    user_id: int,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Get user's current win rate"""
    controller = WinRateController(db)
    win_rate = controller._calculate_win_rate(user_id)
    
    return {
        "user_id": user_id,
        "win_rate": win_rate
    }
```

---

### Task 3.3: Update TradeBroadcaster with configurable parameters (30 min)
**File:** `backend/app/services/trade_broadcaster.py`

Add methods:
```python
def set_volatility(self, volatility: float):
    """Set price volatility (0.001 - 0.10)"""
    self.volatility = volatility

def set_trend(self, trend: str):
    """Set market trend: up, down, sideways"""
    self.trend = trend

def set_volume_multiplier(self, multiplier: float):
    """Set volume multiplier (0.1 - 10.0)"""
    self.volume_multiplier = multiplier

def reset_to_defaults(self):
    """Reset all parameters to defaults"""
    self.volatility = 0.005
    self.trend = "sideways"
    self.volume_multiplier = 1.0
```

Update `_generate_trade()` to use these parameters.

---

## PHASE 4: DISPLAY CONTROLS & TESTING (5 hours)

### Task 4.1: Display Configuration Endpoints (1 hour)
**File:** `backend/app/api/endpoints/admin_display.py`

```python
@router.get("/display/config")
async def get_display_config(db: Session = Depends(get_db)):
    """Get display configuration"""
    from ...models.system import SystemSetting
    
    config = db.query(SystemSetting).filter_by(
        key="display_config"
    ).first()
    
    if not config:
        # Default config
        default = {
            "show_mock_indicator": True,
            "mock_opacity": 0.8,
            "highlight_simulated": True,
            "source_badge": True,
            "chart_update_ms": 1000,
            "orderbook_levels": 20
        }
        return {"config": default}
    
    return {"config": config.value}

@router.put("/display/config")
async def update_display_config(
    config: DisplayConfigRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Update display configuration"""
    from ...models.system import SystemSetting
    
    setting = db.query(SystemSetting).filter_by(
        key="display_config"
    ).first()
    
    if not setting:
        setting = SystemSetting(
            key="display_config",
            value=config.dict(),
            is_public=True
        )
        db.add(setting)
    else:
        setting.value = config.dict()
    
    db.commit()
    return {"success": True, "config": config}

@router.post("/display/toggle-source")
async def toggle_data_source(
    source: DataSourceRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Toggle data source between mock/opex/auto"""
    from ...models.system import SystemSetting
    
    setting = db.query(SystemSetting).filter_by(
        key="data_source"
    ).first()
    
    if not setting:
        setting = SystemSetting(
            key="data_source",
            value={"source": source.source},
            is_public=True
        )
        db.add(setting)
    else:
        setting.value = {"source": source.source}
    
    db.commit()
    return {"success": True, "source": source.source}
```

---

### Task 4.2: Integration Testing (2 hours)
**File:** `backend/tests/test_admin_control_integration.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_scenario_crud(client: TestClient, admin_token):
    # Create scenario
    response = client.post(
        "/api/admin/scenarios",
        json={
            "name": "Test Bull Market",
            "scenario_type": "bull",
            "config": {"trend": "up", "volatility": 0.01}
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    scenario_id = response.json()["scenario"]["id"]
    
    # Activate scenario
    response = client.post(
        f"/api/admin/scenarios/{scenario_id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Check status
    response = client.get(
        "/api/admin/simulation/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["current_scenario"] is not None

def test_simulation_control(client: TestClient, admin_token):
    # Start simulation
    response = client.post(
        "/api/admin/simulation/start",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Check running
    response = client.get(
        "/api/admin/simulation/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.json()["is_running"] == True
    
    # Stop simulation
    response = client.post(
        "/api/admin/simulation/stop",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

def test_win_rate_adjustment(client: TestClient, admin_token, test_user):
    response = client.post(
        "/api/admin/trading-adjustments/win-rate",
        json={
            "user_id": test_user.id,
            "target_win_rate": 75.0,
            "mode": "immediate"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
```

---

### Task 4.3: Admin UI Integration Testing (1 hour)
Test các flows:
1. Create scenario → Activate → Verify in UI
2. Start/Stop simulation → Check status updates
3. Adjust win rate → Check positions changed
4. Toggle display source → Verify UI updates

---

### Task 4.4: Documentation & Final Review (1 hour)
Update documentation:
- Admin user guide
- API documentation
- Scenario examples
- Troubleshooting guide

---

## 📊 CHECKLIST HOÀN THÀNH

### Phase 1: Market Scenarios ✅
- [ ] MarketScenario model + migration
- [ ] ScenarioManager service
- [ ] Admin endpoints (CRUD)
- [ ] MarketScenarios.vue + ScenarioModal.vue
- [ ] Test scenario activation

### Phase 2: Simulation Control ✅
- [ ] Simulation control endpoints
- [ ] SimulationControl.vue component
- [ ] Real-time status updates
- [ ] Test start/stop/restart

### Phase 3: Win Rate Logic ✅
- [ ] WinRateController service
- [ ] Win rate endpoint
- [ ] TradeBroadcaster enhancements
- [ ] Test win rate adjustments

### Phase 4: Display & Testing ✅
- [ ] Display config endpoints
- [ ] Integration tests
- [ ] UI integration tests
- [ ] Documentation updates

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành tất cả tasks:
- ✅ Market scenario system hoạt động đầy đủ
- ✅ Admin có thể control simulation real-time
- ✅ Win rate adjustment tự động
- ✅ Display controls flexible
- ✅ Integration tests pass 100%
- ✅ Documentation đầy đủ

**Admin Control Logic: 100% HOÀN THIỆN**

