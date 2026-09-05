from flask import Flask, jsonify, render_template
from src.gemini import ask_stock_sense
from src.analytics import load_data, calculate_product_metrics, get_dashboard_summary
from src.risk_engine import generate_decisions
from src.scenario_engine import get_depletion_forecasts
from src.data_quality import analyze_sales_quality, get_quality_summary
from src.recommender import find_transfer_opportunities, rank_transfer_opportunities


app = Flask(__name__)


# ---------------------------------------------------------
# Load retailer data
# ---------------------------------------------------------

products, stores, inventory, sales = load_data()

metrics = calculate_product_metrics(
    products,
    stores,
    inventory,
    sales
)


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")
  

# ---------------------------------------------------------
# Dashboard API
# ---------------------------------------------------------

@app.route("/api/dashboard")
def dashboard():

    summary = get_dashboard_summary(metrics)

    return jsonify(summary)


# ---------------------------------------------------------
# Why Today?
# ---------------------------------------------------------

@app.route("/api/decisions")
def decisions():

    result = generate_decisions(metrics)

    return jsonify(result)


# ---------------------------------------------------------
# If I Do Nothing?
# ---------------------------------------------------------

@app.route("/api/forecasts")
def forecasts():

    result = get_depletion_forecasts(metrics)

    return jsonify(result)

# ---------------------------------------------------------
# What-If Simulation
# ---------------------------------------------------------

@app.route("/api/simulate")
def simulate():

    from flask import request

    product_id = request.args.get("product_id")
    store_id = request.args.get("store_id")
    demand_change = request.args.get(
        "demand_change",
        default=0,
        type=float
    )

    if not product_id or not store_id:
        return jsonify({
            "error": "product_id and store_id are required"
        }), 400

    matching = metrics[
        (metrics["product_id"] == product_id)
        &
        (metrics["store_id"] == store_id)
    ]

    if matching.empty:
        return jsonify({
            "error": "Product/store combination not found"
        }), 404

    row = matching.iloc[0]

    from src.scenario_engine import simulate_demand

    result = simulate_demand(
        row,
        demand_change
    )

    return jsonify(result)

@app.route("/api/ask", methods=["POST"])
def ask():
    from flask import request

    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "success": False,
            "answer": "Please enter a question."
        }), 400

    # Build grounded context from the actual StockSense analytics.
    context_rows = []

    for _, row in metrics.iterrows():
        context_rows.append(
            f"""
Store: {row['store_name']}
Product: {row['product_name']}
Current stock: {row['current_stock']} units
Average daily sales: {row['average_daily_sales']:.2f} units/day
Days of stock: {row['days_of_stock']:.2f}
Sales trend: {row['sales_trend_pct']:.1f}%
Status: {row['status']}
Data confidence: {row['data_confidence']:.0f}%
"""
        )

    context = "\n".join(context_rows)

    result = ask_stock_sense(
        question,
        context
    )

    return jsonify(result)

# ---------------------------------------------------------
# Smart Transfers
# ---------------------------------------------------------

@app.route("/api/transfers")
def transfers():

    result = find_transfer_opportunities(metrics)

    result = rank_transfer_opportunities(result)

    return jsonify(result)


# ---------------------------------------------------------
# Data Detective
# ---------------------------------------------------------

@app.route("/api/data-quality")
def data_quality():

    quality = analyze_sales_quality(
        sales,
        stores,
        products
    )

    summary = get_quality_summary(quality)

    issues = quality[
        quality["missing_days"] > 0
    ].to_dict(orient="records")

    return jsonify({
        "summary": summary,
        "issues": issues
    })


# ---------------------------------------------------------
# Start server
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )