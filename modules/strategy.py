import pandas as pd

from modules.inventory import load_inventory
from modules.demand import calculate_average_demand
from modules.supplier import compare_suppliers
from modules.stockout import calculate_stockout_risk


def evaluate_suppliers(product_id):

    # =====================================
    # STEP 1: LOAD PRODUCT INFORMATION
    # =====================================

    inventory = load_inventory()

    if inventory is None:
        return None

    product = inventory[
        inventory["product_id"] == product_id
    ]

    if product.empty:
        return None

    current_stock = float(
        product.iloc[0]["current_stock"]
    )

    safety_stock = float(
        product.iloc[0]["safety_stock"]
    )

    product_name = product.iloc[0]["product_name"]

    # =====================================
    # STEP 2: CALCULATE AVERAGE DEMAND
    # =====================================

    average_demand = calculate_average_demand(product_id)

    if average_demand is None:
        return None

    # =====================================
    # STEP 3: LOAD SUPPLIER INFORMATION
    # =====================================

    suppliers = compare_suppliers(product_id)

    if suppliers is None or suppliers.empty:
        return None

    suppliers = suppliers.copy()

    required_columns = [
        "unit_price",
        "delivery_days",
        "reliability_score"
    ]

    if not all(
        column in suppliers.columns
        for column in required_columns
    ):
        raise ValueError(
            "Supplier data is missing a required column."
        )

    for column in required_columns:
        suppliers[column] = pd.to_numeric(
            suppliers[column],
            errors="coerce"
        )

    suppliers = suppliers.dropna(
        subset=required_columns
    )

    suppliers = suppliers[
        (suppliers["unit_price"] > 0)
        & (suppliers["delivery_days"] > 0)
        & (suppliers["reliability_score"].between(0, 100))
    ]

    if suppliers.empty:
        return None

    # =====================================
    # STEP 4: EVALUATE EACH SUPPLIER
    # =====================================

    evaluation = []

    for _, supplier in suppliers.iterrows():

        supplier_name = supplier["supplier_name"]

        unit_price = float(supplier["unit_price"])

        delivery_days = int(supplier["delivery_days"])

        reliability = float(
            supplier["reliability_score"]
        )

        expected_demand = (
            average_demand * delivery_days
        )

        reorder_quantity = max(
            0,
            expected_demand + safety_stock - current_stock
        )

        total_cost = (
            reorder_quantity * unit_price
        )

        risk_result = calculate_stockout_risk(
            product_id,
            delivery_days
        )

        if risk_result is None:
            continue

        risk = risk_result["risk"]

        evaluation.append({

            "Supplier": supplier_name,

            "Unit Price": unit_price,

            "Delivery Days": delivery_days,

            "Reliability": reliability,

            "Expected Demand": expected_demand,

            "Order Quantity": reorder_quantity,

            "Total Cost": total_cost,

            "Stockout Risk": risk

        })

    if not evaluation:
        return None

    result = pd.DataFrame(evaluation)

    # =====================================
    # STEP 5: NORMALISE COST SCORE
    # =====================================

    min_cost = result["Total Cost"].min()

    max_cost = result["Total Cost"].max()

    if max_cost == min_cost:

        result["Cost Score"] = 100

    else:

        result["Cost Score"] = (

            (max_cost - result["Total Cost"])

            / (max_cost - min_cost)

        ) * 100

    # =====================================
    # STEP 6: NORMALISE DELIVERY SCORE
    # =====================================

    min_days = result["Delivery Days"].min()

    max_days = result["Delivery Days"].max()

    if max_days == min_days:

        result["Delivery Score"] = 100

    else:

        result["Delivery Score"] = (

            (max_days - result["Delivery Days"])

            / (max_days - min_days)

        ) * 100

    # =====================================
    # STEP 7: CALCULATE RISK SCORE
    # =====================================

    risk_scores = {

        "LOW": 100,

        "MEDIUM": 60,

        "HIGH": 0

    }

    result["Risk Score"] = result[
        "Stockout Risk"
    ].map(risk_scores)

    # =====================================
    # STEP 8: CALCULATE RELIABILITY SCORE
    # =====================================

    result["Reliability Score"] = result[
        "Reliability"
    ]

    # =====================================
    # STEP 9: CALCULATE FINAL DECISION SCORE
    # =====================================

    result["Decision Score"] = (

        result["Cost Score"] * 0.30

        + result["Delivery Score"] * 0.25

        + result["Risk Score"] * 0.25

        + result["Reliability Score"] * 0.20

    )

    result["Decision Score"] = result[
        "Decision Score"
    ].round(2)

    # =====================================
    # STEP 10: SELECT BEST SUPPLIER
    # =====================================

    result = result.sort_values(

        by=[
            "Decision Score",
            "Total Cost",
            "Delivery Days"
        ],

        ascending=[False, True, True]

    ).reset_index(drop=True)

    best_supplier = result.iloc[0]

    # =====================================
    # STEP 11: GENERATE EXPLANATION
    # =====================================

    if reorder_quantity == 0:
        order_message = (
            "Current inventory does not require immediate replenishment."
        )
    else:
        order_message = (
            f"An order of {int(best_supplier['Order Quantity'])} "
            "units is recommended."
        )

    explanation = (

        f"{best_supplier['Supplier']} was selected with a "
        f"decision score of {best_supplier['Decision Score']}/100. "

        f"The supplier has a reliability score of "
        f"{best_supplier['Reliability']}/100, "

        f"a delivery time of "
        f"{int(best_supplier['Delivery Days'])} days, "

        f"and an estimated procurement cost of "
        f"₹{best_supplier['Total Cost']:,.2f}. "

        f"Projected stockout risk is "
        f"{best_supplier['Stockout Risk']}. "

        f"{order_message}"

    )

    # =====================================
    # STEP 12: RETURN FINAL RESULTS
    # =====================================

    return {

        "Product": product_name,

        "Current Stock": current_stock,

        "Average Demand": average_demand,

        "Supplier Evaluation": result,

        "Recommended Supplier": best_supplier["Supplier"],

        "Recommended Quantity": best_supplier["Order Quantity"],

        "Estimated Cost": best_supplier["Total Cost"],

        "Final Risk": best_supplier["Stockout Risk"],

        "Decision Score": best_supplier["Decision Score"],

        "Reliability": best_supplier["Reliability"],

        "Explanation": explanation

    }


# =========================================
# TEST THE STRATEGY ENGINE
# =========================================

def display_strategy(product_id):

    result = evaluate_suppliers(product_id)

    if result is None:

        print("Unable to generate supplier strategy.")

        return

    print("\n======================================")
    print("   INTELLIGENT PROCUREMENT ENGINE")
    print("======================================")

    print("Product:", result["Product"])

    print("\nSUPPLIER EVALUATION")

    print(
        result["Supplier Evaluation"].to_string(
            index=False
        )
    )

    print("\nBEST PROCUREMENT DECISION")

    print(
        "Recommended Supplier:",
        result["Recommended Supplier"]
    )

    print(
        "Supplier Reliability:",
        result["Reliability"],
        "/100"
    )

    print(
        "Recommended Quantity:",
        result["Recommended Quantity"]
    )

    print(
        "Estimated Cost: ₹",
        f"{result['Estimated Cost']:,.2f}"
    )

    print(
        "Stockout Risk:",
        result["Final Risk"]
    )

    print(
        "Decision Score:",
        result["Decision Score"],
        "/100"
    )

    print("\nAGENT EXPLANATION")

    print(result["Explanation"])

    print("\n======================================")


if __name__ == "__main__":

    display_strategy("P101")