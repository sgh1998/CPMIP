import numpy as np
import matplotlib.pyplot as plt
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

east_txt_path = get_full_path(major_folder, paths['east_txt_path'])
west_txt_path = get_full_path(major_folder, paths['west_txt_path'])
north_txt_path = get_full_path(major_folder, paths['north_txt_path'])
south_txt_path = get_full_path(major_folder, paths['south_txt_path'])


east_file = np.loadtxt(east_txt_path, delimiter=',' , usecols=(0, 1, 2, 3))
west_file = np.loadtxt(west_txt_path, delimiter=',' , usecols=(0, 1, 2, 3))
north_file = np.loadtxt(north_txt_path, delimiter=',', usecols=(0, 1, 2, 3))
south_file = np.loadtxt(south_txt_path, delimiter=',', usecols=(0, 1, 2, 3))

plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
for xt, yt, xb, yb in east_file:
    plt.plot([xt, xb], [yt, yb], marker='o', color='r')
plt.title('east')

plt.subplot(2, 2, 2)
for xt, yt, xb, yb in west_file:
    plt.plot([xt, xb], [yt, yb], marker='o', color='r')
plt.title('west')

plt.subplot(2, 2, 3)
for xt, yt, xb, yb in north_file:
    plt.plot([xt, xb], [yt, yb], marker='o', color='r')
plt.title('north')

plt.subplot(2, 2, 4)
for xt, yt, xb, yb in south_file:
    plt.plot([xt, xb], [yt, yb], marker='o', color='r')
plt.title('south')
plt.show()





'''
def plot_columns(data):
    "plots columns"
    plt.figure()
    for xt,yt,xb,yb in data:
        plt.plot([xb, xt], [yb, yt], marker='o', color='r')


#net_output_file = 'east_002.txt'
model_output_file = 'south.txt'

#data_net = np.loadtxt(net_output_file, delimiter=',')
data_model_raw = np.loadtxt(model_output_file, delimiter=',')

#data_model = data_model_raw[:, [0, 2,0,3]]
data_model = data_model_raw[:, [0, 1,2,3]]

#plot_columns(data_net)
plot_columns(data_model)
plt.show()
'''