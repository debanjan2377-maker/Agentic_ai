import os
import json
import requests
import pandas as pd

from modules.purchase_order import generate_purchase_order
from dotenv import load_dotenv
from modules.strategy import evaluate_suppliers


# =========================================
# CONFIGURATION
# =========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.5-flash-lite"

API_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/" + MODEL + ":generateContent"
)


# =========================================
# LOAD PROJECT DATA
# =========================================

def load_inventory():

    return pd.read_csv(
        os.path.join(BASE_DIR, "inventory.csv")
    )


def load_sales():

    return pd.read_csv(
        os.path.join(BASE_DIR, "sales.csv")
    )


def find_product(product_name):

    inventory = load_inventory()

    matches = inventory[
        inventory["product_name"].str.lower()
        == product_name.lower()
    ]

    if matches.empty:
        raise ValueError("Product not found.")

    return matches.iloc[0]


# =========================================
# TOOL 1: INVENTORY ANALYSIS
# =========================================

def inventory_analysis(product_name):

    product = find_product(product_name)

    sales = load_sales()

    sales_row = sales[
        sales["product_id"] == product["product_id"]
    ]

    if sales_row.empty:
        raise ValueError("Sales data not found.")

    day_columns = [
        col for col in sales.columns
        if col.startswith("day_")
    ]

    average_demand = float(
        sales_row[day_columns].iloc[0].mean()
    )

    current_stock = float(product["current_stock"])

    safety_stock = float(product["safety_stock"])

    return {
        "product": product_name,
        "current_stock": current_stock,
        "safety_stock": safety_stock,
        "average_daily_demand": average_demand,
        "stock_coverage_days": (
            current_stock / average_demand
            if average_demand > 0 else None
        )
    }


# =========================================
# TOOL 2: DEMAND FORECAST
# =========================================

def demand_forecast(product_name):

    product = find_product(product_name)

    sales = load_sales()

    sales_row = sales[
        sales["product_id"] == product["product_id"]
    ]

    if sales_row.empty:
        raise ValueError("Sales data not found.")

    day_columns = [
        col for col in sales.columns
        if col.startswith("day_")
    ]

    average = float(
        sales_row[day_columns].iloc[0].mean()
    )

    return {
        "product": product_name,
        "average_daily_demand": average,
        "forecast_period": "7 days",
        "forecast": [round(average, 2)] * 7,
        "total_forecast": round(average * 7, 2),
        "method": "Seven-day historical average"
    }


# =========================================
# TOOL 3: SUPPLIER EVALUATION
# =========================================

def supplier_evaluation(product_name):

    product = find_product(product_name)

    result = evaluate_suppliers(
        product["product_id"]
    )

    evaluation = result.get("Supplier Evaluation")

    if isinstance(evaluation, pd.DataFrame):
        evaluation = evaluation.to_dict(
            orient="records"
        )

    return {
        "product": product_name,
        "recommended_supplier": result.get(
            "Recommended Supplier"
        ),
        "recommended_quantity": result.get(
            "Recommended Quantity"
        ),
        "estimated_cost": result.get(
            "Estimated Cost"
        ),
        "decision_score": result.get(
            "Decision Score"
        ),
        "risk": result.get("Final Risk"),
        "supplier_comparison": evaluation
    }


# =========================================
# TOOL 4: COMPLETE INVENTORY OVERVIEW
# =========================================

def complete_inventory_overview():

    inventory = load_inventory()

    sales = load_sales()

    results = []

    for _, product in inventory.iterrows():

        sales_row = sales[
            sales["product_id"] == product["product_id"]
        ]

        day_columns = [
            col for col in sales.columns
            if col.startswith("day_")
        ]

        average = float(
            sales_row[day_columns].iloc[0].mean()
        )

        results.append({

            "product": product["product_name"],

            "current_stock": float(
                product["current_stock"]
            ),

            "safety_stock": float(
                product["safety_stock"]
            ),

            "average_daily_demand": average,

            "coverage_days": (
                float(product["current_stock"]) / average
                if average > 0 else None
            )

        })

    return {
        "total_products": len(results),
        "inventory": results
    }


# =========================================
# TOOL DEFINITIONS
# =========================================

TOOLS = [

    {
        "name": "inventory_analysis",
        "description": "Analyse the stock, safety stock, daily demand and stock coverage of a product.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "product_name": {
                    "type": "STRING",
                    "description": "Product name such as Laptop or Mouse"
                }
            },
            "required": ["product_name"]
        }
    },

    {
        "name": "demand_forecast",
        "description": "Forecast the next seven days of product demand using historical sales.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "product_name": {
                    "type": "STRING",
                    "description": "Product name"
                }
            },
            "required": ["product_name"]
        }
    },

    {
        "name": "supplier_evaluation",
        "description": "Evaluate available suppliers and return the recommended supplier, decision score, cost and risk.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "product_name": {
                    "type": "STRING",
                    "description": "Product name"
                }
            },
            "required": ["product_name"]
        }
    },

    {
        "name": "complete_inventory_overview",
        "description": "Analyse inventory levels and demand for all products.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    }

    ,
    {
        "name": "generate_purchase_order",
        "description": "Generate and save a purchase order draft only after the customer explicitly requests one. Never place or submit an actual order.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "supplier_name": {
                    "type": "STRING",
                    "description": "Supplier name, such as QuickTech"
                },
                "product_name": {
                    "type": "STRING",
                    "description": "Product name, such as Laptop"
                },
                "quantity": {
                    "type": "INTEGER",
                    "description": "Number of units to order"
                },
                "unit_price": {
                    "type": "NUMBER",
                    "description": "Supplier unit price in INR"
                },
                "delivery_days": {
                    "type": "INTEGER",
                    "description": "Estimated supplier delivery time in days"
                }
            },
            "required": [
                "supplier_name",
                "product_name",
                "quantity",
                "unit_price",
                "delivery_days"
            ]
        }
    }
]


