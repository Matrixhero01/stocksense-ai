TRACK_ID=PS03

# StockSense AI

## Explainable Retail Sales & Inventory Copilot

StockSense AI is an AI-powered retail decision-support system that helps store managers understand sales and inventory conditions, identify risks, and decide what needs attention first.

It combines deterministic Python analytics with Gemini-powered natural-language explanations.

## Problem Statement

Retail managers have sales and inventory data, but it can be difficult to quickly identify:

- Which products are at risk of stock-out
- Which products are overstocked
- Where sales are increasing or decreasing
- Which store may have excess inventory
- How reliable the available sales data is
- What deserves attention first

StockSense AI turns these signals into explainable, data-grounded decisions.

## Key Features

### Smart Inventory Dashboard

Provides an overview of:

- Total products
- Total inventory
- Critical products
- Overstocked products
- Healthy inventory
- Store-level inventory signals

### Why Today?

A deterministic decision engine prioritizes the most important inventory situations.

It considers:

- Stock coverage
- Sales trends
- Risk level
- Revenue impact
- Data confidence

### Future Risk Radar

Forecasts potential inventory depletion if current demand continues.

### What-If Simulator

Allows managers to change expected demand and see how inventory coverage and stock-out risk change.

### Smart Multi-Store Transfers

Identifies potential transfer opportunities when one store has excess inventory while another store has lower coverage.

### Data Detective

Checks sales-data completeness and identifies missing observations instead of silently treating missing data as zero sales.

### Ask StockSense

Managers can ask questions in natural language.

Gemini explains the calculated results using the retailer's actual data.

## Explainable AI

StockSense separates numerical business logic from language-model reasoning.

Python performs:

- Sales calculations
- Inventory calculations
- Days-of-stock calculations
- Sales trend analysis
- Risk detection
- Decision scoring
- Forecasting
- What-If simulation
- Transfer detection
- Data-quality analysis

Gemini performs:

- Natural-language explanations
- Question answering
- Recommendation wording
- Communicating data limitations

Gemini does not calculate the underlying business numbers.

## Responsible AI

StockSense AI is a decision-support system, not an autonomous purchasing system.

The system:

- Uses actual retailer data
- Shows evidence behind recommendations
- Detects incomplete data
- Does not invent missing information
- Does not invent suppliers, costs, lead times, or purchase orders
- Keeps the final decision with the human manager

If required information is missing, StockSense explicitly states that it does not have enough data rather than fabricating an answer.

## Technology Stack

- Python
- Flask
- Pandas
- Google Gemini
- HTML
- CSS
- JavaScript
- CSV

## Project Structure

```text
stocksense-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── products.csv
│   ├── stores.csv
│   ├── inventory.csv
│   └── sales.csv
├── src/
│   ├── analytics.py
│   ├── risk_engine.py
│   ├── scenario_engine.py
│   ├── data_quality.py
│   ├── recommender.py
│   └── gemini.py
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js