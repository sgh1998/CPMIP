import numpy as np
import cv2 as cv
import random
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import yaml
import os
import glob

# Load configuration from YAML
def load_config(config_file="user.yaml"):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_full_path(major_folder, relative_path):
    return os.path.join(major_folder, relative_path)

def process_image(image_file_path, view, asbuilt_output_folder):
    print(f"\nProcessing image: {image_file_path}")
    
    # Get the image file name without the extension
    file_name = os.path.splitext(os.path.basename(image_file_path))[0]

    # Find the corresponding text file based on the image name and view direction
    if view == "east":
        net_output_file = os.path.join(asbuilt_output_folder, f"east_output", f"{file_name}.txt")
    elif view == "west":
        net_output_file = os.path.join(asbuilt_output_folder, f"west_output", f"{file_name}.txt")
    elif view == "north":
        net_output_file = os.path.join(asbuilt_output_folder, f"north_output", f"{file_name}.txt")
    elif view == "south":
        net_output_file = os.path.join(asbuilt_output_folder, f"south_output", f"{file_name}.txt")
    else:
        raise ValueError(f"Unknown view direction: {view}")

    if not os.path.exists(net_output_file):
        print(f"Warning: Text file not found for image {file_name}. Skipping.")
        return

    try:
        # Load the data from the text file
        data_net = np.loadtxt(net_output_file, delimiter=',')

        # Read the image
        I = cv.imread(image_file_path)
        if I is None:
            print(f"Warning: Could not read image {file_name}. Skipping.")
            return

        m, n, _ = I.shape

        bottom_points = []
        column_data = []
        column_heights = []

        # Process column data
        for xt, yt, xb, yb in data_net:
            height = yt - yb
            xb_transformed = int(xb)
            yb_transformed = int(m - yb)
            xt_transformed = int(xt)
            yt_transformed = int(m - yt)
            
            xb, yb, xt, yt = map(int, [xb, yb, xt, yt])

            bottom_points.append((xb, yb))
            column_data.append([xt, yt, xb, yb])
            column_heights.append(height)
            
            cv.circle(I, (xb_transformed, yb_transformed), 4, (255, 0, 0), 2)

        # Calculate average height
        average_column_height = np.mean(column_heights)
        print(f"Average height of columns: {average_column_height:.2f} pixels")

        # DBSCAN clustering
        x_coords = np.array([x for x, _ in bottom_points]).reshape(-1, 1)
        eps_value = np.average(np.diff(np.sort(x_coords[:, 0]))) * 1.2
        print(f'Calculated eps: {eps_value}')
        
        dbscan = DBSCAN(eps=eps_value, min_samples=1)
        clusters = dbscan.fit_predict(x_coords)

        # Create cluster dictionary
        cluster_dict = {}
        for i, cluster_id in enumerate(clusters):
            if cluster_id != -1:
                if cluster_id not in cluster_dict:
                    cluster_dict[cluster_id] = []
                cluster_dict[cluster_id].append(column_data[i])

        # Calculate scaled distances
        cluster_distances = []
        lowest_y_coords = []

        for cluster in cluster_dict.values():
            lowest_y = min([col[3] for col in cluster])
            lowest_y_coords.append(lowest_y)
        
        avg_lowest_y = np.mean(lowest_y_coords)

        for cluster_id, columns in cluster_dict.items():
            lowest_col = min(columns, key=lambda x: x[3])
            lowest_y = lowest_col[3]
            column_height = lowest_col[1] - lowest_col[3]
            
            scaled_distance = (lowest_y - avg_lowest_y) / column_height
            cluster_distances.append({
                'cluster_id': cluster_id,
                'scaled_distance': scaled_distance,
                'lowest_y': lowest_y
            })

        # Assign floors and collect results
        all_floors_info = []
        for cluster_id, columns in cluster_dict.items():
            cluster_info = next(cd for cd in cluster_distances if cd['cluster_id'] == cluster_id)
            
            column_floor_info = assign_floors_with_gaps(
                columns, 
                average_column_height,
                cluster_info['scaled_distance']
            )
            
            all_floors_info.extend(column_floor_info)
            
            # Detailed printing of cluster information
            print(f"\nResults for Cluster {cluster_id}:")
            print(f"Scaled Distance: {cluster_info['scaled_distance']:.3f}")
            print(f"Starting Floor: {'1' if cluster_info['scaled_distance'] <= DISTANCE_THRESHOLD else '2'}")
            print("\nColumns in this cluster:")
            print("Xtop    Ytop    Xbot    Ybot    Floor")
            print("-" * 45)
            
            # Sort by floor number for clearer output
            sorted_floor_info = sorted(column_floor_info, key=lambda x: x[4])
            for xt, yt, xb, yb, floor in sorted_floor_info:
                print(f"{xt:<7.1f} {yt:<7.1f} {xb:<7.1f} {yb:<7.1f} {floor}")
            print("\n")

        # Save results
        output_file_name = f"{view}_{file_name}_floor_info.txt"
        output_file_path = os.path.join(asbuilt_output_folder, output_file_name)
        with open(output_file_path, 'w') as f:
            f.write("Xtop, Ytop, Xbot, Ybot, Floor\n")
            for entry in all_floors_info:
                f.write(f"{entry[0]}, {entry[1]}, {entry[2]}, {entry[3]}, {entry[4]}\n")

        print(f"Results saved to {output_file_path}")

        # Visualize clusters
        plt.figure(figsize=(10, 6))
        for cluster_id, coordinates in cluster_dict.items():
            x_values = [x[2] for x in coordinates]
            y_values = [cluster_id] * len(x_values)
            plt.scatter(x_values, y_values, label=f'Cluster {cluster_id}', s=100)

        plt.xlabel('X Coordinate')
        plt.ylabel('Cluster ID')
        plt.title(f'X Coordinates of Columns by Cluster - {file_name}')
        plt.legend()
        plt.grid(True)
        
        # Save plot
        plot_path = os.path.join(asbuilt_output_folder, f"{view}_{file_name}_clusters.png")
        plt.savefig(plot_path)
        plt.close()

    except Exception as e:
        print(f"Error processing {file_name}: {str(e)}")