# =========================================
# TOOL EXECUTION
# =========================================

AVAILABLE_TOOLS = {
    "inventory_analysis": inventory_analysis,
    "demand_forecast": demand_forecast,
    "supplier_evaluation": supplier_evaluation,
    "complete_inventory_overview": complete_inventory_overview,
    "generate_purchase_order": generate_purchase_order
}


# =========================================
# GEMINI API REQUEST
# =========================================

def call_gemini(contents):

    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    payload = {

        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are SupplyChainIQ, an intelligent "
                    "supply chain decision agent. "
                    "Understand the user's request and decide "
                    "which available tools to call. "
                    "Use actual tool results when making "
                    "recommendations. Never invent inventory "
                    "or supplier information. "
                    "Explain your decisions clearly. "
                    "Do not claim that an order was placed. "
                    "All procurement actions are recommendations "
                    "requiring human approval."
                )
            }]
        },"systemInstruction": {
    "parts": [{
        "text": (
            "You are SupplyChainIQ, an autonomous supply chain "
            "decision support agent. "

            "IMPORTANT RULES: "

            "1. Always use available tools to retrieve actual "
            "inventory, demand and supplier information. "

            "2. Never invent stock quantities, supplier capacity, "
            "delivery commitments or reliability values. "

            "3. Calculate recommended order quantity using "
            "the actual inventory and supplier lead time. "

            "4. Use Indian Rupees (₹) for every monetary value. "
            "Never use dollars ($). "

            "5. Supplier reliability scores are estimates from "
            "the supplied dataset, not guaranteed performance. "

            "6. Supplier capacity and available inventory are "
            "unknown unless explicitly provided by a tool. "
            "Never claim that a supplier can fulfil an order "
            "without verified capacity information. "

            "7. Clearly explain supplier selection using "
            "decision scores, price, delivery time and reliability. "

            "8. Distinguish between inventory risk and stock "
            "coverage. Explain the reason for each risk assessment. "

            "9. Never change, approximate or invent numerical values "
"returned by tools. Preserve exact quantities, prices, "
"decision scores and costs. Before presenting total cost, "
"verify that unit price multiplied by order quantity equals "
"the reported total cost. Use Indian number formatting, "
"such as ₹6,30,000. "
            "10. Never claim that a purchase order was created, "
            "an order was placed or goods were dispatched. "

            "11. All procurement recommendations require "
            "human approval. "

            "12. Be transparent about missing information "
            "and calculation assumptions. "
"13. Never confuse current stock with safety stock. "
"Always compare the actual numerical values correctly. "
"If current stock is greater than safety stock, never "
"describe it as below the safety stock threshold. "
"Explain stockout risk separately using expected demand "
"during supplier lead time and available inventory. "
"Never claim that a purchase order has been created "
"unless the system has actually generated one. "
"Do not ask the customer to approve an existing purchase "
"order when none exists. Instead, ask whether they want "
"to generate a purchase order draft for review. "
"Never claim that an order has been placed or submitted."

            "Your objective is to provide accurate, explainable "
            "and actionable supply chain recommendations."
        )
    }]
},

        "contents": contents,

        "tools": [{
            "functionDeclarations": TOOLS
        }]

    }

    response = requests.post(

        API_URL,

        params={"key": API_KEY},

        json=payload,

        timeout=60

    )

    if response.status_code != 200:

        raise RuntimeError(
            "Gemini API error: " + response.text[:1000]
        )

    return response.json()


# =========================================
# AUTONOMOUS AGENT
# =========================================

def run_llm_agent(user_query):

    contents = [

        {
            "role": "user",

            "parts": [{
                "text": user_query
            }]
        }

    ]

    activity = []

    for round_number in range(5):

        response = call_gemini(contents)

        candidates = response.get(
            "candidates", []
        )

        if not candidates:
            raise RuntimeError(
                "Gemini returned no response candidates."
            )

        candidate_content = candidates[0]["content"]

        contents.append(candidate_content)

        parts = candidate_content.get("parts", [])

        function_calls = [

            part["functionCall"]

            for part in parts

            if "functionCall" in part

        ]

        if not function_calls:

            final_text = "\n".join(

                part["text"]

                for part in parts

                if "text" in part

            )

            return {

                "answer": final_text,

                "activity": activity,

                "tool_calls": len(activity)

            }

        for function_call in function_calls:

            name = function_call["name"]

            arguments = function_call.get(
                "args", {}
            )

            if name not in AVAILABLE_TOOLS:

                result = {
                    "error": "Unknown tool requested."
                }

            else:

                try:

                    result = AVAILABLE_TOOLS[name](
                        **arguments
                    )

                except Exception as error:

                    result = {
                        "error": str(error)
                    }

            activity.append({

                "tool": name,

                "arguments": arguments,

                "result": result

            })

            contents.append({

                "role": "user",

                "parts": [{

                    "functionResponse": {

                        "name": name,

                        "response": {
                            "result": result
                        }

                    }

                }]

            })

    raise RuntimeError(
        "Agent reached its five-round tool limit."
    )