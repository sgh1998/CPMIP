import numpy as np
import cv2 as cv
import random
import matplotlib.pyplot as plt

img_path = r"F:\CPMIP_Data\advanced\asbuilt_coordinates\east_output\east_009.jpeg"
net_output_file = r"F:\CPMIP_Data\advanced\asbuilt_coordinates\east_output\east_009.txt"

def plot_columns(data):
    "plots columns"
    plt.figure()
    for xt, yt, xb, yb in data:
        plt.plot([xb, xt], [yb, yt], marker='o', color='r')

# Load the data with comma delimiter
data_net = np.loadtxt(net_output_file, delimiter=',')

# Read the image
I = cv.imread(img_path)

# Get the dimensions of the image
m, n, _ = I.shape

# Initialize an empty mask for drawing
B = np.zeros((m, n), dtype=np.uint8)

bottom_points = []
# Iterate through each line of the text file, using only the bottom points
for xbot, ybot, xtop, ytop in data_net:
    xbot = int(xbot)  # Assuming xbot is already in image coordinates
    ybot = int(ybot)  # Assuming ybot is already in image coordinates
    
    B[ybot, xbot] = 255
    bottom_points.append((xbot, ybot))

# Sort bottom points by x coordinate
bottom_points.sort(key=lambda t: t[0])
x_list = [x for x, _ in bottom_points]

ax = np.array(x_list)
dx = np.diff(ax)

# Find separations in the columns
sep_list = np.where(dx > 5 * np.median(dx))[0]

sep_columns = []

start = 0
for sep in sep_list:
    end = sep + 1
    sep_columns.append(bottom_points[start:end])
    start = end

# Add the last column
sep_columns.append(bottom_points[start:])

# Draw circles at the bottom points for each column
for column in sep_columns:
    bottom_points.sort(key=lambda t: -t[1])

for column in sep_columns:
    color = (random.randrange(256), random.randrange(256), random.randrange(256))
    for x, y in column:
        cv.circle(I, (x, y), 4, color, 2)

# Show the image with the drawn circles
cv.imshow('', I)
cv.waitKey()
