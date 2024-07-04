import subprocess
import os
import glob
import yaml
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

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
model_path = get_full_path(major_folder, paths['model'])
asbuilt_images = get_full_path(major_folder, paths['asbuilt_images'])
detect_save_folder = get_full_path(major_folder, paths['detect_save_folder'])   # where detection results are saved
output_folder_base = get_full_path(major_folder, paths['output_folder_base'])

# View direction
view_direction = config['view_direction'].strip().lower()  # Read view direction from config
output_folder = os.path.join(output_folder_base, f"{view_direction}_output")  # coordinates save path

# Ensure the view direction is valid
if view_direction not in ["east", "west", "north", "south"]:
    print("Invalid view direction. Please enter one of: east, west, north, south.")
    exit()

# Path to detect.py in the YOLOv5 repository
detect_script_path = os.path.join(os.getcwd(), "yolov5", "detect.py")

# Check if detect.py exists
if not os.path.exists(detect_script_path):
    print(f"Error: {detect_script_path} does not exist.")
    exit()

# Use the weights for detection
command_detect = f"python {detect_script_path} --source {asbuilt_images} --weights {model_path} --conf 0.5 --hide-labels --line-thickness 1 --save-txt --nosave --project {detect_save_folder} --name exp --device cpu"
# Run the command
subprocess.run(command_detect, shell=True)

detect_exp_folders = glob.glob(os.path.join(detect_save_folder, 'exp*', 'labels'))  # path to predicted labels for the last model
if detect_exp_folders:
    latest_detect_exp_folder = max(detect_exp_folders, key=os.path.getctime)
    print("Latest Detect Experiment Folder:", latest_detect_exp_folder)
else:
    print("No predicted label folders found.")
    exit()

# Function to plot detected labels on images and save them
def plot_label(folder_path, predicted_labels_folder, output_folder, view_direction):
    line_width = 0.5
    img_counter = 1

    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)
            fig, ax = plt.subplots(1)
            ax.imshow(img)

            predicted_labels_file = os.path.join(predicted_labels_folder, f'{filename.split(".")[0]}.txt')
            if os.path.exists(predicted_labels_file):
                with open(predicted_labels_file, "r") as file:
                    for line in file:
                        data = line.split()
                        label = int(data[0])
                        x, y, w, h = map(float, data[1:5])

                        x = (x - w / 2.0) * img.width
                        y = (y - h / 2.0) * img.height
                        w *= img.width
                        h *= img.height

                        rect = Rectangle((x, y), w, h, linewidth=line_width, edgecolor="r", facecolor="none", label="Predicted Label")
                        ax.add_patch(rect)

            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.axis('off')

            image_base_name = f'{view_direction}_{img_counter:03d}'
            save_path = os.path.join(output_folder, f'{image_base_name}.jpeg')
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0.0, dpi=300)
            plt.close(fig)

            img_counter += 1

print("detection_predicted_labels_folder is", latest_detect_exp_folder)

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

plot_label(asbuilt_images, latest_detect_exp_folder, output_folder, view_direction)

# Read labels and convert to the format
col_coordinates = []
img_counter = 1
for image_file in os.listdir(asbuilt_images):
    if image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        image_path = os.path.join(asbuilt_images, image_file)
        img = Image.open(image_path)
        width, height = img.size
        print(f"Image: {image_file}, Width: {width}, Height: {height}")

        predicted_labels_file = os.path.join(latest_detect_exp_folder, f'{image_file.split(".")[0]}.txt')
        elements_coordinates = []

        if os.path.exists(predicted_labels_file):
            with open(predicted_labels_file, "r") as file:
                for line in file:
                    data = line.split()
                    label = int(data[0])
                    x, y, w, h = map(float, data[1:5])

                    x = x * width
                    y = y * height
                    w *= width
                    h *= height
                    mid_top = (x, y - h / 2)
                    mid_bottom = (x, y + h / 2)
                    print("Midpoint of the top:", mid_top)
                    print("Midpoint of the bottom:", mid_bottom)

                    elements_coordinates.append([mid_top[0], mid_top[1], mid_bottom[0], mid_bottom[1]])

        image_base_name = f'{view_direction}_{img_counter:03d}'
        output_file_path = os.path.join(output_folder, f'{image_base_name}.txt')
        with open(output_file_path, "w") as output_file:
            for coord in elements_coordinates:
                output_file.write(f"{coord[0]}, {coord[1]}, {coord[2]}, {coord[3]}\n")

        img_counter += 1

'''
The script loads a trained YOLOv5 model and performs object detection on images in a specified directory.
It processes each image, runs inference to detect objects, applies non-maximum suppression to filter the detections, and plots bounding boxes on the images.
Finally, it displays the processed images with detected objects and saves the coordinates to text files.
'''
