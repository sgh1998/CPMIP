import numpy as np
import cv2 as cv
import random
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import yaml
import os
import glob

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
asbuilt_output_folder = get_full_path(major_folder, config['paths']['output_folder_base'])
asbuilt_images_path = get_full_path(major_folder, config['paths']['asbuilt_images'])

# Extract the view information from the configuration
view = config['view_direction'].strip().lower()

# Step 1: Find the image in the asbuilt_images directory
image_files = glob.glob(os.path.join(asbuilt_images_path, "*.jpg")) + glob.glob(os.path.join(asbuilt_images_path, "*.png"))

if len(image_files) != 1:
    raise ValueError(f"Expected exactly one image file in {asbuilt_images_path}, but found {len(image_files)}.")

# Get the image file name without the extension
image_file_path = image_files[0]
file_name = os.path.splitext(os.path.basename(image_file_path))[0]

# Step 2: Find the corresponding text file based on the image name and view direction
if view == "east":
    net_output_file = os.path.join(asbuilt_output_folder, f"east_output", f"{file_name}.txt")
elif view == "west":
    net_output_file = os.path.join(asbuilt_output_folder, f"west_output", f"{file_name}.txt")
elif view == "north":
    net_output_file = os.path.join(asbuilt_output_folder, f"north_output", f"{file_name}.txt")
elif view == "south":
    net_output_file = os.path.join(asbuilt_output_folder, f"south_output", f"{file_name}.txt")
else:
    raise ValueError(f"Unknown view direction: {view}")

if not os.path.exists(net_output_file):
    raise FileNotFoundError(f"Text file {net_output_file} not found for image {file_name} and view {view}.")

# Load the data from the text file
data_net = np.loadtxt(net_output_file, delimiter=',')

# Read the image
I = cv.imread(image_file_path)

m, n, _ = I.shape

bottom_points = []
column_data = []
column_heights = []  # List to store the heights of all columns

# Loop through the data and extract the bottom points
for xt, yt, xb, yb in data_net:
    height = yt - yb
    xb_transformed = int(xb)
    yb_transformed = int(m - yb)  # Transform yb to be relative to the bottom-left corner
    xt_transformed = int(xt)
    yt_transformed = int(m - yt)  # Transform ytop to be relative to the bottom-left corner
    
    xb = int(xb)
    yb = int(yb)
    xt = int(xt)
    yt = int(yt)

    bottom_points.append((xb, yb))
    column_data.append([xt, yt, xb, yb])
    column_heights.append(height)
    
    cv.circle(I, (xb_transformed, yb_transformed), 4, (255, 0, 0), 2)

# Calculate and print the average height of all columns
average_column_height = np.mean(column_heights)
print(f"Average height of all columns: {average_column_height:.2f} pixels")

# Apply DBSCAN clustering based on x-coordinates
x_coords = np.array([x for x, _ in bottom_points]).reshape(-1, 1)
eps_value = np.average(np.diff(np.sort(x_coords[:, 0]))) * 1.2
print('Calculated eps:', eps_value)

dbscan = DBSCAN(eps=eps_value, min_samples=1)
clusters = dbscan.fit_predict(x_coords)

# Initialize a dictionary to store the clusters
cluster_dict = {}
for i, cluster_id in enumerate(clusters):
    if cluster_id != -1:
        if cluster_id not in cluster_dict:
            cluster_dict[cluster_id] = []
        cluster_dict[cluster_id].append(column_data[i])

# Calculate scaled distances for each cluster
cluster_distances = []
lowest_y_coords = []

# First: collect all lowest points and calculate the average
for cluster in cluster_dict.values():
    lowest_y = min([col[3] for col in cluster])
    lowest_y_coords.append(lowest_y)
    
avg_lowest_y = np.mean(lowest_y_coords)

