"""
StockSense AI - SQLite Database Layer

Loads the demo CSV data into a local SQLite database.
The database is created automatically when the application starts.
"""

from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "stocksense.db"


def get_connection():
    """Create a connection to the local SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """
    Create the SQLite database and load the current CSV data.

    CSV files remain the source dataset for the hackathon demo.
    SQLite provides the application's structured data layer.
    """
    DATA_DIR.mkdir(exist_ok=True)

    products = pd.read_csv(DATA_DIR / "products.csv")
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    sales = pd.read_csv(DATA_DIR / "sales.csv")

    with get_connection() as conn:
        products.to_sql("products", conn, if_exists="replace", index=False)
        stores.to_sql("stores", conn, if_exists="replace", index=False)
        inventory.to_sql("inventory", conn, if_exists="replace", index=False)
        sales.to_sql("sales", conn, if_exists="replace", index=False)

    return DB_PATH


def load_data_from_database():
    """Load all retail data from SQLite."""
    with get_connection() as conn:
        products = pd.read_sql_query(
            "SELECT * FROM products",
            conn
        )

        stores = pd.read_sql_query(
            "SELECT * FROM stores",
            conn
        )

        inventory = pd.read_sql_query(
            "SELECT * FROM inventory",
            conn
        )

        sales = pd.read_sql_query(
            "SELECT * FROM sales",
            conn
        )

    sales["date"] = pd.to_datetime(sales["date"])

    return products, stores, inventory, sales


if __name__ == "__main__":
    path = initialize_database()
    print(f"Database created: {path}")

    products, stores, inventory, sales = load_data_from_database()

    print(f"Products: {len(products)}")
    print(f"Stores: {len(stores)}")
    print(f"Inventory records: {len(inventory)}")
    print(f"Sales records: {len(sales)}")