def assign_floors_with_gaps(column_data, avg_height, scaled_distance, tolerance=1.93):
    column_data.sort(key=lambda col: col[3], reverse=True)
    column_floor_info = []

    if scaled_distance <= DISTANCE_THRESHOLD:
        floor_number = 1
    else:
        floor_number = 2

    prev_y = column_data[-1][3]

    for idx, col in enumerate(reversed(column_data)):
        xt, yt, xb, yb = col
        if idx == 0:
            column_floor_info.append((xt, yt, xb, yb, floor_number))
        else:
            vertical_distance = yb - prev_y
            
            if vertical_distance > 2 * avg_height * tolerance:
                floor_number += 3
            elif vertical_distance > avg_height * tolerance:
                floor_number += 2
            else:
                floor_number += 1
            
            column_floor_info.append((xt, yt, xb, yb, floor_number))
        
        prev_y = yb

    column_floor_info.reverse()
    return column_floor_info

def main():
    # Load configuration
    config = load_config()
    major_folder = config['major_folder']
    asbuilt_output_folder = get_full_path(major_folder, config['paths']['output_folder_base'])
    asbuilt_images_path = get_full_path(major_folder, config['paths']['asbuilt_images'])
    view = config['view_direction'].strip().lower()

    # Define threshold for floor determination
    global DISTANCE_THRESHOLD
    DISTANCE_THRESHOLD = 0.31

    # Process all images in the directory
    image_files = glob.glob(os.path.join(asbuilt_images_path, "*.jpg")) + \
                 glob.glob(os.path.join(asbuilt_images_path, "*.png"))
    
    print(f"Found {len(image_files)} images to process")
    
    for image_file_path in image_files:
        process_image(image_file_path, view, asbuilt_output_folder)

if __name__ == "__main__":
    main()