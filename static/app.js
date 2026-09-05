// =========================================================
// StockSense AI - Frontend Controller
// =========================================================


// ---------------------------------------------------------
// Navigation
// ---------------------------------------------------------

function showSection(sectionId) {

    // Hide every section
    document.querySelectorAll(".section").forEach(section => {
        section.classList.remove("active");
    });

    // Show selected section
    const selected = document.getElementById(sectionId);

    if (selected) {
        selected.classList.add("active");
    }

    // Update sidebar
    document.querySelectorAll(".nav-item").forEach(button => {
        button.classList.remove("active");
    });

    const navButtons = document.querySelectorAll(".nav-item");

    navButtons.forEach(button => {

        const text = button.innerText.toLowerCase();

        if (
            (sectionId === "overview" && text.includes("overview")) ||
            (sectionId === "decisions" && text.includes("why today")) ||
            (sectionId === "forecast" && text.includes("future risk")) ||
            (sectionId === "transfers" && text.includes("transfer")) ||
            (sectionId === "data" && text.includes("data detective"))
        ) {
            button.classList.add("active");
        }
    });

    // Update title
    const titles = {
        overview: "Inventory Overview",
        decisions: "Why Today?",
        forecast: "Future Risk",
        transfers: "Smart Transfers",
        data: "Data Detective"
    };

    document.getElementById("page-title").innerText =
        titles[sectionId] || "StockSense AI";
}


// ---------------------------------------------------------
// API helper
// ---------------------------------------------------------

async function fetchJSON(url) {

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(
            `API request failed: ${response.status}`
        );
    }

    return await response.json();
}


// ---------------------------------------------------------
// Dashboard summary
// ---------------------------------------------------------

async function loadDashboard() {

    try {

        const data = await fetchJSON(
            "/api/dashboard"
        );

        document.getElementById("total-products")
            .innerText = data.total_products;

        document.getElementById("total-inventory")
            .innerText = data.total_inventory.toLocaleString();

        document.getElementById("critical-count")
            .innerText = data.critical;

        document.getElementById("overstock-count")
            .innerText = data.overstock;

    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );
    }
}


// ---------------------------------------------------------
// Why Today?
// ---------------------------------------------------------

async function loadDecisions() {

    try {

        const decisions = await fetchJSON(
            "/api/decisions"
        );

        const container =
            document.getElementById("decisions-list");

        const topContainer =
            document.getElementById("top-decisions");

        if (!decisions.length) {

            container.innerHTML =
                '<div class="loading">No decisions detected.</div>';

            topContainer.innerHTML =
                '<div class="loading">No urgent decisions.</div>';

            return;
        }


        // Full decision list

        container.innerHTML =
            '<div class="decision-grid">' +
            decisions.map(createDecisionCard).join("") +
            '</div>';


        // Top 3 for overview

        topContainer.innerHTML =
            decisions
                .slice(0, 3)
                .map(createDecisionCard)
                .join("");

    } catch (error) {

        console.error(
            "Decision error:",
            error
        );

        document.getElementById("decisions-list").innerHTML =
            '<div class="loading">Unable to load decisions.</div>';
    }
}


function createDecisionCard(item) {

    const priority =
        item.priority.toLowerCase();

    return `
        <div class="decision-card ${priority}">

            <div class="decision-top">

                <span class="priority ${priority}">
                    ${item.priority}
                </span>

                <span class="score">
                    ${item.attention_score}/100
                </span>

            </div>

            <h3>
                ${item.product_name}
            </h3>

            <div class="store-name">
                ${item.store_name}
            </div>

            <div class="reason">
                ${item.reason}
            </div>

            <div class="metrics">

                <div class="metric">
                    <strong>
                        ${item.current_stock}
                    </strong>
                    <span>UNITS</span>
                </div>

                <div class="metric">
                    <strong>
                        ${item.days_of_stock}
                    </strong>
                    <span>DAYS COVERAGE</span>
                </div>

                <div class="metric">
                    <strong>
                        ${formatTrend(item.sales_trend_pct)}
                    </strong>
                    <span>SALES TREND</span>
                </div>

            </div>

        </div>
    `;
}


function formatTrend(value) {

    const number = Number(value);

    if (number > 0) {
        return "+" + number.toFixed(1) + "%";
    }

    return number.toFixed(1) + "%";
}


// ---------------------------------------------------------
// Future Risk
// ---------------------------------------------------------

