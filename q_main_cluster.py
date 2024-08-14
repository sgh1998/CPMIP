import numpy as np
import cv2 as cv
import random
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors



img_path = r"D:\CS\case1\Data_CPMIP\user_inputs\asbuilt_images\e (4).jpg"
net_output_file = r"D:\CS\case1\Data_CPMIP\advanced\asbuilt_coordinates\east_output\e (4).txt"

def plot_columns(data):
    "plots columns"
    plt.figure()
    for xt,yt,xb,yb in data:
        plt.plot([xb, xt], [yb, yt], marker='o', color='r')

data_net = np.loadtxt(net_output_file, delimiter=',')

I = cv.imread(img_path)

m,n,_ = I.shape

B = np.zeros((m,n), dtype=np.uint8)
bottom_points = []

# Loop through the data and extract the bottom points
for xt, yt, xb, yb in data_net:
    # Convert the bottom points to integer values
    xb = int(xb)
    yb = int(m - yb)  # Transform yb to be relative to the bottom-left corner and scale it
    
    # Append the bottom points to the list
    bottom_points.append((xb, yb))

    # Draw a circle at the bottom point on the image
    cv.circle(I, (xb, yb), 4, (255, 0, 0), 2)

cv.imshow('Clustered Bottom Points', I)
cv.waitKey()

bottom_points.sort(key = lambda t : t[0])

x_list = [x for x,_ in bottom_points]

ax = np.array(x_list)

dx = np.diff(ax)

sep_list = np.where(dx > 5 * np.median(dx))[0]

sep_columns = []

start = 0
for sep in sep_list:
    end = sep+1
    sep_columns.append(bottom_points[start:end])
    start = end

sep_columns.append(bottom_points[start:])

for column in sep_columns:
    bottom_points.sort(key = lambda t : -t[1])


for column in sep_columns:
    color = (random.randrange(256), random.randrange(256), random.randrange(256))
    for x,y in column:
        cv.circle(I, (x,y), 4, color, 2)

print(sep_columns)
cv.imshow('', I)
cv.waitKey()



