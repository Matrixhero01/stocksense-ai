"""
StockSense AI - Decision / Risk Engine

This module converts factual analytics into prioritized decisions.

Important:
- No Gemini calls here.
- No invented numbers.
- All scores are derived from retailer data.
"""


import pandas as pd


def calculate_attention_score(row):
    """
    Calculate a deterministic 0-100 attention score.

    Higher score = more urgent for the store manager.
    """

    score = 0

    # ---------------------------------------------------------
    # 1. Stock coverage risk
    # ---------------------------------------------------------

    days = row["days_of_stock"]

    if days < 2:
        score += 45
    elif days < 4:
        score += 35
    elif days < 7:
        score += 25
    elif days < 14:
        score += 10

    # ---------------------------------------------------------
    # 2. Demand trend
    # ---------------------------------------------------------

    trend = row["sales_trend_pct"]

    if trend >= 30:
        score += 25
    elif trend >= 15:
        score += 15
    elif trend >= 5:
        score += 8
    elif trend <= -30:
        score += 15
    elif trend <= -15:
        score += 8

    # ---------------------------------------------------------
    # 3. Revenue impact
    # ---------------------------------------------------------

    daily_revenue = (
        row["average_daily_sales"] * row["unit_price"]
    )

    if daily_revenue >= 500:
        score += 15
    elif daily_revenue >= 250:
        score += 10
    elif daily_revenue >= 100:
        score += 5

    # ---------------------------------------------------------
    # 4. Data confidence
    # ---------------------------------------------------------

    confidence = row["data_confidence"]

    if confidence >= 90:
        score += 10
    elif confidence >= 70:
        score += 5

    # Keep score within 0-100.
    return min(int(score), 100)


def classify_priority(score):
    """Convert numeric score into a human-readable priority."""

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "WATCH"

    return "LOW"


def generate_reason(row):
    """
    Generate a factual explanation for why an item needs attention.

    The explanation uses only calculated retailer data.
    """

    reasons = []

    days = row["days_of_stock"]
    trend = row["sales_trend_pct"]

    if days < 4:
        reasons.append(
            f"only {days:.1f} days of stock remaining"
        )

    elif days < 7:
        reasons.append(
            f"only {days:.1f} days of stock coverage"
        )

    if trend >= 15:
        reasons.append(
            f"sales are up {trend:.1f}% versus the previous period"
        )

    elif trend <= -15:
        reasons.append(
            f"sales are down {abs(trend):.1f}% versus the previous period"
        )

    if not reasons:
        reasons.append("inventory and demand require monitoring")

    return "; ".join(reasons)


def build_decision(row):
    """
    Create one structured decision object.
    """

    score = calculate_attention_score(row)

    return {
        "store_id": row["store_id"],
        "store_name": row["store_name"],
        "product_id": row["product_id"],
        "product_name": row["product_name"],
        "attention_score": score,
        "priority": classify_priority(score),
        "reason": generate_reason(row),
        "current_stock": int(row["current_stock"]),
        "average_daily_sales": round(
            row["average_daily_sales"], 2
        ),
        "days_of_stock": round(
            row["days_of_stock"], 2
        ),
        "sales_trend_pct": round(
            row["sales_trend_pct"], 2
        ),
        "data_confidence": round(
            row["data_confidence"], 1
        ),
    }


def generate_decisions(metrics):
    """
    Generate and rank decisions for all inventory items.
    """

    decisions = []

    for _, row in metrics.iterrows():
        decision = build_decision(row)
        decisions.append(decision)

    decisions.sort(
        key=lambda x: x["attention_score"],
        reverse=True,
    )

    return decisions


if __name__ == "__main__":
    from analytics import load_data, calculate_product_metrics

    products, stores, inventory, sales = load_data()

    metrics = calculate_product_metrics(
        products,
        stores,
        inventory,
        sales,
    )

    decisions = generate_decisions(metrics)

    print("\n========== WHY TODAY? ==========\n")

    for decision in decisions[:10]:
        print(
            f"{decision['attention_score']:>3}/100 | "
            f"{decision['priority']:<8} | "
            f"{decision['store_name']} | "
            f"{decision['product_name']}"
        )

        print(
            f"      Stock: {decision['current_stock']} units | "
            f"Coverage: {decision['days_of_stock']} days | "
            f"Trend: {decision['sales_trend_pct']}%"
        )

        print(
            f"      Why: {decision['reason']}"
        )

        print(
            f"      Data confidence: "
            f"{decision['data_confidence']}%"
        )

        print()