async function loadForecasts() {

    try {

        const forecasts = await fetchJSON(
            "/api/forecasts"
        );

        const container =
            document.getElementById("forecast-list");

        const valid = forecasts
            .filter(item => item.days_remaining !== null)
            .sort(
                (a, b) =>
                    a.days_remaining -
                    b.days_remaining
            );

        if (!valid.length) {

            container.innerHTML =
                '<div class="loading">No forecast data available.</div>';

            return;
        }

        container.innerHTML =
            '<div class="forecast-grid">' +
            valid.map(item => {

                const critical =
                    item.days_remaining <= 3
                        ? "critical"
                        : "";

                return `
                    <div class="forecast-card ${critical}">

                        <div class="item-row">

                            <div>

                                <div class="item-title">
                                    ${item.product_name}
                                </div>

                                <div class="item-subtitle">
                                    ${item.store_name}
                                </div>

                            </div>

                            <div class="risk-value">
                                ${item.stock_out_risk}
                            </div>

                        </div>

                        <div class="forecast-days">

                            ${item.days_remaining}

                            <span>
                                days remaining
                            </span>

                        </div>

                        <div class="item-subtitle">

                            Current stock:
                            ${item.current_stock} units

                            ·

                            Demand:
                            ${item.average_daily_sales}
                            units/day

                        </div>

                    </div>
                `;

            }).join("") +
            '</div>';


        // Overview preview

        const preview =
            document.getElementById("risk-preview");

        const first = valid[0];

        preview.innerHTML = `
            <div class="risk-item">

                <div class="item-row">

                    <div>

                        <div class="item-title">
                            ${first.product_name}
                        </div>

                        <div class="item-subtitle">
                            ${first.store_name}
                        </div>

                    </div>

                    <div class="risk-value">
                        ${first.days_remaining} days
                    </div>

                </div>

                <div class="item-subtitle">
                    ${first.stock_out_risk} stock-out risk
                </div>

            </div>
        `;

    } catch (error) {

        console.error(
            "Forecast error:",
            error
        );
    }
}


// ---------------------------------------------------------
// Smart Transfers
// ---------------------------------------------------------

async function loadTransfers() {

    try {

        const transfers = await fetchJSON(
            "/api/transfers"
        );

        const container =
            document.getElementById("transfer-list");

        const preview =
            document.getElementById("transfer-preview");


        if (!transfers.length) {

            container.innerHTML =
                '<div class="loading">No transfer opportunities detected.</div>';

            preview.innerHTML =
                '<div class="loading">No transfer opportunities.</div>';

            return;
        }


        container.innerHTML =
            transfers.map(item => {

                return `
                    <div class="transfer-item">

                        <div class="item-row">

                            <div>

                                <div class="item-title">
                                    ${item.product_name}
                                </div>

                                <div class="item-subtitle">
                                    ${item.from_store}
                                </div>

                            </div>

                            <div class="transfer-arrow">
                                →
                            </div>

                            <div>

                                <div class="item-title">
                                    ${item.to_store}
                                </div>

                                <div class="item-subtitle">
                                    ${item.before_days} days coverage
                                </div>

                            </div>

                        </div>

                        <div class="transfer-quantity">

                            Suggested transfer:

                            <strong>
                                ${item.transfer_units} units
                            </strong>

                            · Destination becomes

                            <strong>
                                ${item.after_days} days
                            </strong>

                        </div>

                    </div>
                `;

            }).join("");


        // Overview preview

        const first = transfers[0];

        preview.innerHTML = `

            <div class="transfer-item">

                <div class="item-title">
                    ${first.product_name}
                </div>

                <div class="item-subtitle">
                    ${first.from_store}
                    →
                    ${first.to_store}
                </div>

                <div class="transfer-quantity">

                    Move

                    <strong>
                        ${first.transfer_units} units
                    </strong>

                    · Destination:
                    ${first.after_days} days

                </div>

            </div>
        `;

    } catch (error) {

        console.error(
            "Transfer error:",
            error
        );
    }
}


// ---------------------------------------------------------
// Data Detective
// ---------------------------------------------------------

