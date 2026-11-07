import pandas as pd

from modules.strategy import evaluate_suppliers


# =========================================
# SUPPLIER BACKUP PLANNING ENGINE
# =========================================

def generate_backup_plan(product_id):

    # =====================================
    # STEP 1: GET SUPPLIER EVALUATION
    # =====================================

    result = evaluate_suppliers(product_id)

    if result is None:
        return None

    evaluation = result["Supplier Evaluation"].copy()

    primary_supplier = result["Recommended Supplier"]

    # =====================================
    # STEP 2: IDENTIFY BACKUP SUPPLIERS
    # =====================================

    backup_suppliers = evaluation[
        evaluation["Supplier"] != primary_supplier
    ].copy()

    if backup_suppliers.empty:
        return {
            "Product": result["Product"],
            "Primary Supplier": primary_supplier,
            "Backup Suppliers": backup_suppliers,
            "Best Backup Supplier": None,
            "Explanation": "No alternative suppliers are available."
        }

    # =====================================
    # STEP 3: RANK BACKUP SUPPLIERS
    # =====================================

    backup_suppliers = backup_suppliers.sort_values(
        by=[
            "Decision Score",
            "Reliability",
            "Delivery Days",
            "Total Cost"
        ],
        ascending=[False, False, True, True]
    ).reset_index(drop=True)

    # =====================================
    # STEP 4: SELECT BEST BACKUP
    # =====================================

    best_backup = backup_suppliers.iloc[0]

    # =====================================
    # STEP 5: GENERATE EXPLANATION
    # =====================================

    explanation = (

        f"If {primary_supplier} becomes unavailable, "

        f"{best_backup['Supplier']} is the recommended "
        f"backup supplier. "

        f"It has a decision score of "
        f"{best_backup['Decision Score']}/100, "

        f"a reliability score of "
        f"{best_backup['Reliability']}/100, "

        f"and a delivery time of "
        f"{int(best_backup['Delivery Days'])} days."

    )

    # =====================================
    # STEP 6: RETURN BACKUP PLAN
    # =====================================

    return {

        "Product": result["Product"],

        "Primary Supplier": primary_supplier,

        "Backup Suppliers": backup_suppliers,

        "Best Backup Supplier": best_backup["Supplier"],

        "Backup Reliability": best_backup["Reliability"],

        "Backup Delivery Days": best_backup["Delivery Days"],

        "Backup Order Quantity": best_backup["Order Quantity"],

        "Backup Estimated Cost": best_backup["Total Cost"],

        "Backup Decision Score": best_backup["Decision Score"],

        "Explanation": explanation

    }


# =========================================
# DISPLAY BACKUP PLAN
# =========================================

def display_backup_plan(product_id):

    result = generate_backup_plan(product_id)

    if result is None:

        print("Unable to generate backup plan.")

        return

    print("\n======================================")
    print("       SUPPLIER BACKUP PLANNING")
    print("======================================")

    print("Product:", result["Product"])

    print(
        "\nPrimary Supplier:",
        result["Primary Supplier"]
    )

    print("\nBACKUP SUPPLIER EVALUATION")

    print(
        result["Backup Suppliers"][
            [
                "Supplier",
                "Delivery Days",
                "Reliability",
                "Order Quantity",
                "Total Cost",
                "Decision Score"
            ]
        ].to_string(index=False)
    )

    print("\nBEST BACKUP SUPPLIER")

    if result["Best Backup Supplier"] is None:

        print("No alternative supplier available.")

        print(result["Explanation"])

        return

    print(
        "Recommended Backup:",
        result["Best Backup Supplier"]
    )

    print(
        "Reliability:",
        result["Backup Reliability"],
        "/100"
    )

    print(
        "Delivery Days:",
        result["Backup Delivery Days"]
    )

    print(
        "Backup Order Quantity:",
        result["Backup Order Quantity"]
    )

    print(
        "Estimated Backup Cost: ₹",
        f"{result['Backup Estimated Cost']:,.2f}"
    )

    print(
        "Decision Score:",
        result["Backup Decision Score"],
        "/100"
    )

    print("\nBACKUP DECISION EXPLANATION")

    print(result["Explanation"])

    print("\n======================================")


# =========================================
# MAIN EXECUTION
# =========================================

if __name__ == "__main__":

    display_backup_plan("P101")