import json, datetime

def route_expense(amount, category, description):
    # Logic: Maps expense to the best tax code/credit line
    # 0: Personal, 1: LLC OpEx, 2: Grant R&D (Tax Credit)
    mapping = {
        "hardware": 2, 
        "electricity": 1,
        "fuel": 1,
        "software": 2
    }
    tier = mapping.get(category, 0)
    print(f"[finance] ${amount} ({description}) routed to Tier {tier}. Maximizing tax write-off.")
    return tier

if __name__ == "__main__":
    # Example: Route a new hardware purchase
    route_expense(500, "hardware", "New OptiPlex for Pod-Garden")
