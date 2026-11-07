import os
import pandas as pd
from datetime import datetime


# =========================================
# AGENT LOG CONFIGURATION
# =========================================

LOG_FOLDER = "reports"
LOG_FILE = os.path.join(
    LOG_FOLDER,
    "agent_activity_log.csv"
)


# =========================================
# CREATE LOG DIRECTORY
# =========================================

def create_log_directory():

    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)


# =========================================
# RECORD AGENT ACTIVITY
# =========================================

def record_agent_activity(
    product,
    current_stock,
    average_demand,
    stockout_risk,
    recommended_supplier,
    recommended_quantity,
    estimated_cost,
    decision_score,
    explanation,
    reliability=None,
    backup_supplier=None,
    backup_score=None,
    backup_cost=None
):

    create_log_directory()

    activity = {

        "Timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "Product": product,

        "Current Stock": current_stock,

        "Average Daily Demand": average_demand,

        "Stockout Risk": stockout_risk,

        "Primary Supplier": recommended_supplier,

        "Supplier Reliability": reliability,

        "Recommended Quantity": recommended_quantity,

        "Estimated Procurement Cost": estimated_cost,

        "Decision Score": decision_score,

        "Backup Supplier": backup_supplier,

        "Backup Decision Score": backup_score,

        "Backup Estimated Cost": backup_cost,

        "Decision Explanation": explanation

    }

    new_record = pd.DataFrame([activity])

    if os.path.exists(LOG_FILE):

        existing_records = pd.read_csv(LOG_FILE)

        updated_records = pd.concat(
            [existing_records, new_record],
            ignore_index=True
        )

    else:

        updated_records = new_record

    updated_records.to_csv(
        LOG_FILE,
        index=False
    )

    return True


# =========================================
# LOAD AGENT ACTIVITY HISTORY
# =========================================

def load_agent_logs():

    create_log_directory()

    if os.path.exists(LOG_FILE):

        return pd.read_csv(LOG_FILE)

    return pd.DataFrame()


# =========================================
# DISPLAY AGENT ACTIVITY HISTORY
# =========================================

def display_agent_logs():

    logs = load_agent_logs()

    print("\n======================================")
    print("       AGENT ACTIVITY HISTORY")
    print("======================================")

    if logs.empty:

        print("No agent activity recorded yet.")

        return

    print(logs.to_string(index=False))

    print("\nTotal Activities Recorded:", len(logs))


# =========================================
# CLEAR AGENT ACTIVITY HISTORY
# =========================================

def clear_agent_logs():

    if os.path.exists(LOG_FILE):

        os.remove(LOG_FILE)

        print("Agent activity history cleared.")

    else:

        print("No activity history found.")


# =========================================
# MAIN EXECUTION
# =========================================

if __name__ == "__main__":

    display_agent_logs()