from modules.inventory import load_inventory
from modules.demand import calculate_average_demand


def calculate_stockout_risk(product_id, delivery_days):

    inventory = load_inventory()

    if inventory is None:
        return None

    product = inventory[
        inventory["product_id"] == product_id
    ]

    if product.empty:
        return None

    # Convert stock values into numeric data
    current_stock = float(product.iloc[0]["current_stock"])

    safety_stock = float(product.iloc[0]["safety_stock"])

    # Calculate average daily demand
    average_demand = calculate_average_demand(product_id)

    if average_demand is None:
        return None

    # Calculate expected demand during delivery time
    expected_demand = average_demand * delivery_days

    # Determine stockout risk
    if current_stock < expected_demand:
        risk = "HIGH"

    elif current_stock <= expected_demand + safety_stock:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return {
        "current_stock": current_stock,
        "average_demand": average_demand,
        "expected_demand": expected_demand,
        "delivery_days": delivery_days,
        "safety_stock": safety_stock,
        "risk": risk
    }


def display_stockout_risk():

    print("\n========== STOCKOUT RISK ANALYSIS ==========")

    inventory = load_inventory()

    if inventory is None:
        return

    for _, product in inventory.iterrows():

        product_id = product["product_id"]

        # Temporary delivery time for testing
        delivery_days = 5

        result = calculate_stockout_risk(
            product_id, delivery_days
        )

        if result is None:
            continue

        print(f"\nProduct: {product['product_name']}")
        print(f"Current Stock: {result['current_stock']}")
        print(f"Average Daily Demand: {result['average_demand']}")
        print(f"Expected Demand: {result['expected_demand']}")
        print(f"Delivery Days: {result['delivery_days']}")
        print(f"Safety Stock: {result['safety_stock']}")
        print(f"Stockout Risk: {result['risk']}")


if __name__ == "__main__":
    display_stockout_risk()