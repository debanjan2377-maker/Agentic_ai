from modules.strategy import evaluate_suppliers


def generate_recommendation_insights(product_id):

    result = evaluate_suppliers(product_id)

    evaluation = result["Supplier Evaluation"]

    best_supplier = evaluation.iloc[0]

    insights = {
        "product": result["Product"],
        "recommended_supplier": result["Recommended Supplier"],
        "reliability": result["Reliability"],
        "delivery_days": best_supplier["Delivery Days"],
        "estimated_cost": result["Estimated Cost"],
        "decision_score": result["Decision Score"],
        "stockout_risk": result["Final Risk"],
        "explanation": result["Explanation"]
    }

    return insights


def display_recommendation_insights(product_id):

    insights = generate_recommendation_insights(product_id)

    print("\n========== SUPPLIER RECOMMENDATION INSIGHTS ==========")

    print("Product:", insights["product"])
    print("Recommended Supplier:", insights["recommended_supplier"])
    print("Reliability:", insights["reliability"], "/100")
    print("Delivery Time:", insights["delivery_days"], "days")
    print("Estimated Procurement Cost: ₹", insights["estimated_cost"])
    print("Decision Score:", insights["decision_score"])
    print("Stockout Risk:", insights["stockout_risk"])
    print("Reason:", insights["explanation"])

    print("======================================================")