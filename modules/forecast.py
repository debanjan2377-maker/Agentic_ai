import pandas as pd


def forecast_product_demand(product_id):

    sales = pd.read_csv("sales.csv")

    product = sales[sales["product_id"] == product_id]

    if product.empty:
        return None

    day_columns = [
        "day_1", "day_2", "day_3",
        "day_4", "day_5", "day_6", "day_7"
    ]

    daily_sales = product[day_columns].iloc[0]

    average_demand = daily_sales.mean()

    forecast = []

    for day in range(1, 8):

        forecast.append({
            "Day": f"Future Day {day}",
            "Forecasted Demand": round(average_demand, 2)
        })

    forecast_df = pd.DataFrame(forecast)

    return {
        "product": product["product_name"].iloc[0],
        "average_demand": round(average_demand, 2),
        "total_forecast": round(average_demand * 7, 2),
        "forecast": forecast_df
    }