import json
import os
import streamlit as st
import pandas as pd


from modules.llm_agent import run_llm_agent
from modules.inventory_health import calculate_inventory_health
from modules.stock_coverage import calculate_stock_coverage
from modules.forecast import forecast_product_demand
from modules.strategy import evaluate_suppliers
from modules.recommendation_insights import generate_recommendation_insights
from modules.supplier_analytics import calculate_supplier_performance
from modules.agent_log import load_agent_logs
from modules.inventory import load_inventory
from modules.demand import calculate_average_demand
from modules.stockout import calculate_stockout_risk
from modules.supplier import compare_suppliers
from modules.reorder import calculate_reorder_quantity
from modules.report import generate_procurement_report
from modules.agent import run_supplychain_agent
from modules.backup import generate_backup_plan


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="SupplyChainIQ",
    page_icon="📦",
    layout="wide"
)


# =====================================================
# DASHBOARD TITLE
# =====================================================

st.title("📦 SupplyChainIQ")

st.subheader(
    "Autonomous Supply Chain Decision Agent"
)

st.write(
    "An intelligent system for inventory monitoring, "
    "demand analysis and procurement recommendations."
)

st.divider()


# =====================================================
# LOAD INVENTORY
# =====================================================

inventory = load_inventory()

if inventory is None:
    st.error("Inventory data could not be loaded.")
    st.stop()


# =====================================================
# 1. INVENTORY OVERVIEW
# =====================================================

st.header("📊 Inventory Overview")

# Calculate at-risk products
at_risk_count = 0

for _, product in inventory.iterrows():

    result = calculate_stockout_risk(
        product["product_id"], 5
    )

    if result is not None and result["risk"] != "LOW":
        at_risk_count += 1


col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Products",
    len(inventory)
)

col2.metric(
    "Total Available Stock",
    int(inventory["current_stock"].sum())
)

col3.metric(
    "At-Risk Products",
    at_risk_count
)

st.divider()


# =====================================================
# 2. INVENTORY DETAILS
# =====================================================

st.header("📋 Inventory Details")

st.dataframe(
    inventory,
    use_container_width=True
)

st.divider()


# =====================================================
# 3. DEMAND ANALYSIS
# =====================================================

st.header("📈 Demand Analysis")

demand_data = []

for _, product in inventory.iterrows():

    average = calculate_average_demand(
        product["product_id"]
    )

    demand_data.append({

        "Product": product["product_name"],

        "Average Daily Demand": average

    })


demand_df = pd.DataFrame(demand_data)

st.bar_chart(
    demand_df.set_index("Product")
)

st.divider()


# =====================================================
# 4. STOCKOUT RISK ANALYSIS
# =====================================================

st.header("⚠️ Stockout Risk Analysis")

risk_data = []

for _, product in inventory.iterrows():

    result = calculate_stockout_risk(
        product["product_id"], 5
    )

    if result is not None:

        risk_data.append({

            "Product": product["product_name"],

            "Current Stock": result["current_stock"],

            "Expected Demand": result["expected_demand"],

            "Delivery Days": result["delivery_days"],

            "Risk": result["risk"]

        })


risk_df = pd.DataFrame(risk_data)

st.dataframe(
    risk_df,
    use_container_width=True
)

st.divider()


# =====================================================
# 5. SUPPLIER COMPARISON
# =====================================================

st.header("🏭 Supplier Comparison")

selected_product = st.selectbox(

    "Select a Product",

    inventory["product_id"].tolist(),

    format_func=lambda x: inventory.loc[
        inventory["product_id"] == x,
        "product_name"
    ].iloc[0]

)

supplier_data = compare_suppliers(
    selected_product
)

if supplier_data is not None:

    st.dataframe(
        supplier_data,
        use_container_width=True
    )

st.divider()


# =====================================================
# 6. WHAT-IF ANALYSIS
# =====================================================

st.header("🔍 What-if Analysis")

