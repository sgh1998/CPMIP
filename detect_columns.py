import numpy as np
import cv2 as cv
import random
import matplotlib.pyplot as plt
import yaml
import os


def load_config(config_file="user.yaml"):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_full_path(base_folder, relative_path):
    return os.path.join(base_folder, relative_path)

def load_file(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file is invalid: {file_path}")
    data = np.loadtxt(file_path, delimiter=',', usecols=(0, 1, 2, 3))
    return data

def load_files_from_directory(directory_path):
    files_data = []
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"The directory name is invalid: {directory_path}")
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.txt'):
            data = np.loadtxt(file_path, delimiter=',', usecols=(0, 1, 2, 3))
            files_data.append(data)
    return files_data

def plot_data(data, title, subplot_position):
    plt.subplot(subplot_position)
    for xt, yt, xb, yb in data:
        plt.plot([xt, xb], [yt, yb], marker='o', color='r')
    plt.title(title)





img_path = "photo_71_2024-07-25_13-37-51.jpg"
net_output_file = "photo_71_2024-07-25_13-37-51.txt"

def plot_columns(data):
    "plots columns"
    plt.figure()
    for xt,yt,xb,yb in data:
        plt.plot([xb, xt], [yb, yt], marker='o', color='r')

data_net = np.loadtxt(net_output_file, delimiter=' ')

I = cv.imread(img_path)

m,n,_ = I.shape

B = np.zeros((m,n), dtype=np.uint8)

bottom_points = []
for cls, x,y,w,h in data_net:
    x = int(x * n)
    y = int(y * m)
    w = int(w * n)
    h = int(h * m)
    y += h//2
    B[y,x] = 255
    bottom_points.append((x,y,w,h))

    
    #cv.circle(I, (x,y), 4, (255,0,0), 2)



bottom_points.sort(key = lambda t : t[0])
x_list = [x for x,_,_,_ in bottom_points]

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
    for x,y,w,h in column:
        cv.circle(I, (x,y), 4, color, 2)
   
cv.imshow('', I)
cv.waitKey()



