# US household telecom spend
us_households = 130_000_000
avg_monthly_spend = 100  # $/month
total_addressable = us_households * avg_monthly_spend * 12

# Payback period
savings_per_month = 80  # $/month
dish_cost = 20  # $/dish
lora_cost = 41  # $/node

# Payback period for dish only
payback_dish = dish_cost / savings_per_month

# Payback period for dish + LoRa node
payback_dish_lora = (dish_cost + lora_cost) / savings_per_month

print(f"Economic Model")
print("=" * 50)
print(f"Total Addressable Market:")
print(f"  - US Households: {us_households:,}")
print(f"  - Avg Monthly Spend: ${avg_monthly_spend}/month")
print(f"  - Total Addressable: ${total_addressable:,.0f}/year")
print(f"\nPayback Period:")
print(f"  - Dish Only: {payback_dish:.1f} months")
print(f"  - Dish + LoRa Node: {payback_dish_lora:.1f} months")
