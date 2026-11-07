from datetime import datetime
import os
import pandas as pd


def generate_purchase_order(
    supplier_name,
    product_name,
    quantity,
    unit_price,
    delivery_days
):

    quantity = int(quantity)
    unit_price = float(unit_price)
    delivery_days = int(delivery_days)

    if quantity <= 0 or unit_price <= 0:
        raise ValueError("Quantity and price must be positive.")

    total_cost = quantity * unit_price

    folder = "reports"
    os.makedirs(folder, exist_ok=True)

    po_number = "DRAFT-PO-" + datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    order = {
        "PO Number": po_number,
        "Date": datetime.now().strftime("%d-%m-%Y"),
        "Status": "DRAFT - PENDING HUMAN APPROVAL",
        "Supplier": supplier_name,
        "Product": product_name,
        "Quantity": quantity,
        "Unit Price": unit_price,
        "Total Cost": total_cost,
        "Delivery Days": delivery_days,
        "Note": "Draft only. No order has been placed."
    }

    file_path = os.path.join(
        folder,
        po_number + ".csv"
    )

    pd.DataFrame([order]).to_csv(
        file_path,
        index=False
    )

    return {
        "message": "Purchase order draft generated successfully.",
        "purchase_order": order,
        "file": file_path
    }


def update_purchase_order_status(file_path, new_status):

    if new_status not in ["APPROVED", "REJECTED"]:
        raise ValueError("Invalid purchase order status.")

    if not os.path.exists(file_path):
        raise FileNotFoundError("Purchase order file not found.")

    df = pd.read_csv(file_path)

    df["Status"] = new_status

    df["Note"] = (
        "Human decision recorded. "
        "No actual supplier order has been placed."
    )

    df.to_csv(file_path, index=False)

    # Record approval history
    log_file = os.path.join(
        "reports",
        "po_approval_log.csv"
    )

    approval_record = {
        "PO Number": df.iloc[0]["PO Number"],
        "Supplier": df.iloc[0]["Supplier"],
        "Product": df.iloc[0]["Product"],
        "Decision": new_status,
        "Decision Date": datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )
    }

    log_df = pd.DataFrame([approval_record])

    if os.path.exists(log_file):
        log_df.to_csv(
            log_file,
            mode="a",
            header=False,
            index=False
        )
    else:
        log_df.to_csv(log_file, index=False)

    return {
        "message": "Purchase order status updated successfully.",
        "status": new_status,
        "file": file_path
    }