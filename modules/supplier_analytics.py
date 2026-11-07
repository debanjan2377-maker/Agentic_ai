import pandas as pd


def calculate_supplier_performance():

    suppliers = pd.read_csv("suppliers.csv")

    performance = suppliers.groupby("supplier_name").agg(
        Total_Products=("product_id", "count"),
        Average_Reliability=("reliability_score", "mean"),
        Average_Delivery_Days=("delivery_days", "mean"),
        Average_Unit_Price=("unit_price", "mean")
    ).reset_index()

    performance = performance.sort_values(
        by="Average_Reliability",
        ascending=False
    )

    return performance