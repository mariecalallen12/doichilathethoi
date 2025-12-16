import asyncio

import pytest

from app.schemas.trading_simulator import TradingSimScenario, TradingSimScenarioUpdate
from app.services.trading_data_simulator import TradingDataSimulator


@pytest.mark.asyncio
async def test_snapshot_has_core_sections():
    sim = TradingDataSimulator(symbols=["TESTUSDT"])
    await sim.start(interval_seconds=0.01)
    await asyncio.sleep(0.05)
    snapshot = await sim.get_snapshot()
    await sim.stop()

    assert "TESTUSDT" in snapshot.prices
    assert "TESTUSDT" in snapshot.orderbooks
    assert "TESTUSDT" in snapshot.trades
    assert "TESTUSDT" in snapshot.positions
    assert snapshot.latency_ms > 0


@pytest.mark.asyncio
async def test_update_scenarios_applies_changes():
    sim = TradingDataSimulator(symbols=["BTCUSDT"])
    await sim.update_scenarios(
        TradingSimScenarioUpdate(
            scenarios=[
                TradingSimScenario(
                    symbol="BTCUSDT",
                    drift=0.001,
                    volatility=0.003,
                    spread_bps=5,
                    depth=8,
                )
            ]
        )
    )

    updated = await sim.get_scenarios()
    assert any(s.symbol == "BTCUSDT" and s.spread_bps == 5 for s in updated)