st.write(
    "Simulate different stock levels and delivery times "
    "to evaluate inventory risk."
)


# Select product for simulation
whatif_product = st.selectbox(

    "Choose Product for Simulation",

    inventory["product_id"].tolist(),

    format_func=lambda x: inventory.loc[
        inventory["product_id"] == x,
        "product_name"
    ].iloc[0],

    key="whatif_product"

)


# Get selected product details
product = inventory[
    inventory["product_id"] == whatif_product
].iloc[0]


current_stock = int(product["current_stock"])

safety_stock = float(product["safety_stock"])


# Calculate average demand
average_demand = calculate_average_demand(
    whatif_product
)


# User input controls
simulated_stock = st.slider(

    "Simulated Current Stock",

    min_value=0,

    max_value=max(200, current_stock * 3),

    value=current_stock

)


delivery_days = st.slider(

    "Supplier Delivery Time (Days)",

    min_value=1,

    max_value=30,

    value=5

)


# Calculate expected demand
expected_demand = average_demand * delivery_days


# Calculate stockout risk
if simulated_stock < expected_demand:

    risk = "HIGH"

elif simulated_stock <= expected_demand + safety_stock:

    risk = "MEDIUM"

else:

    risk = "LOW"


# Calculate recommended order quantity
reorder_quantity = max(

    0,

    expected_demand + safety_stock - simulated_stock

)


# Display simulation results
col1, col2, col3 = st.columns(3)

col1.metric(
    "Expected Demand",
    f"{expected_demand:.0f} units"
)

col2.metric(
    "Stockout Risk",
    risk
)

col3.metric(
    "Recommended Order",
    f"{reorder_quantity:.0f} units"
)


# Display risk message
if risk == "HIGH":

    st.error(
        "High risk! Immediate replenishment is recommended."
    )

elif risk == "MEDIUM":

    st.warning(
        "Moderate risk. Monitor inventory and plan replenishment."
    )

else:

    st.success(
        "Low risk. Current inventory is sufficient."
    )


st.divider()


# =====================================================
# 7. INTELLIGENT SUPPLIER RECOMMENDATION
# =====================================================

st.header("🤖 Intelligent Supplier Recommendation")


# Calculate stockout risk for selected supplier product
risk_result = calculate_stockout_risk(
    selected_product, 5
)


if (
    supplier_data is not None
    and not supplier_data.empty
    and risk_result is not None
):

    # Find cheapest supplier
    cheapest_supplier = supplier_data.sort_values(
        by="unit_price"
    ).iloc[0]


    # Find fastest supplier
    fastest_supplier = supplier_data.sort_values(
        by=["delivery_days", "unit_price"]
    ).iloc[0]


    # Select supplier based on inventory risk
    if risk_result["risk"] in ["HIGH", "MEDIUM"]:

        recommended_supplier = fastest_supplier

        reason = (
            "Inventory risk is elevated. "
            "The fastest supplier is recommended "
            "to reduce replenishment time."
        )

    else:

        recommended_supplier = cheapest_supplier

        reason = (
            "Inventory risk is low. "
            "The cheapest supplier is recommended "
            "to reduce procurement cost."
        )


    # Display recommendation
    st.success(
        f"Recommended Supplier: "
        f"{recommended_supplier['supplier_name']}"
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Stockout Risk",
        risk_result["risk"]
    )


    col2.metric(
        "Unit Price",
        f"₹{recommended_supplier['unit_price']:,.2f}"
    )


    col3.metric(
        "Delivery Time",
        f"{int(recommended_supplier['delivery_days'])} Days"
    )


    st.info(reason)


else:

    st.warning(
        "Supplier recommendation could not be generated."
    )


st.divider()


# =====================================================
# 8. REORDER RECOMMENDATIONS
# =====================================================

st.header("🛒 Reorder Recommendations")

reorder_data = []

