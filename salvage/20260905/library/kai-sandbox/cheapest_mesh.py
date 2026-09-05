# Cheapest possible self-sufficient mesh for Sikeston, MO

# BOM costs
lora_bom = 41  # ESP32 + SX1262 + solar + battery + antenna
dish_bom = 20  # Salvaged dish + USB dongle + mount + PoE cable

# Minimum nodes for Sikeston (42 km²)
nodes_lora = 1
nodes_dish = 1

# Total cost
total_cost = (nodes_lora * lora_bom) + (nodes_dish * dish_bom)

print(f"Cheapest Possible Self-Sufficient Mesh for Sikeston, MO")
print("=" * 60)
print(f"Components:")
print(f"  - LoRa Backbone Nodes: {nodes_lora} x ${lora_bom} = ${nodes_lora * lora_bom}")
print(f"  - Dish Repeaters: {nodes_dish} x ${dish_bom} = ${nodes_dish * dish_bom}")
print(f"\nTotal Cost: ${total_cost}")
print(f"\nDeployment Steps:")
print(f"  1. Deploy {nodes_lora} LoRa backbone node(s) in central Sikeston.")
print(f"  2. Deploy {nodes_dish} dish repeater(s) to extend Wi-Fi coverage.")
print(f"  3. Connect dish repeater(s) to LoRa backbone node(s).")
print(f"  4. Test and optimize coverage.")
