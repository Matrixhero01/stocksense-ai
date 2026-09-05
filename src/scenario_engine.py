"""
StockSense AI - Scenario Engine

Deterministic forecasting and what-if calculations.
No Gemini calculations are performed here.
"""

import math
import pandas as pd


def calculate_depletion_forecast(row, demand_change_pct=0):
    """
    Estimate inventory depletion under a demand scenario.

    demand_change_pct:
        0   = current demand
        20  = demand increases by 20%
        -20 = demand decreases by 20%
    """

    current_stock = float(row["current_stock"])
    current_demand = float(row["average_daily_sales"])

    # Apply scenario demand change.
    scenario_demand = current_demand * (
        1 + demand_change_pct / 100
    )

    if scenario_demand <= 0:
        return {
            "current_stock": int(current_stock),
            "scenario_demand": 0,
            "days_remaining": None,
            "stock_out_risk": "LOW",
            "message": "No positive demand detected."
        }

    days_remaining = current_stock / scenario_demand

    if days_remaining <= 3:
        risk = "CRITICAL"
    elif days_remaining <= 7:
        risk = "HIGH"
    elif days_remaining <= 14:
        risk = "WATCH"
    else:
        risk = "LOW"

    return {
        "current_stock": int(current_stock),
        "scenario_demand": round(scenario_demand, 2),
        "days_remaining": round(days_remaining, 2),
        "stock_out_risk": risk,
        "message": (
            f"At {round(scenario_demand, 2)} units/day, "
            f"inventory may last approximately "
            f"{round(days_remaining, 1)} days."
        )
    }


def simulate_demand(row, demand_change_pct):
    """
    Run a what-if demand simulation.
    """

    result = calculate_depletion_forecast(
        row,
        demand_change_pct=demand_change_pct
    )

    return {
        "product_name": row["product_name"],
        "store_name": row["store_name"],
        "demand_change_pct": demand_change_pct,
        **result
    }


def build_scenario_table(row):
    """
    Generate several demand scenarios for one product/store.
    """

    scenarios = [-30, -10, 0, 10, 20, 30, 50]

    results = []

    for change in scenarios:
        results.append(
            simulate_demand(row, change)
        )

    return pd.DataFrame(results)


def get_depletion_forecasts(metrics):
    """
    Generate the current-demand depletion forecast
    for every product/store combination.
    """

    forecasts = []

    for _, row in metrics.iterrows():

        result = calculate_depletion_forecast(row)

        forecasts.append({
            "store_id": row["store_id"],
            "store_name": row["store_name"],
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "current_stock": int(row["current_stock"]),
            "average_daily_sales": round(
                row["average_daily_sales"], 2
            ),
            "days_remaining": result["days_remaining"],
            "stock_out_risk": result["stock_out_risk"],
        })

    return forecasts


if __name__ == "__main__":

    from analytics import (
        load_data,
        calculate_product_metrics
    )

    products, stores, inventory, sales = load_data()

    metrics = calculate_product_metrics(
        products,
        stores,
        inventory,
        sales
    )

    # ---------------------------------------------------------
    # Find the most urgent depletion risks
    # ---------------------------------------------------------

    forecasts = get_depletion_forecasts(metrics)

    forecasts = [
        x for x in forecasts
        if x["days_remaining"] is not None
    ]

    forecasts.sort(
        key=lambda x: x["days_remaining"]
    )

    print("\n========== IF I DO NOTHING? ==========\n")

    for item in forecasts[:10]:

        print(
            f"{item['store_name']} | "
            f"{item['product_name']}"
        )

        print(
            f"      Stock: {item['current_stock']} units"
        )

        print(
            f"      Demand: "
            f"{item['average_daily_sales']} units/day"
        )

        print(
            f"      Estimated stock remaining: "
            f"{item['days_remaining']} days"
        )

        print(
            f"      Risk: {item['stock_out_risk']}"
        )

        print()

    # ---------------------------------------------------------
    # Demonstrate What-If simulation using the highest-risk item
    # ---------------------------------------------------------

    print("\n========== WHAT-IF SIMULATION ==========\n")

    highest_risk = forecasts[0]

    matching_row = metrics[
        (metrics["store_id"] == highest_risk["store_id"])
        &
        (metrics["product_id"] == highest_risk["product_id"])
    ].iloc[0]

    scenario_table = build_scenario_table(
        matching_row
    )

    print(
        scenario_table[
            [
                "demand_change_pct",
                "scenario_demand",
                "days_remaining",
                "stock_out_risk"
            ]
        ].to_string(index=False)
    )