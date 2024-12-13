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
print("Initial Construction Percentages:")
for floor in range(1, max_floor):
    if asplanned_counts[floor] > 0:
        print(f"Floor {floor}: {constructed_percentages[floor]:.2f}% of columns constructed ({asbuilt_counts[floor]}/{asplanned_counts[floor]})")
    else:
        print(f"Floor {floor}: No planned columns.")

# Sequence Consideration Section
print("\nSequence Consideration:")
adjusted_asbuilt_counts = asbuilt_counts.copy()

# Go from top floor to bottom floor to apply the sequence rule
for floor in range(max_floor - 1, 0, -1):
    if adjusted_asbuilt_counts[floor] > 0:
        for lower_floor in range(1, floor):
            if asplanned_counts[lower_floor] > 0:
                adjusted_asbuilt_counts[lower_floor] = asplanned_counts[lower_floor]

# Calculate the new percentage of constructed columns per floor
adjusted_constructed_percentages = (adjusted_asbuilt_counts / asplanned_counts) * 100

# Print the adjusted construction percentages per floor
for floor in range(1, max_floor):
    if asplanned_counts[floor] > 0:
        print(f"Floor {floor}: {adjusted_constructed_percentages[floor]:.2f}% of columns constructed ({adjusted_asbuilt_counts[floor]}/{asplanned_counts[floor]})")
    else:
        print(f"Floor {floor}: No planned columns.")

# Calculate the overall progress percentage of the project
total_floors = np.sum(asplanned_counts > 0)  # Total number of floors with planned columns
weighted_progress = np.sum(adjusted_constructed_percentages[1:max_floor] / 100)  # Sum of progress as a decimal
overall_progress_percentage = (weighted_progress / total_floors) * 100

print(f"\nOverall Project Progress: {overall_progress_percentage:.2f}%")

# If you want to save this output to a file, you can do so like this:
output_results_path = os.path.join(asbuilt_file_path, f"{view}_construction_percentage.txt")
with open(output_results_path, 'w') as f:
    f.write("Floor, Constructed Percentage, Constructed Columns, Planned Columns\n")
    for floor in range(1, max_floor):
        if asplanned_counts[floor] > 0:
            f.write(f"{floor}, {adjusted_constructed_percentages[floor]:.2f}%, {adjusted_asbuilt_counts[floor]}, {asplanned_counts[floor]}\n")
        else:
            f.write(f"{floor}, No planned columns\n")
    f.write(f"\nOverall Project Progress: {overall_progress_percentage:.2f}%\n")

print(f"Construction percentage with sequence consideration and overall progress saved to {output_results_path}")
