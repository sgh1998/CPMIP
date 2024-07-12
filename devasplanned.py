import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.placement
import ifcopenshell.util.element
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yaml
import os

def load_config(config_file="user.yaml"):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_full_path(major_folder, relative_path):
    return os.path.join(major_folder, relative_path)

# Load configuration
config = load_config()
major_folder = config['major_folder']
paths = config['paths']

# Construct full paths from the major folder and relative paths
ifc_file_path = get_full_path(major_folder, paths['ifc_model'])
east_txt_path = get_full_path(major_folder, paths['east_txt_path'])
west_txt_path = get_full_path(major_folder, paths['west_txt_path'])
north_txt_path = get_full_path(major_folder, paths['north_txt_path'])
south_txt_path = get_full_path(major_folder, paths['south_txt_path'])
view_direction = config['view_direction'].strip().lower()  # Read view direction from config

# Extract and Calculate coordinates for columns
ifc_file = ifcopenshell.open(ifc_file_path)

# Get all elements in a container
for storey in ifc_file.by_type("IfcBuildingStorey"):
    elements = ifcopenshell.util.element.get_decomposition(storey)
    print(f"There are {len(elements)} located on storey {storey.Name}, they are:")
    for element in elements:
        print(element.Name)

columns = ifc_file.by_type("IfcColumn")
print("Number of columns is:", len(columns))

verts_list = []
relative_list = []
local_list = []
mixed_list = []

for column in columns:
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, column)

    column_info = {
        'IfcID': column.id(),
        'Name': column.Name if hasattr(column, 'Name') else None,
        'Global ID': column.GlobalId,
    }
    
    container = ifcopenshell.util.element.get_container(column)
    container_name = container.Name
    level_number = int(container_name.split()[-1])

    verts = shape.geometry.verts
    organized_verts = [(verts[i], verts[i+1], verts[i+2]) for i in range(0, len(verts), 3)] # 8 points

    points = organized_verts
    z_coordinates = [point[2] for point in points]
    Ztop = round(max(z_coordinates), 2)
    Zbot = round(min(z_coordinates), 2)
    Height = Ztop - Zbot

    matrix = ifcopenshell.util.placement.get_local_placement(column.ObjectPlacement)
    placement = column.ObjectPlacement
    coordinates = placement.RelativePlacement.Location.Coordinates if placement and hasattr(placement, 'RelativePlacement') and placement.RelativePlacement else []

    mixed = [matrix[:,3][:3][0], matrix[:,3][:3][1], Ztop, Zbot, level_number]   

    verts_list.append(list(verts))
    relative_list.append(list(coordinates))
    local_list.append(list(matrix[:,3][:3]))
    mixed_list.append(mixed)

df_verts = pd.DataFrame(verts_list)
df_relative = pd.DataFrame(relative_list)
df_local = pd.DataFrame(local_list)
df_mixed = pd.DataFrame(mixed_list)

merged_df = pd.concat([df_relative, df_local, df_mixed], axis=1)
merged_df.columns = ["Rx", "Ry", "Rz", "Lx", "Ly", "Lz", "Mx", "My", "Mztop", "Mzbot", "Level"]
print(merged_df)

def round_list(lst, decimal_places=5):
    return [[round(num, decimal_places) for num in sublist] for sublist in lst]

rounded_mixed_list = round_list(mixed_list, decimal_places=2) # x y ztop zbot level

print("This is rounded mixed list:")        
for item in rounded_mixed_list:
    print(item)

max_x = max(col[0] for col in rounded_mixed_list)
print("max X is:", max_x)
outlier_east_col = [coord for coord in rounded_mixed_list if coord[0] == max_x]

min_x = min(col[0] for col in rounded_mixed_list)
print("min X is:", min_x)
outlier_west_col = [coord for coord in rounded_mixed_list if coord[0] == min_x]

max_y = max(col[1] for col in rounded_mixed_list)
print("max Y is:", max_y)
outlier_north_col = [coord for coord in rounded_mixed_list if coord[1] == max_y]

min_y = min(coord[1] for coord in rounded_mixed_list)
print("min Y is:", min_y)
outlier_south_col = [coord for coord in rounded_mixed_list if coord[1] == min_y]

print("\n" * 3)
print("These are primary results:")

print("Outlier East:", outlier_east_col)
print("number of East col:", len(outlier_east_col))
print("\n" * 1)

