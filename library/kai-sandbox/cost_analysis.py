# BOM costs
lora_bom = 41  # ESP32 + SX1262 + solar + battery + antenna
dish_bom = 20  # Salvaged dish + USB dongle + mount + PoE cable

# Sikeston coverage nodes
nodes_lora = 1
nodes_dish_24ghz = 1
nodes_dish_58ghz = 2

# Total cost for Sikeston
cost_lora_only = nodes_lora * lora_bom
cost_dish_24ghz = nodes_dish_24ghz * dish_bom
cost_dish_58ghz = nodes_dish_58ghz * dish_bom

print(f"Cost Analysis for Sikeston, MO")
print("=" * 50)
print(f"LoRa Backbone Only:")
print(f"  - Total cost: ${cost_lora_only}")
print(f"\n2.4 GHz Dish Repeaters:")
print(f"  - Total cost: ${cost_dish_24ghz}")
print(f"\n5.8 GHz Dish Repeaters:")
print(f"  - Total cost: ${cost_dish_58ghz}")

# Cost per km²
cost_per_km2_lora = cost_lora_only / 42
cost_per_km2_dish_24ghz = cost_dish_24ghz / 42
cost_per_km2_dish_58ghz = cost_dish_58ghz / 42

print(f"\nCost per km²:")
print(f"  - LoRa Only: ${cost_per_km2_lora:.2f}/km²")
print(f"  - 2.4 GHz Dish: ${cost_per_km2_dish_24ghz:.2f}/km²")
print(f"  - 5.8 GHz Dish: ${cost_per_km2_dish_58ghz:.2f}/km²")
