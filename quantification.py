import numpy as np
import yaml
import os

# Load configuration from YAML
def load_config(config_file="user.yaml"):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_full_path(major_folder, relative_path):
    return os.path.join(major_folder, relative_path)

# Load the configuration
config = load_config()
major_folder = config['major_folder']
view = config['view_direction']

# Determine the correct as-planned file path based on the view
if view == 'east':
    asplanned_file_path = get_full_path(major_folder, config['paths']['east_txt_path'])
elif view == 'west':
    asplanned_file_path = get_full_path(major_folder, config['paths']['west_txt_path'])
elif view == 'north':
    asplanned_file_path = get_full_path(major_folder, config['paths']['north_txt_path'])
elif view == 'south':
    asplanned_file_path = get_full_path(major_folder, config['paths']['south_txt_path'])
else:
    raise ValueError(f"Unknown view direction: {view}")

# Determine the as-built file path
asbuilt_file_path = get_full_path(major_folder, config['paths']['output_folder_base'])

# Load the as-planned data
asplanned_data = np.loadtxt(asplanned_file_path, delimiter=',')

# Load the as-built data
asbuilt_file_name = f"{view}_asbuilt_floor_info.txt"
asbuilt_full_path = os.path.join(asbuilt_file_path, asbuilt_file_name)
asbuilt_data = np.loadtxt(asbuilt_full_path, delimiter=',', skiprows=1)  # Skipping the header row

# Extract floor numbers from both as-planned and as-built data
asplanned_floors = asplanned_data[:, -1].astype(int)
asbuilt_floors = asbuilt_data[:, -1].astype(int)

# Count the number of columns per floor in as-planned and as-built data
asplanned_counts = np.bincount(asplanned_floors)
asbuilt_counts = np.bincount(asbuilt_floors)

# Ensure the arrays are the same length
max_floor = max(len(asplanned_counts), len(asbuilt_counts))
asplanned_counts = np.pad(asplanned_counts, (0, max_floor - len(asplanned_counts)), 'constant')
asbuilt_counts = np.pad(asbuilt_counts, (0, max_floor - len(asbuilt_counts)), 'constant')

# Calculate the percentage of constructed columns per floor
constructed_percentages = (asbuilt_counts / asplanned_counts) * 100

# Print the percentage of constructed columns per floor
for floor in range(1, max_floor):
    if asplanned_counts[floor] > 0:
        print(f"Floor {floor}: {constructed_percentages[floor]:.2f}% of columns constructed ({asbuilt_counts[floor]}/{asplanned_counts[floor]})")
    else:
        print(f"Floor {floor}: No planned columns.")

# If you want to save this output to a file, you can do so like this:
output_results_path = os.path.join(asbuilt_file_path, f"{view}_construction_percentage.txt")
with open(output_results_path, 'w') as f:
    f.write("Floor, Constructed Percentage, Constructed Columns, Planned Columns\n")
    for floor in range(1, max_floor):
        if asplanned_counts[floor] > 0:
            f.write(f"{floor}, {constructed_percentages[floor]:.2f}%, {asbuilt_counts[floor]}, {asplanned_counts[floor]}\n")
        else:
            f.write(f"{floor}, No planned columns\n")

print(f"Construction percentage saved to {output_results_path}")
