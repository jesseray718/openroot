import math

# Sikeston, MO area ~42 km²
sikeston_area = 42

# Scaling factors
scott_county_area = 1133  # km²
missouri_area = 180540   # km²
conus_area = 9833517     # km²

# Node density (nodes per km²)
density_dish_24ghz = 0.0127

# Total nodes for each region
nodes_scott_county = math.ceil(scott_county_area * density_dish_24ghz)
nodes_missouri = math.ceil(missouri_area * density_dish_24ghz)
nodes_conus = math.ceil(conus_area * density_dish_24ghz)

# BOM cost per node
dish_bom = 20

# Total cost for each region
cost_scott_county = nodes_scott_county * dish_bom
cost_missouri = nodes_missouri * dish_bom
cost_conus = nodes_conus * dish_bom

print(f"Fractal Scaling with 2.4 GHz Dish Repeaters")
print("=" * 50)
print(f"Scott County, MO (1133 km²):")
print(f"  - Total nodes: {nodes_scott_county}")
print(f"  - Total cost: ${cost_scott_county:,}")
print(f"\nMissouri (180,540 km²):")
print(f"  - Total nodes: {nodes_missouri}")
print(f"  - Total cost: ${cost_missouri:,}")
print(f"\nCONUS (9,833,517 km²):")
print(f"  - Total nodes: {nodes_conus}")
print(f"  - Total cost: ${cost_conus:,}")
