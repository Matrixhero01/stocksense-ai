"""
StockSense AI - Data Quality Engine

Detects incomplete or suspicious retail data.
The system should surface uncertainty instead of hiding it.
"""

import pandas as pd


def analyze_sales_quality(sales, stores, products):
    """
    Check whether each store/product combination has
    complete daily sales observations across the full
    14-day analysis period.
    """

    latest_date = sales["date"].max()

    # Full 14-day analysis window
    earliest_date = latest_date - pd.Timedelta(days=29)

    expected_dates = pd.date_range(
        start=earliest_date,
        end=latest_date,
        freq="D"
    )

    expected_days = len(expected_dates)

    results = []

    for _, store in stores.iterrows():

        for _, product in products.iterrows():

            store_id = store["store_id"]
            product_id = product["product_id"]

            records = sales[
                (sales["store_id"] == store_id)
                &
                (sales["product_id"] == product_id)
                &
                (sales["date"] >= earliest_date)
                &
                (sales["date"] <= latest_date)
            ]

            observed_dates = set(
                records["date"].dt.normalize()
            )

            missing_dates = [
                date.strftime("%Y-%m-%d")
                for date in expected_dates
                if date not in observed_dates
            ]

            observed_days = len(observed_dates)

            missing_days = len(missing_dates)

            completeness_pct = (
                observed_days / expected_days
            ) * 100

            if missing_days == 0:
                quality = "COMPLETE"

            elif missing_days <= 1:
                quality = "MINOR_GAP"

            else:
                quality = "INCOMPLETE"

            results.append({

                "store_id": store_id,

                "store_name": store["store_name"],

                "product_id": product_id,

                "product_name": product["product_name"],

                "expected_days": expected_days,

                "observed_days": observed_days,

                "missing_days": missing_days,

                "missing_dates": missing_dates,

                "completeness_pct": round(
                    completeness_pct,
                    1
                ),

                "quality": quality,

            })

    return pd.DataFrame(results)


def get_quality_summary(quality_df):
    """Create high-level data quality statistics."""

    return {

        "total_combinations": len(
            quality_df
        ),

        "complete": int(
            (
                quality_df["quality"]
                == "COMPLETE"
            ).sum()
        ),

        "minor_gaps": int(
            (
                quality_df["quality"]
                == "MINOR_GAP"
            ).sum()
        ),

        "incomplete": int(
            (
                quality_df["quality"]
                == "INCOMPLETE"
            ).sum()
        ),

        "total_missing_days": int(
            quality_df["missing_days"].sum()
        ),

    }


if __name__ == "__main__":

    from analytics import load_data

    products, stores, inventory, sales = load_data()

    quality = analyze_sales_quality(
        sales,
        stores,
        products
    )

    summary = get_quality_summary(
        quality
    )

    print(
        "\n========== DATA DETECTIVE ==========\n"
    )

    print(
        f"Store/Product combinations checked: "
        f"{summary['total_combinations']}"
    )

    print(
        f"Complete: "
        f"{summary['complete']}"
    )

    print(
        f"Minor gaps: "
        f"{summary['minor_gaps']}"
    )

    print(
        f"Incomplete: "
        f"{summary['incomplete']}"
    )

    print(
        f"Total missing sales days: "
        f"{summary['total_missing_days']}"
    )

    print(
        "\n---------- Detected Issues ----------\n"
    )

    issues = quality[
        quality["missing_days"] > 0
    ].sort_values(
        "missing_days",
        ascending=False
    )

    if issues.empty:

        print(
            "No missing sales observations detected."
        )

    else:

        for _, row in issues.iterrows():

            print(
                f"{row['store_name']} | "
                f"{row['product_name']}"
            )

            print(
                f"      Expected days: "
                f"{row['expected_days']}"
            )

            print(
                f"      Observed days: "
                f"{row['observed_days']}"
            )

            print(
                f"      Missing days: "
                f"{row['missing_days']}"
            )

            print(
                f"      Missing dates: "
                f"{', '.join(row['missing_dates'])}"
            )

            print(
                f"      Completeness: "
                f"{row['completeness_pct']}%"
            )

            print(
                f"      Data quality: "
                f"{row['quality']}"
            )

            print()