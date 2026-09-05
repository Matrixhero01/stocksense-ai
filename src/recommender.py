"""
StockSense AI - Recommendation Engine

Finds inventory imbalances between stores.

The engine recommends transfers only when:
1. One store has low stock coverage.
2. Another store has significant excess stock.
3. The same product exists at both stores.

No logistics costs, lead times, or purchase quantities are invented.
"""

import pandas as pd


def find_transfer_opportunities(metrics):
    """
    Find products that are critically low at one store
    while another store has substantial excess.
    """

    opportunities = []

    for product_id in metrics["product_id"].unique():

        product_rows = metrics[
            metrics["product_id"] == product_id
        ]

        shortage_rows = product_rows[
            product_rows["days_of_stock"] < 7
        ]

        excess_rows = product_rows[
            product_rows["days_of_stock"] > 30
        ]

        for _, shortage in shortage_rows.iterrows():

            for _, excess in excess_rows.iterrows():

                # Do not transfer within the same store.
                if shortage["store_id"] == excess["store_id"]:
                    continue

                # Conservative transfer quantity:
                # bring the shortage store toward 7 days,
                # but do not exceed the excess store's stock
                # beyond its 30-day threshold.
                shortage_target = (
                    shortage["average_daily_sales"] * 7
                )

                shortage_needed = max(
                    0,
                    shortage_target - shortage["current_stock"]
                )

                excess_reserve = (
                    excess["average_daily_sales"] * 30
                )

                transferable = max(
                    0,
                    excess["current_stock"] - excess_reserve
                )

                transfer_qty = min(
                    shortage_needed,
                    transferable
                )

                if transfer_qty <= 0:
                    continue

                before_days = shortage["days_of_stock"]

                after_stock = (
                    shortage["current_stock"] + transfer_qty
                )

                if shortage["average_daily_sales"] > 0:
                    after_days = (
                        after_stock
                        / shortage["average_daily_sales"]
                    )
                else:
                    after_days = None

                opportunities.append({
                    "product_id": product_id,
                    "product_name": shortage["product_name"],
                    "from_store": excess["store_name"],
                    "to_store": shortage["store_name"],
                    "from_stock": int(excess["current_stock"]),
                    "to_stock": int(shortage["current_stock"]),
                    "transfer_units": int(transfer_qty),
                    "before_days": round(before_days, 2),
                    "after_days": (
                        round(after_days, 2)
                        if after_days is not None
                        else None
                    ),
                    "source_days": round(
                        excess["days_of_stock"], 2
                    ),
                })

    return opportunities


def rank_transfer_opportunities(opportunities):
    """
    Rank opportunities by urgency.
    """

    return sorted(
        opportunities,
        key=lambda x: (
            x["before_days"],
            -x["transfer_units"]
        )
    )


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

    opportunities = find_transfer_opportunities(
        metrics
    )

    opportunities = rank_transfer_opportunities(
        opportunities
    )

    print("\n========== SMART TRANSFER ENGINE ==========\n")

    if not opportunities:

        print("No transfer opportunities detected.")

    else:

        for item in opportunities:

            print(
                f"{item['product_name']}"
            )

            print(
                f"      From: {item['from_store']} "
                f"({item['from_stock']} units, "
                f"{item['source_days']} days coverage)"
            )

            print(
                f"      To: {item['to_store']} "
                f"({item['to_stock']} units, "
                f"{item['before_days']} days coverage)"
            )

            print(
                f"      Suggested transfer: "
                f"{item['transfer_units']} units"
            )

            print(
                f"      Destination coverage after transfer: "
                f"{item['after_days']} days"
            )

            print()