async function loadDataQuality() {

    try {

        const data = await fetchJSON(
            "/api/data-quality"
        );

        const summary =
            data.summary;

        const container =
            document.getElementById("data-quality");


        container.innerHTML = `

            <div class="quality-summary">

                <div class="quality-stat">

                    <strong>
                        ${summary.total_combinations}
                    </strong>

                    <span>
                        COMBINATIONS CHECKED
                    </span>

                </div>

                <div class="quality-stat">

                    <strong>
                        ${summary.complete}
                    </strong>

                    <span>
                        COMPLETE
                    </span>

                </div>

                <div class="quality-stat">

                    <strong>
                        ${summary.minor_gaps}
                    </strong>

                    <span>
                        MINOR GAPS
                    </span>

                </div>

                <div class="quality-stat">

                    <strong>
                        ${summary.total_missing_days}
                    </strong>

                    <span>
                        MISSING DAYS
                    </span>

                </div>

            </div>
        `;


        if (data.issues.length) {

            container.innerHTML +=
                data.issues.map(issue => {

                    return `
                        <div class="quality-card">

                            <div class="item-title">
                                ${issue.product_name}
                            </div>

                            <div class="item-subtitle">
                                ${issue.store_name}
                            </div>

                            <div class="reason">

                                ${issue.missing_days}
                                missing sales day(s).

                                Data quality:
                                ${issue.quality}

                            </div>

                        </div>
                    `;

                }).join("");

        } else {

            container.innerHTML += `

                <div class="quality-card">

                    <div class="item-title">
                        ✓ No data quality issues detected
                    </div>

                    <div class="item-subtitle">
                        All store/product combinations
                        have complete observations
                        in the current analysis window.
                    </div>

                </div>

            `;
        }

    } catch (error) {

        console.error(
            "Data quality error:",
            error
        );
    }
}


// ---------------------------------------------------------
// Initialize application
// ---------------------------------------------------------

async function initializeApp() {

    await Promise.all([
        loadDashboard(),
        loadDecisions(),
        loadForecasts(),
        loadTransfers(),
        loadDataQuality()
    ]);

}

// =========================================================
// What-If Simulator
// =========================================================

let forecastData = [];


async function initializeSimulator() {

    try {

        forecastData = await fetchJSON(
            "/api/forecasts"
        );

        populateSimulationSelectors();

        runSimulation();

    } catch (error) {

        console.error(
            "Simulator initialization error:",
            error
        );
    }
}


function populateSimulationSelectors() {

    const productSelect =
        document.getElementById(
            "simulation-product"
        );

    const storeSelect =
        document.getElementById(
            "simulation-store"
        );


    // Unique products

    const products = [];

    forecastData.forEach(item => {

        if (
            !products.some(
                p => p.product_id === item.product_id
            )
        ) {

            products.push({
                product_id: item.product_id,
                product_name: item.product_name
            });

        }

    });


    productSelect.innerHTML =
        products.map(product => {

            return `
                <option value="${product.product_id}">
                    ${product.product_name}
                </option>
            `;

        }).join("");


    updateSimulationStores();


    productSelect.addEventListener(
        "change",
        updateSimulationStores
    );
}


function updateSimulationStores() {

    const productId =
        document.getElementById(
            "simulation-product"
        ).value;

    const storeSelect =
        document.getElementById(
            "simulation-store"
        );


    const stores = forecastData.filter(
        item =>
            item.product_id === productId
    );


    storeSelect.innerHTML =
        stores.map(store => {

            return `
                <option value="${store.store_id}">
                    ${store.store_name}
                </option>
            `;

        }).join("");


    runSimulation();
}


function setupSimulationSlider() {

    const slider =
        document.getElementById(
            "demand-slider"
        );

    const value =
        document.getElementById(
            "demand-value"
        );


    slider.addEventListener(
        "input",
        () => {

            value.innerText =
                `${slider.value}%`;

            runSimulation();

        }
    );

}


