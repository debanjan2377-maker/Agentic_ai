import pandas as pd


def calculate_stock_coverage():

    inventory = pd.read_csv("inventory.csv")
    sales = pd.read_csv("sales.csv")

    day_columns = [
        "day_1", "day_2", "day_3",
        "day_4", "day_5", "day_6", "day_7"
    ]

    sales["Average Daily Demand"] = sales[day_columns].mean(axis=1)

    coverage = pd.merge(
        inventory,
        sales[["product_id", "Average Daily Demand"]],
        on="product_id"
    )

    coverage["Days of Stock Remaining"] = (
        coverage["current_stock"] /
        coverage["Average Daily Demand"]
    ).round(2)

    def get_status(days):

        if days <= 2:
            return "CRITICAL"
        elif days <= 5:
            return "LOW"
        else:
            return "HEALTHY"

    coverage["Inventory Status"] = (
        coverage["Days of Stock Remaining"].apply(get_status)
    )

    return coverage[
        [
            "product_name",
            "current_stock",
            "Average Daily Demand",
            "Days of Stock Remaining",
            "Inventory Status"
        ]
    ]