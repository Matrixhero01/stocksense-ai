"""
StockSense AI - Core Retail Analytics

This module performs deterministic calculations on sales and inventory data.
Gemini is NOT used here. All numbers shown to the user must come from these
calculations.
"""

from pathlib import Path

import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_data():
    """Load all retailer datasets."""

    products = pd.read_csv(DATA_DIR / "products.csv")
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    sales = pd.read_csv(DATA_DIR / "sales.csv")

    sales["date"] = pd.to_datetime(sales["date"])

    return products, stores, inventory, sales


def calculate_product_metrics(
    products: pd.DataFrame,
    stores: pd.DataFrame,
    inventory: pd.DataFrame,
    sales: pd.DataFrame,
):
    """
    Calculate inventory and sales metrics for every product/store combination.

    Returns a dataframe containing factual metrics that can later be used by
    the risk engine and Gemini explanation layer.
    """

    # Determine the latest date available in the dataset.
    latest_date = sales["date"].max()

    # Last 7 days
    recent_start = latest_date - pd.Timedelta(days=6)

    # Previous 7 days
    previous_start = latest_date - pd.Timedelta(days=13)
    previous_end = latest_date - pd.Timedelta(days=7)

    recent_sales = sales[
        (sales["date"] >= recent_start)
        & (sales["date"] <= latest_date)
    ]

    previous_sales = sales[
        (sales["date"] >= previous_start)
        & (sales["date"] <= previous_end)
    ]

    # Aggregate recent sales.
    recent_summary = (
        recent_sales.groupby(["store_id", "product_id"])
        .agg(
            recent_units=("units_sold", "sum"),
            valid_sales_days=("date", "nunique"),
        )
        .reset_index()
    )

    # Aggregate previous-period sales.
    previous_summary = (
        previous_sales.groupby(["store_id", "product_id"])
        .agg(previous_units=("units_sold", "sum"))
        .reset_index()
    )

    # Start from inventory so products with zero sales are still included.
    result = inventory.copy()

    result = result.merge(
        recent_summary,
        on=["store_id", "product_id"],
        how="left",
    )

    result = result.merge(
        previous_summary,
        on=["store_id", "product_id"],
        how="left",
    )

    result = result.merge(
        products,
        on="product_id",
        how="left",
    )

    result = result.merge(
        stores,
        on="store_id",
        how="left",
    )

    # Missing sales are treated as zero for calculation purposes.
    result["recent_units"] = result["recent_units"].fillna(0)
    result["previous_units"] = result["previous_units"].fillna(0)
    result["valid_sales_days"] = result["valid_sales_days"].fillna(0)

    # Average daily sales.
    result["average_daily_sales"] = (
        result["recent_units"] / result["valid_sales_days"].replace(0, pd.NA)
    )

    result["average_daily_sales"] = (
        result["average_daily_sales"]
        .fillna(0)
        .astype(float)
    )

    # Days of inventory remaining.
    result["days_of_stock"] = 0.0

    positive_demand = result["average_daily_sales"] > 0

    result.loc[positive_demand, "days_of_stock"] = (
        result.loc[positive_demand, "current_stock"]
        / result.loc[positive_demand, "average_daily_sales"]
    )

    # Sales trend.
    result["sales_trend_pct"] = 0.0

    previous_positive = result["previous_units"] > 0

    result.loc[previous_positive, "sales_trend_pct"] = (
        (
            result.loc[previous_positive, "recent_units"]
            - result.loc[previous_positive, "previous_units"]
        )
        / result.loc[previous_positive, "previous_units"]
    ) * 100

    # Basic inventory status.
    result["status"] = "HEALTHY"

    result.loc[
        result["days_of_stock"].between(0, 7, inclusive="both"),
        "status",
    ] = "WATCH"

    result.loc[
        result["days_of_stock"] < 4,
        "status",
    ] = "CRITICAL"

    # Very high coverage = possible overstock.
    result.loc[
        result["days_of_stock"] > 30,
        "status",
    ] = "OVERSTOCK"

    # Products with no demand need a special status.
    result.loc[
        result["average_daily_sales"] == 0,
        "status",
    ] = "NO_DEMAND"

    # Data confidence.
    result["data_confidence"] = (
        result["valid_sales_days"] / 7 * 100
    ).clip(upper=100)

    return result


def get_dashboard_summary(metrics: pd.DataFrame):
    """Return high-level numbers for the dashboard."""

    return {
        "total_products": int(metrics["product_id"].nunique()),
        "total_inventory": int(metrics["current_stock"].sum()),
        "critical": int((metrics["status"] == "CRITICAL").sum()),
        "watch": int((metrics["status"] == "WATCH").sum()),
        "overstock": int((metrics["status"] == "OVERSTOCK").sum()),
        "healthy": int((metrics["status"] == "HEALTHY").sum()),
    }


if __name__ == "__main__":
    products, stores, inventory, sales = load_data()

    metrics = calculate_product_metrics(
        products,
        stores,
        inventory,
        sales,
    )

    print("\n========== STOCKSENSE ANALYTICS ==========\n")

    print(
        metrics[
            [
                "store_name",
                "product_name",
                "current_stock",
                "average_daily_sales",
                "days_of_stock",
                "sales_trend_pct",
                "status",
            ]
        ].to_string(index=False)
    )

    print("\n========== DASHBOARD SUMMARY ==========\n")

    summary = get_dashboard_summary(metrics)

    for key, value in summary.items():
        print(f"{key}: {value}")