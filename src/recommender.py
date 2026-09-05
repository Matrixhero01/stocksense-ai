"""
StockSense AI - Recommendation Engine

Finds inventory imbalances between stores.

The engine recommends transfers only when:
1. One store has low stock coverage.
2. Another store has significant excess stock.
3. The same product exists at both stores.

All transfer quantities are calculated deterministically.
No logistics costs, lead times, supplier data, or purchase quantities
are invented.
"""

import pandas as pd


SHORTAGE_DAYS = 7
EXCESS_DAYS = 30


def find_transfer_opportunities(metrics):
    """
    Find products that are low at one store while another store
    has enough excess inventory to support a transfer.

    Transfer quantity is calculated using:
        shortage_needed = stock required to reach 7 days
        transferable = stock above 30-day reserve at source

    The final transfer is the smaller of those two values.
    """

    opportunities = []

    for product_id in metrics["product_id"].unique():

        product_rows = metrics[
            metrics["product_id"] == product_id
        ]

        # Destination stores that need inventory.
        shortage_rows = product_rows[
            (product_rows["days_of_stock"] < SHORTAGE_DAYS)
            & (product_rows["average_daily_sales"] > 0)
        ]

        # Source stores with significant excess.
        excess_rows = product_rows[
            (product_rows["days_of_stock"] > EXCESS_DAYS)
            & (product_rows["average_daily_sales"] > 0)
        ]

        for _, shortage in shortage_rows.iterrows():

            for _, excess in excess_rows.iterrows():

                # Never transfer within the same store.
                if shortage["store_id"] == excess["store_id"]:
                    continue

                # -------------------------------------------------
                # Destination calculation
                # -------------------------------------------------

                shortage_target = (
                    shortage["average_daily_sales"]
                    * SHORTAGE_DAYS
                )

                shortage_needed = max(
                    0,
                    shortage_target - shortage["current_stock"]
                )

                # -------------------------------------------------
                # Source calculation
                # -------------------------------------------------

                excess_reserve = (
                    excess["average_daily_sales"]
                    * EXCESS_DAYS
                )

                transferable = max(
                    0,
                    excess["current_stock"] - excess_reserve
                )

                # -------------------------------------------------
                # Conservative transfer quantity
                # -------------------------------------------------

                transfer_qty = min(
                    shortage_needed,
                    transferable
                )

                if transfer_qty <= 0:
                    continue

                transfer_qty = int(transfer_qty)

                # Recalculate destination coverage.
                before_days = float(
                    shortage["days_of_stock"]
                )

                after_stock = (
                    shortage["current_stock"]
                    + transfer_qty
                )

                after_days = (
                    after_stock
                    / shortage["average_daily_sales"]
                )

                # Recalculate source coverage after transfer.
                source_before_days = float(
                    excess["days_of_stock"]
                )

                source_after_stock = (
                    excess["current_stock"]
                    - transfer_qty
                )

                source_after_days = (
                    source_after_stock
                    / excess["average_daily_sales"]
                )

                opportunities.append({
                    "product_id": product_id,
                    "product_name": shortage["product_name"],

                    "from_store": excess["store_name"],
                    "to_store": shortage["store_name"],

                    "from_stock": int(
                        excess["current_stock"]
                    ),
                    "to_stock": int(
                        shortage["current_stock"]
                    ),

                    "transfer_units": transfer_qty,

                    "before_days": round(
                        before_days,
                        2
                    ),
                    "after_days": round(
                        after_days,
                        2
                    ),

                    "source_days": round(
                        source_before_days,
                        2
                    ),
                    "source_after_days": round(
                        source_after_days,
                        2
                    ),

                    # Explainable reason for the recommendation.
                    "reason": (
                        f"{shortage['store_name']} has "
                        f"{before_days:.1f} days of stock, while "
                        f"{excess['store_name']} has "
                        f"{source_before_days:.1f} days."
                    ),

                    # These are assumptions, not invented business facts.
                    "assumptions": [
                        "Demand remains near the observed average.",
                        "Inventory can be transferred between these stores.",
                        "No lead-time, MOQ, open-PO, or logistics constraint was provided."
                    ]
                })

    return opportunities


def rank_transfer_opportunities(opportunities):
    """
    Rank transfer opportunities by urgency.

    Lower destination coverage = higher priority.
    Larger transfer opportunity = secondary priority.
    """

    return sorted(
        opportunities,
        key=lambda x: (
            x["before_days"],
            -x["transfer_units"]
        )
    )


if __name__ == "__main__":

    from src.analytics import (
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
                f"      Destination after: "
                f"{item['after_days']} days"
            )

            print(
                f"      Source after: "
                f"{item['source_after_days']} days"
            )

            print(
                f"      Why: {item['reason']}"
            )

            print()