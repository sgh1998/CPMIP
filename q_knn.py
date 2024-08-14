import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import random
from sklearn.neighbors import NearestNeighbors

img_path = r"D:\CS\case1\Data_CPMIP\user_inputs\asbuilt_images\e (4).jpg"
net_output_file = r"D:\CS\case1\Data_CPMIP\advanced\asbuilt_coordinates\east_output\e (4).txt"

def plot_columns(data):
    "plots columns"
    plt.figure()
    for xt, yt, xb, yb in data:
        plt.plot([xb, xt], [yb, yt], marker='o', color='r')

# Load the data from the text file
data_net = np.loadtxt(net_output_file, delimiter=',')

# Read the image
I = cv.imread(img_path)

# Get the dimensions of the image
print(I.shape)
m, n, _ = I.shape

# Resize the image to 50% of its original size (adjust the scale as needed)
scale_percent = 70  # Percentage of the original size
width = int(I.shape[1] * scale_percent / 100)
height = int(I.shape[0] * scale_percent / 100)
dim = (width, height)
I = cv.resize(I, dim, interpolation=cv.INTER_AREA)

# Initialize an empty list to store the bottom points
bottom_points = []

# Loop through the data and extract the bottom points
for xt, yt, xb, yb in data_net:
    # Convert the bottom points to integer values
    xb = int(xb * scale_percent / 100)
    yb = int(m - yb * scale_percent / 100)  # Transform yb to be relative to the bottom-left corner and scale it
    
    # Append the bottom points to the list
    bottom_points.append((xb, yb))

    # Draw a circle at the bottom point on the image
    cv.circle(I, (xb, yb), 4, (255, 0, 0), 2)


cv.imshow('Clustered Bottom Points', I)
cv.waitKey(0)
cv.destroyAllWindows()

'''
# KNN Clustering
bottom_points = np.array(bottom_points)  # Convert to NumPy array
nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(bottom_points)
distances, indices = nbrs.kneighbors(bottom_points)

# Define a threshold distance (tunable parameter) for clustering
threshold_distance = 25  # Adjusted for the resized image

# Group points based on distance
clusters = []
visited = set()

for i in range(len(bottom_points)):
    if i in visited:
        continue
    cluster = []
    stack = [i]
    
    while stack:
        index = stack.pop()
        if index in visited:
            continue
        visited.add(index)
        cluster.append(tuple(bottom_points[index]))
        
        # Find neighbors within the threshold distance
        neighbors = [j for j in indices[index] if distances[index][np.where(indices[index] == j)[0][0]] < threshold_distance]
        
        stack.extend(neighbors)
    
    clusters.append(cluster)

# Sort clusters by y-coordinate to identify floors
for cluster in clusters:
    cluster.sort(key=lambda t: -t[1])  # Sort by y-coordinate (top to bottom)

# Visualize the clusters
for cluster in clusters:
    color = (random.randrange(256), random.randrange(256), random.randrange(256))
    for x, y in cluster:
        cv.circle(I, (x, y), 4, color, 2)





'''