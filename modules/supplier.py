import pandas as pd


def load_suppliers():

    try:
        suppliers = pd.read_csv("suppliers.csv")
        return suppliers

    except FileNotFoundError:
        print("Error: suppliers.csv not found!")
        return None


def compare_suppliers(product_id):

    suppliers = load_suppliers()

    if suppliers is None:
        return None

    product_suppliers = suppliers[
        suppliers["product_id"] == product_id
    ].copy()

    if product_suppliers.empty:
        print("No suppliers found for this product.")
        return None

    product_suppliers["unit_price"] = pd.to_numeric(
        product_suppliers["unit_price"]
    )

    product_suppliers["delivery_days"] = pd.to_numeric(
        product_suppliers["delivery_days"]
    )

    # Sort suppliers by price
    product_suppliers = product_suppliers.sort_values(
        by="unit_price"
    )

    return product_suppliers


def display_supplier_comparison():

    print("\n========== SUPPLIER COMPARISON ==========")

    suppliers = load_suppliers()

    if suppliers is None:
        return

    for product_id in suppliers["product_id"].unique():

        comparison = compare_suppliers(product_id)

        if comparison is not None:

            product_name = comparison.iloc[0]["product_name"]

            print(f"\nProduct: {product_name}")

            print(
                comparison[
                    [
                        "supplier_name",
                        "unit_price",
                        "delivery_days"
                    ]
                ].to_string(index=False)
            )

            cheapest = comparison.iloc[0]

            fastest = comparison.sort_values(
                by="delivery_days"
            ).iloc[0]

            print(
                f"Cheapest Supplier: {cheapest['supplier_name']}"
            )

            print(
                f"Fastest Supplier: {fastest['supplier_name']}"
            )


if __name__ == "__main__":
    display_supplier_comparison()