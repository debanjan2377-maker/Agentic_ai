import pandas as pd


def load_inventory():
    try:
        inventory = pd.read_csv("inventory.csv")
        return inventory

    except FileNotFoundError:
        print("Error: inventory.csv not found!")
        return None


def get_product_stock(product_id):
    inventory = load_inventory()

    if inventory is not None:
        product = inventory[
            inventory["product_id"] == product_id
        ]

        if not product.empty:
            return product.iloc[0]["current_stock"]

    return None


def display_inventory():
    inventory = load_inventory()

    if inventory is not None:
        print("\n========== INVENTORY DETAILS ==========")
        print(inventory.to_string(index=False))


if __name__ == "__main__":
    display_inventory()