async function runSimulation() {

    const product =
        document.getElementById(
            "simulation-product"
        );

    const store =
        document.getElementById(
            "simulation-store"
        );

    const slider =
        document.getElementById(
            "demand-slider"
        );


    if (!product || !store || !slider) {
        return;
    }


    if (!product.value || !store.value) {
        return;
    }


    const demandChange =
        slider.value;


    try {

        const result = await fetchJSON(
            `/api/simulate?product_id=${encodeURIComponent(product.value)}&store_id=${encodeURIComponent(store.value)}&demand_change=${demandChange}`
        );


        const container =
            document.getElementById(
                "simulation-result"
            );


        const riskClass =
            result.stock_out_risk === "LOW"
                ? "safe"
                : "risk";


        const days =
            result.days_remaining === null
                ? "—"
                : result.days_remaining;


        container.innerHTML = `

            <div class="simulation-result">

                <div class="sim-result-card">

                    <div class="label">
                        CURRENT STOCK
                    </div>

                    <div class="value">
                        ${result.current_stock}
                    </div>

                    <div class="sub">
                        units available
                    </div>

                </div>


                <div class="sim-result-card">

                    <div class="label">
                        SCENARIO DEMAND
                    </div>

                    <div class="value">
                        ${result.scenario_demand}
                    </div>

                    <div class="sub">
                        units / day
                    </div>

                </div>


                <div class="sim-result-card">

                    <div class="label">
                        EST. COVERAGE
                    </div>

                    <div class="value">
                        ${days}
                    </div>

                    <div class="sub">
                        days remaining
                    </div>

                </div>


                <div class="sim-result-card ${riskClass}">

                    <div class="label">
                        STOCK-OUT RISK
                    </div>

                    <div class="value">
                        ${result.stock_out_risk}
                    </div>

                    <div class="sub">
                        scenario outcome
                    </div>

                </div>

            </div>


            <div class="sim-explanation">

                <strong>
                    Scenario:
                </strong>

                Demand changes by
                ${demandChange > 0 ? "+" : ""}
                ${demandChange}%.

                ${result.message}

            </div>
        `;

    } catch (error) {

        console.error(
            "Simulation error:",
            error
        );

    }

}


// Initialize simulator
initializeSimulator();

setupSimulationSlider();

// ---------------------------------------------------------
// Ask StockSense AI
// ---------------------------------------------------------

async function askStockSense() {

    const input = document.getElementById("ask-question");
    const answerBox = document.getElementById("ask-answer");

    const question = input.value.trim();

    if (!question) {
        answerBox.innerHTML = `
            <div class="empty-answer">
                <div class="empty-icon">!</div>
                <h3>Ask a question first</h3>
                <p>Enter a question about your inventory or sales.</p>
            </div>
        `;
        return;
    }

    // Show loading state
    answerBox.innerHTML = `
        <div class="ai-loading">
            <div class="loading-spinner"></div>
            <h3>StockSense is thinking...</h3>
            <p>Analyzing your retail data with Gemini.</p>
        </div>
    `;

    try {

        const response = await fetch("/api/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        const result = await response.json();

        if (!response.ok || !result.success) {

            throw new Error(
                result.answer || "Unable to get an answer."
            );

        }

        // Display Gemini response
        answerBox.innerHTML = `
            <div class="ai-answer">

                <div class="answer-header">

                    <div>
                        <p class="eyebrow">STOCKSENSE AI</p>
                        <h3>Analysis</h3>
                    </div>

                    <div class="ai-badge">
                        ✦ GEMINI
                    </div>

                </div>

                <div class="answer-content">
                    ${formatAIAnswer(result.answer)}
                </div>

                <div class="answer-footer">
                    <span>✓ Grounded in retailer data</span>
                    <span>Human decision required</span>
                </div>

            </div>
        `;

    } catch (error) {

        console.error("Ask StockSense error:", error);

        answerBox.innerHTML = `
            <div class="empty-answer error-answer">

                <div class="empty-icon">!</div>

                <h3>AI unavailable</h3>

                <p>
                    ${escapeHTML(error.message)}
                </p>

                <small>
                    StockSense calculations are still available
                    without Gemini.
                </small>

            </div>
        `;
    }
}


// ---------------------------------------------------------
// Suggested Questions
// ---------------------------------------------------------

function askSuggested(question) {

    const input = document.getElementById("ask-question");

    input.value = question;

    askStockSense();
}


// ---------------------------------------------------------
// Format Gemini response
// ---------------------------------------------------------

function formatAIAnswer(text) {

    let formatted = escapeHTML(text);

    // Bold markdown
    formatted = formatted.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    // Convert lines into paragraphs
    formatted = formatted
        .split("\n\n")
        .map(paragraph => {

            if (paragraph.trim() === "") {
                return "";
            }

            return `<p>${paragraph.replace(/\n/g, "<br>")}</p>`;

        })
        .join("");

    return formatted;
}


// ---------------------------------------------------------
// Prevent HTML injection
// ---------------------------------------------------------

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}

// Start app
initializeApp();