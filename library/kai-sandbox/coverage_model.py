import math

# Sikeston, MO area ~42 km²
sikeston_area = 42

# Dish repeater ranges (km) from RF calc
range_24ghz_24inch = 10  # conservative estimate
range_58ghz_24inch = 7   # higher freq, shorter range

# LoRa backbone range (km)
lora_range = 10

# Coverage area per node (km²)
area_dish_24ghz = math.pi * (range_24ghz_24inch / 2)**2
area_dish_58ghz = math.pi * (range_58ghz_24inch / 2)**2
area_lora = math.pi * (lora_range / 2)**2

# Node density (nodes per km²)
density_dish_24ghz = 1 / area_dish_24ghz
density_dish_58ghz = 1 / area_dish_58ghz
density_lora = 1 / area_lora

# Total nodes for Sikeston
nodes_dish_24ghz = math.ceil(sikeston_area * density_dish_24ghz)
nodes_dish_58ghz = math.ceil(sikeston_area * density_dish_58ghz)
nodes_lora = math.ceil(sikeston_area * density_lora)

print(f"Coverage Model for Sikeston, MO (42 km²)")
print("=" * 50)
print(f"2.4 GHz Dish Repeaters (10 km range):")
print(f"  - Area per node: {area_dish_24ghz:.2f} km²")
print(f"  - Node density: {density_dish_24ghz:.4f} nodes/km²")
print(f"  - Total nodes: {nodes_dish_24ghz}")
print(f"\n5.8 GHz Dish Repeaters (7 km range):")
print(f"  - Area per node: {area_dish_58ghz:.2f} km²")
print(f"  - Node density: {density_dish_58ghz:.4f} nodes/km²")
print(f"  - Total nodes: {nodes_dish_58ghz}")
print(f"\nLoRa Backbone (10 km range):")
print(f"  - Area per node: {area_lora:.2f} km²")
print(f"  - Node density: {density_lora:.4f} nodes/km²")
print(f"  - Total nodes: {nodes_lora}")
