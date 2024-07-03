import os
import subprocess
import glob
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.placement
import ifcopenshell.util.element
import pandas as pd
import numpy as np

# Paths and configurations
train_save_folder = "F:\\ThesisFiles\\Datasets\\Runs\\OutputTrain"
detect_save_folder = "F:\\PyEnv\\yolov5\\yolov5\\runs\\detect"
ifc_file_path = "F:\\PyEnv\\ifcopenshell\\ifcfiles\\Project52.ifc"
source_path = r"F:\\ThesisFiles\\Datasets\\Runs\\RunPath\\images\\train"
model_path = "F:\\ThesisFiles\\Datasets\\Runs\\OutputTrain\\exp11\\weights\\best.pt"
detect_source_path = r"F:\\ThesisFiles\\Datasets\\Runs\\newdetection"
as_built_path = "F:\\ThesisFiles\\Datasets\\Runs\\newdetection\\asbuilt"

# Create directories if they don't exist
os.makedirs(train_save_folder, exist_ok=True)
os.makedirs(as_built_path, exist_ok=True)

# Function to train the model
def train_model():
    command_train = f"python train.py --img 640 --epochs 50 --data dataset.yaml --weights yolov5n.pt --save-period 100 --project {train_save_folder}"
    subprocess.run(command_train, shell=True)

# Function to perform detection
def detect_images(weights, source, output_folder):
    command_detect = f"python detect.py --source {source} --weights {weights} --conf 0.5 --hide-labels --line-thickness 1 --save-txt --data dataset.yaml --nosave"
    subprocess.run(command_detect, shell=True)

# Function to plot comparison images
def plot_comparison_image(folder_path, real_labels_folder, predicted_labels_folder, output_folder):
    line_width = 0.5
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)
            fig, ax = plt.subplots(1)
            ax.imshow(img)

            real_labels_file = os.path.join(real_labels_folder, f'{filename.split(".")[0]}.txt')
            with open(real_labels_file, "r") as file:
                for line in file:
                    data = line.split()
                    x, y, w, h = map(float, data[1:])
                    x = (x - w / 2.0) * img.width
                    y = (y - h / 2.0) * img.height
                    w *= img.width
                    h *= img.height
                    rect = Rectangle((x, y), w, h, linewidth=line_width, edgecolor="b", facecolor="none", label="Real Label")
                    ax.add_patch(rect)

            predicted_labels_file = os.path.join(predicted_labels_folder, f'{filename.split(".")[0]}.txt')
            if os.path.exists(predicted_labels_file):
                with open(predicted_labels_file, "r") as file:
                    for line in file:
                        data = line.split()
                        x, y, w, h = map(float, data[1:5])
                        x = (x - w / 2.0) * img.width
                        y = (y - h / 2.0) * img.height
                        w *= img.width
                        h *= img.height
                        rect = Rectangle((x, y), w, h, linewidth=line_width, edgecolor="r", facecolor="none", label="Predicted Label")
                        ax.add_patch(rect)

            ax.set_xticks([])
            ax.set_yticks([])
            ax.axis('off')
            save_path = os.path.join(output_folder, f'{filename.split(".")[0]}_output.png')
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0.0, dpi=300)
            plt.close(fig)

# Function to plot detected labels on images
def plot_label(folder_path, predicted_labels_folder, output_folder):
    line_width = 0.5
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
                        x, y, w, h = map(float, data[1:5])
                        x = (x - w / 2.0) * img.width
                        y = (y - h / 2.0) * img.height
                        w *= img.width
                        h *= img.height
                        rect = Rectangle((x, y), w, h, linewidth=line_width, edgecolor="r", facecolor="none", label="Predicted Label")
                        ax.add_patch(rect)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.axis('off')
            save_path = os.path.join(output_folder, f'{filename.split(".")[0]}_output.png')
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0.0, dpi=300)
            plt.close(fig)

# Function to process IFC file
def process_ifc_file(ifc_file_path):
    ifc_file = ifcopenshell.open(ifc_file_path)
    columns = ifc_file.by_type("IfcColumn")
    verts_list = []
    relative_list = []
    local_list = []
    mixed_list = []

    for column in columns:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, column)
        verts = shape.geometry.verts
        organized_verts = [(verts[i], verts[i+1], verts[i+2]) for i in range(0, len(verts), 3)]
        z_coordinates = [point[2] for point in organized_verts]
        Ztop = round(max(z_coordinates), 2)
        Zbot = round(min(z_coordinates), 2)
        matrix = ifcopenshell.util.placement.get_local_placement(column.ObjectPlacement)
        coordinates = column.ObjectPlacement.RelativePlacement.Location.Coordinates
        mixed = [matrix[:,3][:3][0], matrix[:,3][:3][1], Ztop, Zbot]
        verts_list.append(list(verts))
        relative_list.append(list(coordinates))
        local_list.append(list(matrix[:,3][:3]))
        mixed_list.append(mixed)

    df_mixed = pd.DataFrame(mixed_list)
    df_mixed.columns = ["Mx", "My", "Mztop", "Mzbot"]
    return df_mixed

# Function to save coordinates to text files
def save_coordinates_to_file(df, filename):
    with open(filename, 'w') as file:
        for index, row in df.iterrows():
            file.write(' '.join(map(str, row.values)) + '\n')

# Main function to integrate all tasks
def main():
    # Train the model
    train_model()

    # Perform detection on training images
    detect_images(model_path, source_path, detect_save_folder)
    latest_detect_exp_folder = max(glob.glob(os.path.join(detect_save_folder, 'exp*', 'labels')), key=os.path.getctime)

    # Plot comparison for training dataset
    plot_comparison_image(source_path, source_path, latest_detect_exp_folder, detect_save_folder)

    # Perform detection on validation images
    detect_images(model_path, detect_source_path, detect_save_folder)
    latest_detect_exp_folder_val = max(glob.glob(os.path.join(detect_save_folder, 'exp*', 'labels')), key=os.path.getctime)

    # Plot comparison for validation dataset
    plot_comparison_image(detect_source_path, detect_source_path, latest_detect_exp_folder_val, detect_save_folder)

    # Process IFC file and get mixed coordinates
    df_mixed = process_ifc_file(ifc_file_path)

    # Save mixed coordinates to text files
    save_coordinates_to_file(df_mixed, 'mixed_coordinates.txt')

if __name__ == "__main__":
    main()

