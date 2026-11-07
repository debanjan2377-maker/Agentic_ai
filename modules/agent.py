from modules.inventory import load_inventory
from modules.strategy import evaluate_suppliers
from modules.backup import generate_backup_plan
from modules.agent_log import record_agent_activity


# =========================================
# SUPPLYCHAINIQ AUTONOMOUS AI AGENT
# =========================================

def run_supplychain_agent():

    print("\n======================================")
    print("       SUPPLYCHAINIQ AI AGENT")
    print("======================================")

    print("\nAgent started analysing inventory...")

    inventory = load_inventory()

    if inventory is None or inventory.empty:
        print("Unable to load inventory data.")
        return []

    agent_decisions = []

    # =====================================
    # STEP 1: ANALYSE EACH PRODUCT
    # =====================================

    for _, product in inventory.iterrows():

        product_id = product["product_id"]

        result = evaluate_suppliers(product_id)

        if result is None:
            continue

        # =================================
        # STEP 2: GENERATE BACKUP PLAN
        # =================================

        backup = generate_backup_plan(product_id)

        if backup is not None:
            backup_supplier = backup.get(
                "Best Backup Supplier"
            )

            backup_score = backup.get(
                "Backup Decision Score"
            )

            backup_cost = backup.get(
                "Backup Estimated Cost"
            )

            backup_explanation = backup.get(
                "Explanation"
            )

        else:
            backup_supplier = None
            backup_score = None
            backup_cost = None
            backup_explanation = "No backup plan available."

        # =================================
        # STEP 3: COLLECT DECISION
        # =================================

        decision = {

            "Product": result["Product"],

            "Current Stock": result["Current Stock"],

            "Average Demand": result["Average Demand"],

            "Final Risk": result["Final Risk"],

            "Recommended Supplier": result["Recommended Supplier"],

            "Reliability": result["Reliability"],

            "Recommended Quantity": result["Recommended Quantity"],

            "Estimated Cost": result["Estimated Cost"],

            "Decision Score": result["Decision Score"],

            "Backup Supplier": backup_supplier,

            "Backup Decision Score": backup_score,

            "Backup Estimated Cost": backup_cost,

            "Reason": result["Explanation"],

            "Backup Explanation": backup_explanation

        }

        agent_decisions.append(decision)

        # =================================
        # STEP 4: DISPLAY PRIMARY DECISION
        # =================================

        print("\n--------------------------------------")

        print("Product:", decision["Product"])

        print("Current Stock:", decision["Current Stock"])

        print("Average Daily Demand:", decision["Average Demand"])

        print("Stockout Risk:", decision["Final Risk"])

        print(
            "Primary Supplier:",
            decision["Recommended Supplier"]
        )

        print(
            "Supplier Reliability:",
            decision["Reliability"],
            "/100"
        )

        print(
            "Recommended Order Quantity:",
            decision["Recommended Quantity"]
        )

        print(
            "Estimated Procurement Cost: ₹",
            f"{decision['Estimated Cost']:,.2f}"
        )

        print(
            "Decision Score:",
            decision["Decision Score"],
            "/100"
        )

        # =================================
        # STEP 5: DISPLAY BACKUP DECISION
        # =================================

        print("\nBACKUP SUPPLIER PLAN")

        if decision["Backup Supplier"] is not None:

            print(
                "Backup Supplier:",
                decision["Backup Supplier"]
            )

            print(
                "Backup Decision Score:",
                decision["Backup Decision Score"],
                "/100"
            )

            print(
                "Backup Estimated Cost: ₹",
                f"{decision['Backup Estimated Cost']:,.2f}"
            )

            print(decision["Backup Explanation"])

        else:
            print("No alternative supplier available.")

        print("\nPRIMARY DECISION EXPLANATION:")
        print(decision["Reason"])

        # =================================
        # STEP 6: RECORD ACTIVITY
        # =================================

        record_agent_activity(

            product=decision["Product"],

            current_stock=decision["Current Stock"],

            average_demand=decision["Average Demand"],

            stockout_risk=decision["Final Risk"],

            recommended_supplier=decision["Recommended Supplier"],

            recommended_quantity=decision["Recommended Quantity"],

            estimated_cost=decision["Estimated Cost"],

            decision_score=decision["Decision Score"],

            explanation=decision["Reason"],

            reliability=decision["Reliability"],

            backup_supplier=decision["Backup Supplier"],

            backup_score=decision["Backup Decision Score"],

            backup_cost=decision["Backup Estimated Cost"]

        )

    # =====================================
    # STEP 7: GENERATE SUMMARY
    # =====================================

    if not agent_decisions:
        print("\nNo procurement decisions generated.")
        return []

    total_products = len(agent_decisions)

    high_risk = sum(
        1 for item in agent_decisions
        if item["Final Risk"] == "HIGH"
    )

    medium_risk = sum(
        1 for item in agent_decisions
        if item["Final Risk"] == "MEDIUM"
    )

    low_risk = sum(
        1 for item in agent_decisions
        if item["Final Risk"] == "LOW"
    )

    total_cost = sum(
        item["Estimated Cost"]
        for item in agent_decisions
    )

    average_reliability = sum(
        item["Reliability"]
        for item in agent_decisions
    ) / total_products

    # =====================================
    # STEP 8: DISPLAY FINAL SUMMARY
    # =====================================

    print("\n======================================")
    print("       AGENT DECISION SUMMARY")
    print("======================================")

    print("Total Products Analysed:", total_products)

    print("High Risk Products:", high_risk)

    print("Medium Risk Products:", medium_risk)

    print("Low Risk Products:", low_risk)

    print(
        "Average Supplier Reliability:",
        round(average_reliability, 2),
        "/100"
    )

    print(
        "Total Estimated Procurement Cost: ₹",
        f"{total_cost:,.2f}"
    )

    print(
        "Backup Plans Generated:",
        sum(
            1 for item in agent_decisions
            if item["Backup Supplier"] is not None
        )
    )

    print("\nAgent activity successfully recorded.")

    print("\n======================================")
    print("    AGENT ANALYSIS COMPLETED")
    print("======================================")

    return agent_decisions


# =========================================
# MAIN EXECUTION
# =========================================

if __name__ == "__main__":

    run_supplychain_agent()