print("Outlier West:", outlier_west_col)
print("number of West col:", len(outlier_west_col))

print("\n" * 1)

print("Outlier North:", outlier_north_col)
print("number of North col:", len(outlier_north_col))

print("\n" * 1)

print("Outlier South:", outlier_south_col)
print("number of South col:", len(outlier_south_col))

print("\n" * 1)

print("TOTAL number of Columns", len(ifc_file.by_type('IfcColumn')))

def save_to_file(filename, data):
    with open(filename, 'w') as file:
        for entry in data:
            file.write(', '.join(map(str, entry)) + '\n')

#save_to_file(east_txt_path, outlier_east_col)
#save_to_file(west_txt_path, outlier_west_col)
#save_to_file(north_txt_path, outlier_north_col)
#save_to_file(south_txt_path, outlier_south_col)


# transform coordinates for east
e_transformed_coord = []
e_xmax = max(col[0] for col in outlier_east_col)
e_ymax = max(col[1] for col in outlier_east_col)
print(e_xmax)
print(e_ymax)
for col in outlier_east_col:
    x , y , zt, zb, l = col
    xt_transformed = y
    yt_transformed = zt
    xb_transformed = y
    yb_transformed = zb
    e_transformed_coord.append([xt_transformed, yt_transformed, xb_transformed, yb_transformed, l])
print(e_transformed_coord)

# transform coordinates for west
w_transformed_coord = []
w_xmax = max(col[0] for col in outlier_west_col)
w_ymax = max(col[1] for col in outlier_west_col)
print(w_xmax)
print(w_ymax)
for col in outlier_west_col:
    x , y , zt, zb, l = col
    xt_transformed = w_ymax-y
    yt_transformed = zt
    xb_transformed = w_ymax-y
    yb_transformed = zb
    w_transformed_coord.append([xt_transformed, yt_transformed, xb_transformed, yb_transformed, l])
print(w_transformed_coord)

# transform coordinates for north
n_transformed_coord = []
n_xmax = max(col[0] for col in outlier_north_col)
n_ymax = max(col[1] for col in outlier_north_col)
print(n_xmax)
print(n_ymax)
for col in outlier_north_col:
    x , y , zt, zb, l = col
    xt_transformed = n_xmax-x
    yt_transformed = zt
    xb_transformed = n_xmax-x
    yb_transformed = zb
    n_transformed_coord.append([xt_transformed, yt_transformed, xb_transformed, yb_transformed, l])
print(n_transformed_coord)

# transform coordinates for south
s_transformed_coord = []
s_xmax = max(col[0] for col in outlier_south_col)
s_ymax = max(col[1] for col in outlier_south_col)
print(s_xmax)
print(s_ymax)
for col in outlier_south_col:
    x , y , zt, zb, l = col
    xt_transformed = x
    yt_transformed = zt
    xb_transformed = x
    yb_transformed = zb
    s_transformed_coord.append([xt_transformed, yt_transformed, xb_transformed, yb_transformed, l])
print(s_transformed_coord)


save_to_file(east_txt_path, e_transformed_coord)
save_to_file(west_txt_path, w_transformed_coord)
save_to_file(north_txt_path, n_transformed_coord)
save_to_file(south_txt_path, s_transformed_coord)




# Draft section
'''
# convert coordinates based on viewpoint
def transform_coordinates(col_list , view_direction):
    transformed_coordinates = []
    xmax = max(col[0] for col in col_list)
    ymax = max(col[1] for col in col_list)
    for coord in col_list:
        x , y , zt, zb, l = col_list
        if view_direction == 'east':
            xt_transformed = y
            yt_transformed = zt
            xb_transformed = y
            yb_transformed = zb
        elif view_direction == 'west':
            xt_transformed == ymax-y
            yt_transformed = zt
            xb_transformed = ymax-y
            yb_transformed = zb
        elif view_direction == 'north':
            xt_transformed == xmax-x
            yt_transformed = zt
            xb_transformed = xmax-x
            yb_transformed = zb
        elif view_direction == 'south':
            xt_transformed == x
            yt_transformed = zt
            xb_transformed = x
            yb_transformed = zb
        else:
            raise ValueError("Invalid view direction. Use 'east', 'west', 'north', or 'south'.")
    return


print("*" * 20)
print(outlier_east_col[0])

e_transformed_coord = []
for col in outlier_east_col:



'''