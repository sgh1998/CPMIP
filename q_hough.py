import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import random

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
scale_percent = 90  # Percentage of the original size
width = int(I.shape[1] * scale_percent / 100)
height = int(I.shape[0] * scale_percent / 100)
dim = (width, height)
I = cv.resize(I, dim, interpolation=cv.INTER_AREA)

# Initialize an empty list to store the bottom points
bottom_points = []





B = np.zeros((m,n), dtype=np.uint8)
# Loop through the data and extract the bottom points
for xt, yt, xb, yb in data_net:
    # Convert the bottom points to integer values
    xb = int(xb * scale_percent / 100)
    yb = int(m - yb * scale_percent / 100)  # Transform yb to be relative to the bottom-left corner and scale it
    
    # Append the bottom points to the list
    bottom_points.append((xb, yb))
    B[yb,xb] = 255
    # Draw a circle at the bottom point on the image
    cv.circle(I, (xb, yb), 4, (255, 0, 0), 2)


def draw_line(I,rho,theta):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 + 1000*(-b))
    y2 = int(y0 + 1000*(a))
    cv.line(I,(x1,y1),(x2,y2),(0,0,255),2)


dist_res = 6
angle_res = np.pi/180 *5
L = cv.HoughLines(B, dist_res, angle_res, 2)
for [[rho,theta]] in L:
    draw_line(I,rho,theta)



cv.imshow('', I)
cv.waitKey()

'''
# Convert the image to grayscale
gray = cv.cvtColor(I, cv.COLOR_BGR2GRAY)

# Use Hough Line Transform to detect lines between the points
edges = cv.Canny(gray, 50, 150, apertureSize=3)

# Adjusted rho and theta for finer line detection
rho = 3  # Distance resolution in pixels
theta = np.pi / 180*3  # Angle resolution in radians

# Use Hough Line Transform with tuned parameters
lines = cv.HoughLinesP(edges, rho, theta, threshold=100, minLineLength=100, maxLineGap=5)

# Draw the detected lines on the image
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv.line(I, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Display the image with the drawn lines
cv.namedWindow('Detected Lines', cv.WINDOW_NORMAL)
cv.resizeWindow('Detected Lines', width, height)
cv.imshow('Detected Lines', I)
cv.waitKey(0)
cv.destroyAllWindows()



'''