import numpy as np
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

# Load configuration
config = load_config()

# Validate configuration keys
required_keys = ['major_folder', 'paths']
for key in required_keys:
    if key not in config:
        raise KeyError(f"Missing required configuration key: {key}")

paths_required_keys = ['output_folder_base', 'east_txt_path', 'west_txt_path', 'north_txt_path', 'south_txt_path']
for key in paths_required_keys:
    if key not in config['paths']:
        raise KeyError(f"Missing required configuration key in paths: {key}")

major_folder = config['major_folder']
paths = config['paths']
output_folder_base = paths['output_folder_base']

# List of direction keys and titles
directions = ['east', 'west', 'north', 'south']
titles = ['East', 'West', 'North', 'South']
subplots = [221, 222, 223, 224]

# Initialize figure
plt.figure(figsize=(12, 8))
plt.suptitle('Data Plots from East, West, North, and South Files')  # Add a title to the figure

# Plot the data from files
for direction, title, subplot in zip(directions, titles, subplots):
    txt_path_key = f'{direction}_txt_path'
    if txt_path_key in paths:
        txt_path = get_full_path(major_folder, paths[txt_path_key])
        if os.path.isfile(txt_path):
            try:
                data = load_file(txt_path)
                plot_data(data, title, subplot)
            except FileNotFoundError:
                print(f"File not found: {txt_path}")

plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make room for the suptitle
#plt.show()

# Plot asbuilt data
asbuilt_directory = get_full_path(major_folder, os.path.join(output_folder_base, "east_output"))
if os.path.isdir(asbuilt_directory):
    asbuilt_files_data = load_files_from_directory(asbuilt_directory)

    plt.figure(figsize=(12, 8))
    plt.suptitle('Asbuilt Data Plots from East Output Directory')

    for idx, data in enumerate(asbuilt_files_data):
        plt.subplot(1, len(asbuilt_files_data), idx + 1)
        for xt, yt, xb, yb in data:
            plt.plot([xt, xb], [yt, yb], marker='o', color='r')
        plt.title(f'East Asbuilt {idx+1}')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make room for the suptitle
    #plt.show()



asbuilt_directory = get_full_path(major_folder, os.path.join(output_folder_base, "west_output"))
if os.path.isdir(asbuilt_directory):
    asbuilt_files_data = load_files_from_directory(asbuilt_directory)

    plt.figure(figsize=(12, 8))
    plt.suptitle('Asbuilt Data Plots from West Output Directory')

    for idx, data in enumerate(asbuilt_files_data):
        plt.subplot(1, len(asbuilt_files_data), idx + 1)
        for xt, yt, xb, yb in data:
            plt.plot([xt, xb], [yt, yb], marker='o', color='r')
        plt.title(f'East Asbuilt {idx+1}')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make room for the suptitle
    #plt.show()



    asbuilt_directory = get_full_path(major_folder, os.path.join(output_folder_base, "north_output"))
if os.path.isdir(asbuilt_directory):
    asbuilt_files_data = load_files_from_directory(asbuilt_directory)

    plt.figure(figsize=(12, 8))
    plt.suptitle('Asbuilt Data Plots from North Output Directory')

    for idx, data in enumerate(asbuilt_files_data):
        plt.subplot(1, len(asbuilt_files_data), idx + 1)
        for xt, yt, xb, yb in data:
            plt.plot([xt, xb], [yt, yb], marker='o', color='r')
        plt.title(f'East Asbuilt {idx+1}')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make room for the suptitle
    #plt.show()


plt.show()