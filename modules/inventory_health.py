import pandas as pd


def calculate_inventory_health():

    inventory = pd.read_csv("inventory.csv")

    total_products = len(inventory)

    total_stock = inventory["current_stock"].sum()

    critical_products = len(
        inventory[inventory["current_stock"] < inventory["safety_stock"]]
    )

    healthy_products = total_products - critical_products

    health_percentage = round(
        (healthy_products / total_products) * 100, 2
    ) if total_products > 0 else 0

    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "critical_products": critical_products,
        "healthy_products": healthy_products,
        "health_percentage": health_percentage
    }