for _, product in inventory.iterrows():

    result = calculate_reorder_quantity(

        product["product_id"],

        5

    )

    if result is not None:

        reorder_data.append({

            "Product": product["product_name"],

            "Current Stock": result["current_stock"],

            "Average Daily Demand": result["average_demand"],

            "Expected Demand": result["expected_demand"],

            "Recommended Order": result["reorder_quantity"]

        })


reorder_df = pd.DataFrame(reorder_data)

st.dataframe(
    reorder_df,
    use_container_width=True
)

st.divider()


# =====================================================
# 9. PROCUREMENT REPORT
# =====================================================

st.header("📑 Procurement Report")


if st.button("Generate Procurement Report"):

    # Ensure reports folder exists
    os.makedirs("reports", exist_ok=True)

    # Generate report
    generate_procurement_report()


    # Load generated report
    report = pd.read_csv(
        "reports/procurement_report.csv"
    )


    st.success(
        "Procurement report generated successfully!"
    )


    # Display report
    st.dataframe(
        report,
        use_container_width=True
    )


    # Download report
    csv = report.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(

        label="Download Procurement Report",

        data=csv,

        file_name="SupplyChainIQ_Report.csv",

        mime="text/csv"

    )


st.divider()

# =====================================================
# 10. AI AGENT CONTROL PANEL
# =====================================================

st.header("🤖 AI Agent Control Panel")

st.write(
    "Run the SupplyChainIQ autonomous decision agent "
    "to analyse inventory and generate procurement decisions."
)

if st.button("🚀 Run SupplyChainIQ AI Agent"):

    with st.spinner("AI Agent is analysing inventory..."):

        agent_decisions = run_supplychain_agent()

    if agent_decisions:

        agent_df = pd.DataFrame(agent_decisions)

        st.success(
            "AI Agent completed its analysis successfully!"
        )

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Products Analysed",
            len(agent_df)
        )

        col2.metric(
            "High Risk Products",
            (agent_df["Final Risk"] == "HIGH").sum()
        )

        col3.metric(
            "Total Estimated Cost",
            f"₹{agent_df['Estimated Cost'].sum():,.2f}"
        )

        st.subheader("📊 Agent Decision Report")

        st.dataframe(
            agent_df,
            use_container_width=True
        )

        # Decision explanations
        st.subheader("🧠 Agent Decision Explanations")

        for _, decision in agent_df.iterrows():

            st.markdown(
                f"**{decision['Product']}**"
            )

            st.info(
                decision["Reason"]
            )

        # Download agent report
        agent_csv = agent_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download AI Agent Report",
            data=agent_csv,
            file_name="SupplyChainIQ_AI_Agent_Report.csv",
            mime="text/csv"
        )

    else:

        st.warning(
            "The AI Agent could not generate any decisions."
        )

st.divider()
# =========================================
# SUPPLIER BACKUP PLANNING
# =========================================

st.markdown("---")

st.header("🔄 Supplier Backup Planning")

st.write(
    "Evaluate alternative suppliers for all products "
    "and generate a complete backup procurement report."
)

inventory = load_inventory()

if inventory is not None and not inventory.empty:

    if st.button(
        "Generate All Backup Plans",
        key="generate_all_backups"
    ):

        backup_results = []

        for _, product in inventory.iterrows():

            backup = generate_backup_plan(
                product["product_id"]
            )

            if backup is None:
                continue

            if backup["Best Backup Supplier"] is None:
                continue

            backup_results.append({

                "Product": backup["Product"],

                "Primary Supplier": backup["Primary Supplier"],

                "Backup Supplier": backup["Best Backup Supplier"],

                "Reliability": backup["Backup Reliability"],

                "Delivery Days": backup["Backup Delivery Days"],

                "Order Quantity": backup["Backup Order Quantity"],

                "Estimated Cost": backup["Backup Estimated Cost"],

                "Decision Score": backup["Backup Decision Score"]

            })

        if backup_results:

            backup_report = pd.DataFrame(backup_results)

            st.success(
                "Backup planning completed successfully!"
            )

            st.subheader("Complete Backup Supplier Report")

            st.dataframe(
                backup_report,
                use_container_width=True
            )

            st.subheader("Backup Planning Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Products Evaluated",
                len(backup_report)
            )

            col2.metric(
                "Backup Suppliers Identified",
                backup_report["Backup Supplier"].nunique()
            )

            col3.metric(
                "Total Backup Procurement Cost",
                f"₹{backup_report['Estimated Cost'].sum():,.2f}"
            )

            csv_data = backup_report.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download Backup Procurement Report",
                data=csv_data,
                file_name="backup_procurement_report.csv",
                mime="text/csv"
            )

        else:

            st.warning(
                "No backup supplier recommendations generated."
            )

