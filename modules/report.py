import pandas as pd

from modules.inventory import load_inventory
from modules.demand import calculate_average_demand
from modules.supplier import compare_suppliers


def generate_procurement_report():

    inventory = load_inventory()

    if inventory is None:
        return

    report_data = []

    for _, product in inventory.iterrows():

        product_id = product["product_id"]
        product_name = product["product_name"]

        current_stock = float(product["current_stock"])
        safety_stock = float(product["safety_stock"])

        average_demand = calculate_average_demand(product_id)

        suppliers = compare_suppliers(product_id)

        if suppliers is None or suppliers.empty:
            continue

        # Strategy A: Cheapest supplier
        cheapest = suppliers.sort_values(
            by="unit_price"
        ).iloc[0]

        # Strategy B: Fastest supplier
        fastest = suppliers.sort_values(
            by=["delivery_days", "unit_price"]
        ).iloc[0]

        # Calculate reorder quantity for cheapest supplier
        cheapest_demand = (
            average_demand * cheapest["delivery_days"]
        )

        cheapest_quantity = max(
            0,
            cheapest_demand + safety_stock - current_stock
        )

        # Calculate reorder quantity for fastest supplier
        fastest_demand = (
            average_demand * fastest["delivery_days"]
        )

        fastest_quantity = max(
            0,
            fastest_demand + safety_stock - current_stock
        )

        # Calculate procurement costs
        cheapest_cost = (
            cheapest_quantity * cheapest["unit_price"]
        )

        fastest_cost = (
            fastest_quantity * fastest["unit_price"]
        )

        report_data.append({

            "Product": product_name,

            "Current Stock": current_stock,

            "Average Demand": average_demand,

            "Cheapest Supplier": cheapest["supplier_name"],

            "Cheapest Delivery Days": cheapest["delivery_days"],

            "Cheapest Order Quantity": cheapest_quantity,

            "Cheapest Strategy Cost": cheapest_cost,

            "Fastest Supplier": fastest["supplier_name"],

            "Fastest Delivery Days": fastest["delivery_days"],

            "Fastest Order Quantity": fastest_quantity,

            "Fastest Strategy Cost": fastest_cost

        })

    report = pd.DataFrame(report_data)

    report.to_csv(
        "reports/procurement_report.csv",
        index=False
    )

    print("\n========== PROCUREMENT REPORT ==========\n")

    print(report.to_string(index=False))

    print("\nProcurement report generated successfully!")

    print("Saved at: reports/procurement_report.csv")


if __name__ == "__main__":
    generate_procurement_report()