# Second: calculate scaled distances for each cluster's lowest point
for cluster_id, columns in cluster_dict.items():
    lowest_col = min(columns, key=lambda x: x[3])  # Get column with lowest y
    lowest_y = lowest_col[3]
    column_height = lowest_col[1] - lowest_col[3]  # yt - yb
    
    # Calculate scaled distance
    scaled_distance = (lowest_y - avg_lowest_y) / column_height
    cluster_distances.append({
        'cluster_id': cluster_id,
        'scaled_distance': scaled_distance,
        'lowest_y': lowest_y
    })

# Define threshold for floor determination
DISTANCE_THRESHOLD = 0.31  # Replace with your trained threshold

def assign_floors_with_gaps(column_data, avg_height, scaled_distance, tolerance=1.93):
    column_data.sort(key=lambda col: col[3], reverse=True)  # Sort by ybot (from top to bottom)
    column_floor_info = []

    # Determine the starting floor based on scaled distance
    if scaled_distance <= DISTANCE_THRESHOLD:
        floor_number = 1  # Start from Floor 1
    else:
        floor_number = 2  # Start from Floor 2

    prev_y = column_data[-1][3]

    for idx, col in enumerate(reversed(column_data)):
        xt, yt, xb, yb = col
        if idx == 0:
            # The first column takes the determined floor number
            column_floor_info.append((xt, yt, xb, yb, floor_number))
        else:
            vertical_distance = yb - prev_y
            
            # Determine if we need to increment by 1 floor or skip to the next floor
            if vertical_distance > 2 * avg_height * tolerance:
                floor_number += 3
            elif vertical_distance > avg_height * tolerance:
                floor_number += 2  # Skip one floor if gap is larger than expected
            else:
                floor_number += 1
            
            column_floor_info.append((xt, yt, xb, yb, floor_number))
        
        prev_y = yb

    column_floor_info.reverse()
    return column_floor_info

# Analyze clusters and assign floors
all_floors_info = []
for cluster_id, columns in cluster_dict.items():
    # Find the scaled distance for this cluster
    cluster_info = next(cd for cd in cluster_distances if cd['cluster_id'] == cluster_id)
    
    # Assign floors using scaled distance
    column_floor_info = assign_floors_with_gaps(
        columns, 
        average_column_height,
        cluster_info['scaled_distance']
    )
    
    all_floors_info.extend(column_floor_info)
    
    # Print the results
    print(f"\nResults for Cluster {cluster_id}:")
    print(f"Scaled Distance: {cluster_info['scaled_distance']:.3f}")
    print(f"Starting Floor: {'1' if cluster_info['scaled_distance'] <= DISTANCE_THRESHOLD else '2'}")
    for entry in column_floor_info:
        print(f"Xtop: {entry[0]}, Ytop: {entry[1]}, Xbot: {entry[2]}, Ybot: {entry[3]}, Floor: {entry[4]}")

# Save the results to the specified path
output_file_name = f"{view}_asbuilt_floor_info.txt"
output_file_path = os.path.join(asbuilt_output_folder, output_file_name)
with open(output_file_path, 'w') as f:
    f.write("Xtop, Ytop, Xbot, Ybot, Floor\n")
    for entry in all_floors_info:
        f.write(f"{entry[0]}, {entry[1]}, {entry[2]}, {entry[3]}, {entry[4]}\n")

print(f"Results saved to {output_file_path}")

# Visualize the clusters
for i, (x, y) in enumerate(bottom_points):
    cluster_id = clusters[i]
    if cluster_id != -1:
        color = (random.randrange(256), random.randrange(256), random.randrange(256))
        cv.circle(I, (x, y), 4, color, 2)

plt.figure(figsize=(10, 6))
for cluster_id, coordinates in cluster_dict.items():
    x_values = [x[2] for x in coordinates]
    y_values = [cluster_id] * len(x_values)
    plt.scatter(x_values, y_values, label=f'Cluster {cluster_id}', s=100)

plt.xlabel('X Coordinate')
plt.ylabel('Cluster ID')
plt.title('X Coordinates of Columns by Cluster')
plt.legend()
plt.grid(True)

plt.show(block=False)  # Show the plot without blocking the execution
plt.pause(5)           # Pause for 5 seconds
plt.close()            # Close the plot window