else:

    st.error("Inventory data could not be loaded.")
# =========================================
# AGENT ACTIVITY HISTORY
# =========================================

st.markdown("---")

st.header("📋 Agent Activity History")

st.write(
    "Explore and filter previously recorded "
    "procurement decisions."
)

logs = load_agent_logs()

if not logs.empty:

    # =====================================
    # FILTER OPTIONS
    # =====================================

    st.subheader("Filter Activity Records")

    col1, col2 = st.columns(2)

    with col1:

        products = ["All"] + sorted(
            logs["Product"].dropna().unique().tolist()
        )

        selected_product = st.selectbox(
            "Select Product",
            products
        )

    with col2:

        risks = ["All"] + sorted(
            logs["Stockout Risk"].dropna().unique().tolist()
        )

        selected_risk = st.selectbox(
            "Select Stockout Risk",
            risks
        )

    filtered_logs = logs.copy()

    if selected_product != "All":

        filtered_logs = filtered_logs[
            filtered_logs["Product"] == selected_product
        ]

    if selected_risk != "All":

        filtered_logs = filtered_logs[
            filtered_logs["Stockout Risk"] == selected_risk
        ]

    # =====================================
    # DISPLAY FILTERED HISTORY
    # =====================================

    st.subheader("Filtered Decision History")

    st.dataframe(
        filtered_logs,
        use_container_width=True
    )

    # =====================================
    # SUMMARY METRICS
    # =====================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Filtered Activities",
        len(filtered_logs)
    )

    col2.metric(
        "Products",
        filtered_logs["Product"].nunique()
    )

    col3.metric(
        "Backup Recommendations",
        filtered_logs["Backup Supplier"].notna().sum()
    )

    # =====================================
    # DOWNLOAD FILTERED HISTORY
    # =====================================

    csv_data = filtered_logs.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Filtered Activity History",
        data=csv_data,
        file_name="filtered_agent_activity.csv",
        mime="text/csv"
    )

else:

    st.info("No agent activity recorded yet.")

# ==========================================
# SUPPLIER PERFORMANCE ANALYTICS
# ==========================================

st.header("📊 Supplier Performance Analytics")

performance = calculate_supplier_performance()

# Supplier Performance Highlights

best_reliability = performance.loc[
    performance["Average_Reliability"].idxmax()
]

fastest_delivery = performance.loc[
    performance["Average_Delivery_Days"].idxmin()
]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "🏆 Highest Supplier Reliability",
        f"{best_reliability['Average_Reliability']:.1f}/100",
        best_reliability["supplier_name"]
    )

with col2:
    st.metric(
        "🚚 Fastest Average Delivery",
        f"{fastest_delivery['Average_Delivery_Days']:.1f} days",
        fastest_delivery["supplier_name"]
    )

st.subheader("Supplier Reliability Comparison")

st.bar_chart(
    performance.set_index("supplier_name")["Average_Reliability"]
)

st.subheader("Supplier Delivery Time Comparison")

st.bar_chart(
    performance.set_index("supplier_name")["Average_Delivery_Days"]
)

st.subheader("Average Supplier Unit Price")

st.bar_chart(
    performance.set_index("supplier_name")["Average_Unit_Price"]
)

st.subheader("Complete Supplier Performance Table")

