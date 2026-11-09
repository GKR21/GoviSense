"""
Market Adoption Simulation Runner (0%, 30%, 60% Farmer Adoption)
Team DARKBITE · ModelX 2.0 Phase 1
Demonstrates system stabilization when farmers coordinate with GoviSense.
"""

import json
from pathlib import Path
from govisense.simulation.agent_sim import MarketAdoptionSimulator
from govisense.config import settings

def run_market_adoption_simulation():
    sim = MarketAdoptionSimulator()
    results = {}
    
    # 1. Big Onion Simulation (Yala peak harvest in Anuradhapura/Matale)
    bo_res = sim.simulate(
        crop="big_onion",
        season_demand_mt=26667.0,
        uncoordinated_supply_mt=46000.0,
        yield_mid=15.5,
        fair_floor_rs_kg=120.0,
        base_unregulated_price_rs_kg=75.0,
    )
    results["big_onion"] = bo_res

    # 2. Chilli Simulation (Maha harvest)
    chilli_res = sim.simulate(
        crop="chilli",
        season_demand_mt=14500.0,
        uncoordinated_supply_mt=22000.0,
        yield_mid=5.2,
        fair_floor_rs_kg=350.0,
        base_unregulated_price_rs_kg=220.0,
    )
    results["chilli"] = chilli_res

    out_path = Path("data/interim/market_adoption_simulation.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("=== GoviSense Market Adoption Simulation (0%, 30%, 60%) ===")
    for crop, data in results.items():
        print(f"\n--- Crop: {crop.upper()} ---")
        for sc in data["scenarios"]:
            print(
                f"  [{sc['adoption_rate_pct']}% Adoption] "
                f"Supply: {sc['total_supply_mt']:,.0f} MT | "
                f"SPI: {sc['spi_score']:+.2f} ({sc['spi_label']}) | "
                f"Farmgate: Rs {sc['farmgate_price_rs_kg']:.1f}/kg | "
                f"Crash Risk: {sc['price_crash_risk_pct']:.1f}% | "
                f"Economic Loss Avoided: Rs {sc.get('economic_loss_avoided_rs', 0):,.0f}"
            )
    return results

if __name__ == "__main__":
    run_market_adoption_simulation()
