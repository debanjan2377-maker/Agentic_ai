from modules.inventory import load_inventory
from modules.demand import calculate_average_demand


def calculate_reorder_quantity(product_id, delivery_days):

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

    average_demand = calculate_average_demand(product_id)

    if average_demand is None:
        return None

    # Expected demand during delivery period
    expected_demand = average_demand * delivery_days

    # Calculate required reorder quantity
    reorder_quantity = max(
        0,
        expected_demand + safety_stock - current_stock
    )

    return {
        "current_stock": current_stock,
        "average_demand": average_demand,
        "expected_demand": expected_demand,
        "safety_stock": safety_stock,
        "reorder_quantity": reorder_quantity
    }


def display_reorder_plan():

    print("\n========== REORDER RECOMMENDATIONS ==========")

    inventory = load_inventory()

    if inventory is None:
        return

    for _, product in inventory.iterrows():

        product_id = product["product_id"]

        # Temporary delivery period for testing
        delivery_days = 5

        result = calculate_reorder_quantity(
            product_id,
            delivery_days
        )

        if result is None:
            continue

        print(f"\nProduct: {product['product_name']}")

        print(
            f"Current Stock: {result['current_stock']}"
        )

        print(
            f"Average Daily Demand: {result['average_demand']}"
        )

        print(
            f"Expected Demand: {result['expected_demand']}"
        )

        print(
            f"Safety Stock: {result['safety_stock']}"
        )

        print(
            f"Recommended Order Quantity: "
            f"{result['reorder_quantity']}"
        )


if __name__ == "__main__":
    display_reorder_plan()