st.dataframe(performance, use_container_width=True)

# Download Supplier Performance Report

csv_data = performance.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Supplier Performance Report",
    data=csv_data,
    file_name="supplier_performance_report.csv",
    mime="text/csv"
)
# ==========================================
# SUPPLIER RECOMMENDATION INSIGHTS
# ==========================================

st.header("💡 Supplier Recommendation Insights")

st.write(
    "Understand why the autonomous decision agent "
    "selected a particular supplier."
)

product_options = {
    "Laptop": "P101",
    "Mouse": "P102",
    "Keyboard": "P103",
    "Monitor": "P104",
    "Printer": "P105"
}

selected_product = st.selectbox(
    "Select Product for Recommendation Insights",
    list(product_options.keys())
)

product_id = product_options[selected_product]

insights = generate_recommendation_insights(product_id)

st.subheader("Recommended Supplier")

st.success(insights["recommended_supplier"])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Supplier Reliability",
        f"{insights['reliability']:.1f}/100"
    )

with col2:
    st.metric(
        "Delivery Time",
        f"{insights['delivery_days']} days"
    )

with col3:
    st.metric(
        "Decision Score",
        f"{insights['decision_score']:.2f}/100"
    )

col4, col5 = st.columns(2)

with col4:
    st.metric(
        "Estimated Procurement Cost",
        f"₹{insights['estimated_cost']:,.2f}"
    )

with col5:
    st.metric(
        "Stockout Risk",
        insights["stockout_risk"]
    )

st.subheader("Why Was This Supplier Selected?")

st.info(insights["explanation"])

# ==========================================
# DECISION SCORE BREAKDOWN
# ==========================================

st.header("📊 Decision Score Breakdown")

st.write(
    "Explore how different evaluation factors "
    "contribute to the supplier selection."
)

decision_result = evaluate_suppliers(product_id)

evaluation = decision_result["Supplier Evaluation"]

st.subheader("Supplier Evaluation Comparison")

st.dataframe(
    evaluation[
        [
            "Supplier",
            "Cost Score",
            "Delivery Score",
            "Risk Score",
            "Reliability Score",
            "Decision Score"
        ]
    ],
    use_container_width=True
)

st.subheader("Recommended Supplier Score Breakdown")

recommended = evaluation.iloc[0]

score_breakdown = pd.DataFrame({
    "Evaluation Factor": [
        "Cost Score",
        "Delivery Score",
        "Risk Score",
        "Reliability Score"
    ],
    "Score": [
        recommended["Cost Score"],
        recommended["Delivery Score"],
        recommended["Risk Score"],
        recommended["Reliability Score"]
    ]
})

st.bar_chart(
    score_breakdown.set_index("Evaluation Factor")
)

st.info(
    "Decision Score = Cost (30%) + Delivery (25%) "
    "+ Stockout Risk (25%) + Reliability (20%)."
)

# ==========================================
# DOWNLOAD DECISION ANALYSIS REPORT
# ==========================================

st.subheader("📥 Download Decision Analysis Report")

decision_csv = evaluation.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Supplier Decision Report",
    data=decision_csv,
    file_name=f"{selected_product}_decision_analysis.csv",
    mime="text/csv"
)

# ==========================================
# INVENTORY DEMAND FORECASTING
# ==========================================

st.header("📈 Inventory Demand Forecasting")

st.write(
    "Estimate future product demand using historical sales data."
)

forecast_product = st.selectbox(
    "Select Product for Demand Forecasting",
    list(product_options.keys()),
    key="forecast_product"
)

forecast_product_id = product_options[forecast_product]

forecast_result = forecast_product_demand(forecast_product_id)

if forecast_result:

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average Daily Demand",
            f"{forecast_result['average_demand']} units"
        )

    with col2:
        st.metric(
            "7-Day Forecasted Demand",
            f"{forecast_result['total_forecast']} units"
        )

    st.subheader("Future Demand Forecast")

    st.line_chart(
        forecast_result["forecast"].set_index("Day")
    )

    st.subheader("Forecast Details")

    st.dataframe(
        forecast_result["forecast"],
        use_container_width=True
    )

