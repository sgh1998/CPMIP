import numpy as np
import cv2 as cv
import random
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

file_name = '1 (135)'
img_path = fr"D:\CS\case1\Data_CPMIP\user_inputs\asbuilt_images\{file_name}.jpg"
net_output_file = fr"D:\CS\case1\Data_CPMIP\advanced\asbuilt_coordinates\east_output\{file_name}.txt"

def plot_columns(data):
    "plots columns"
    plt.figure()
    for xt, yt, xb, yb in data:
        plt.plot([xb, xt], [yb, yt], marker='o', color='r')

# Load the data from the text file
data_net = np.loadtxt(net_output_file, delimiter=',')

# Read the image
I = cv.imread(img_path)

m, n, _ = I.shape

bottom_points = []
column_data = []

# Loop through the data and extract the bottom points
for xt, yt, xb, yb in data_net:
    # Convert the bottom points to integer values
    xb = int(xb)
    yb = int(m - yb)  # Transform yb to be relative to the bottom-left corner
    xt = int(xt)
    yt = int(m - yt)  # Transform ytop to be relative to the bottom-left corner
    
    # Append the bottom points to the list
    bottom_points.append((xb, yb))
    column_data.append([xt, yt, xb, yb])

    # Draw a circle at the bottom point on the image
    cv.circle(I, (xb, yb), 4, (255, 0, 0), 2)

# cv.imshow('Initial Bottom Points', I)
# cv.waitKey()

# Extract x-coordinates for clustering
x_coords = np.array([x for x, _ in bottom_points]).reshape(-1, 1)

# Calculate the median of the differences as the eps value
eps_value = np.average(np.diff(np.sort(x_coords[:, 0]))) * 1
print('Calculated eps:', eps_value)

# Apply DBSCAN clustering based on x-coordinates
dbscan = DBSCAN(eps=eps_value, min_samples=1)  # Use calculated eps value
clusters = dbscan.fit_predict(x_coords)

# Initialize a dictionary to store the clusters
cluster_dict = {}

# Organize the points by clusters
for i, cluster_id in enumerate(clusters):
    if cluster_id != -1:  # Ignore noise points (if any)
        if cluster_id not in cluster_dict:
            cluster_dict[cluster_id] = []
        cluster_dict[cluster_id].append(column_data[i])

# Initialize a list to store the final column information
column_floor_info = []

# Analyze clusters to determine columns per floor
for cluster_id, columns in cluster_dict.items():
    # Sort the columns by y-values (from bottom to top)
    columns.sort(key=lambda col: col[3], reverse=True)  # Sort by ybot
    
    # Group by floors based on y-coordinate differences
    floor_number = 1
    floor_threshold = 20  # Adjust this threshold as needed based on floor height
    prev_y = columns[0][3]

    for column in columns:
        xt, yt, xb, yb = column
        if abs(yb - prev_y) > floor_threshold:
            floor_number += 1
        column_floor_info.append((cluster_id, xt, yt, xb, yb, floor_number))
        prev_y = yb

# Print the desired list
print("Cluster ID, Xtop, Ytop, Xbot, Ybot, Floor")
for entry in column_floor_info:
    print(entry)

# Visualize the clusters
for i, (x, y) in enumerate(bottom_points):
    cluster_id = clusters[i]
    if cluster_id != -1:  # Ignore noise points (if any)
        color = (random.randrange(256), random.randrange(256), random.randrange(256))
        cv.circle(I, (x, y), 4, color, 2)

# Display the clustered image
# cv.imshow('Clustered Bottom Points', I)
# cv.waitKey(0)
# cv.destroyAllWindows()

# Plot x-coordinates on a new plot (unchanged)
plt.figure(figsize=(10, 6))
for cluster_id, coordinates in cluster_dict.items():
    x_values = [x[2] for x in coordinates]  # x[2] is xbot
    y_values = [cluster_id] * len(x_values)  # Use cluster_id as y value for visualization
    plt.scatter(x_values, y_values, label=f'Cluster {cluster_id}', s=100)

plt.xlabel('X Coordinate')
plt.ylabel('Cluster ID')
plt.title('X Coordinates of Columns by Cluster')
plt.legend()
plt.grid(True)
plt.show()
