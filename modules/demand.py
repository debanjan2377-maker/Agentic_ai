import pandas as pd


def load_sales():
    try:
        sales = pd.read_csv("sales.csv")
        return sales

    except FileNotFoundError:
        print("Error: sales.csv not found!")
        return None


def calculate_average_demand(product_id):
    sales = load_sales()

    if sales is not None:
        product = sales[sales["product_id"] == product_id]

        if not product.empty:
            daily_sales = product.iloc[0, 2:].astype(float)

            average_demand = daily_sales.mean()

            return round(average_demand, 2)

    return None


def display_demand():
    sales = load_sales()

    if sales is not None:
        print("\n========== DEMAND ANALYSIS ==========")

        for _, row in sales.iterrows():

            product_id = row["product_id"]

            average = calculate_average_demand(product_id)

            print(
                f"{row['product_name']}: "
                f"Average Daily Demand = {average} units"
            )


if __name__ == "__main__":
    display_demand()