# ==========================================
# INVENTORY STOCK COVERAGE ANALYSIS
# ==========================================

st.header("📦 Inventory Stock Coverage Analysis")

st.write(
    "Monitor how many days the current inventory "
    "can support customer demand."
)

coverage = calculate_stock_coverage()

st.subheader("Stock Coverage Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Critical Products",
        len(coverage[coverage["Inventory Status"] == "CRITICAL"])
    )

with col2:
    st.metric(
        "Low Stock Products",
        len(coverage[coverage["Inventory Status"] == "LOW"])
    )

with col3:
    st.metric(
        "Healthy Products",
        len(coverage[coverage["Inventory Status"] == "HEALTHY"])
    )

st.subheader("Product-wise Stock Coverage")

st.dataframe(
    coverage,
    use_container_width=True
)

st.subheader("Days of Stock Remaining")

st.bar_chart(
    coverage.set_index("product_name")["Days of Stock Remaining"]
)
# ==========================================
# INVENTORY HEALTH SUMMARY
# ==========================================

st.header("💚 Overall Inventory Health")

health = calculate_inventory_health()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Products", health["total_products"])

with col2:
    st.metric("Total Stock Units", health["total_stock"])

with col3:
    st.metric("Critical Products", health["critical_products"])

with col4:
    st.metric(
        "Inventory Health",
        f'{health["health_percentage"]}%'
    )

st.progress(health["health_percentage"] / 100)

st.success(
    f'{health["healthy_products"]} out of '
    f'{health["total_products"]} products are meeting '
    'their safety stock requirements.'
)

health_report = pd.DataFrame([health])

st.download_button(
    label="📥 Download Inventory Health Report",
    data=health_report.to_csv(index=False).encode("utf-8"),
    file_name="inventory_health_report.csv",
    mime="text/csv"
)

# =========================================
# SUPPLYCHAINIQ - LLM AI ASSISTANT
# =========================================

st.markdown("---")

st.header("🤖 Ask SupplyChainIQ - AI Assistant")
st.info(
    "ℹ️ SupplyChainIQ uses demonstration inventory, sales "
    "and supplier datasets. Supplier prices, reliability "
    "and delivery times are not live-verified. "
    "All procurement recommendations require human approval."
)

st.write(
    "Ask questions about inventory, demand, stockout risks "
    "and supplier recommendations."
)

with st.form("supplychain_ai_form"):

    user_query = st.text_area(
        "Enter your question:",
        placeholder="Example: Which product has the highest stockout risk?"
    )

    ask_button = st.form_submit_button("🚀 Ask AI Agent")


if ask_button:

    if user_query.strip():

        with st.spinner("SupplyChainIQ is analysing your request..."):

            try:

                result = run_llm_agent(user_query)

                st.success("AI analysis completed!")

                st.subheader("💡 AI Response")

                st.markdown(result["answer"])
                st.download_button(
    label="📥 Download AI Analysis Report",
    data=json.dumps(result, indent=4, default=str),
    file_name="SupplyChainIQ_AI_Analysis.json",
    mime="application/json"
)

                st.subheader("⚙️ Agent Tool Activity")

                st.metric(
                    "Total Tool Calls",
                    result["tool_calls"]
                )

                for index, item in enumerate(result["activity"]):

                    with st.expander(
                        f"Tool {index + 1}: {item['tool']}"
                    ):

                        st.write("Arguments:")
                        st.json(item["arguments"])

                        st.write("Tool Result:")
                        st.write(item["result"])

            except Exception as error:

                st.error(f"Agent Error: {error}")

    else:

        st.warning("Please enter a question first.")

# =====================================================
# 10. FOOTER
# =====================================================

st.caption(
    "SupplyChainIQ | Autonomous Supply Chain Decision Agent"
)