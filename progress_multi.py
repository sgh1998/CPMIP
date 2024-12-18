import numpy as np
import yaml
import os
import glob

def load_config(config_file="user.yaml"):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_full_path(major_folder, relative_path):
    return os.path.join(major_folder, relative_path)

def process_single_comparison(asplanned_data, asbuilt_data, image_name):
    # Extract floor numbers from both as-planned and as-built data
    asplanned_floors = asplanned_data[:, -1].astype(int)
    asbuilt_floors = asbuilt_data[:, -1].astype(int)

    # Count columns per floor
    asplanned_counts = np.bincount(asplanned_floors)
    asbuilt_counts = np.bincount(asbuilt_floors)

    # Ensure arrays are same length
    max_floor = max(len(asplanned_counts), len(asbuilt_counts))
    asplanned_counts = np.pad(asplanned_counts, (0, max_floor - len(asplanned_counts)), 'constant')
    asbuilt_counts = np.pad(asbuilt_counts, (0, max_floor - len(asbuilt_counts)), 'constant')

    # Calculate initial percentages
    constructed_percentages = (asbuilt_counts / np.where(asplanned_counts > 0, asplanned_counts, 1)) * 100

    # Sequence Consideration
    adjusted_asbuilt_counts = asbuilt_counts.copy()
    for floor in range(max_floor - 1, 0, -1):
        if adjusted_asbuilt_counts[floor] > 0:
            for lower_floor in range(1, floor):
                if asplanned_counts[lower_floor] > 0:
                    adjusted_asbuilt_counts[lower_floor] = asplanned_counts[lower_floor]

    # Calculate adjusted percentages
    adjusted_constructed_percentages = (adjusted_asbuilt_counts / np.where(asplanned_counts > 0, asplanned_counts, 1)) * 100

    # Calculate overall progress
    total_floors = np.sum(asplanned_counts > 0)
    weighted_progress = np.sum(adjusted_constructed_percentages[1:max_floor] / 100)
    overall_progress = (weighted_progress / total_floors) * 100 if total_floors > 0 else 0

    return {
        'max_floor': max_floor,
        'asplanned_counts': asplanned_counts,
        'adjusted_asbuilt_counts': adjusted_asbuilt_counts,
        'adjusted_percentages': adjusted_constructed_percentages,
        'overall_progress': overall_progress
    }

def main():
    # Load configuration
    config = load_config()
    major_folder = config['major_folder']
    view = config['view_direction']

    # Get as-planned file path
    if view == 'east':
        asplanned_file_path = get_full_path(major_folder, config['paths']['east_txt_path'])
    elif view == 'west':
        asplanned_file_path = get_full_path(major_folder, config['paths']['west_txt_path'])
    elif view == 'north':
        asplanned_file_path = get_full_path(major_folder, config['paths']['north_txt_path'])
    elif view == 'south':
        asplanned_file_path = get_full_path(major_folder, config['paths']['south_txt_path'])
    else:
        raise ValueError(f"Unknown view direction: {view}")

    # Load as-planned data
    asplanned_data = np.loadtxt(asplanned_file_path, delimiter=',')

    # Get as-built output folder
    asbuilt_folder = get_full_path(major_folder, config['paths']['output_folder_base'])
    
    # Find all asbuilt floor info files
    pattern = os.path.join(asbuilt_folder, f"{view}_*_floor_info.txt")
    asbuilt_files = glob.glob(pattern)

    print(f"Found {len(asbuilt_files)} as-built files to analyze")

    # Process each asbuilt file
    for asbuilt_file in asbuilt_files:
        image_name = os.path.basename(asbuilt_file).replace(f"{view}_", "").replace("_floor_info.txt", "")
        print(f"\nProcessing image: {image_name}")

        try:
            # Load as-built data
            asbuilt_data = np.loadtxt(asbuilt_file, delimiter=',', skiprows=1)

            # Process comparison
            results = process_single_comparison(asplanned_data, asbuilt_data, image_name)

            # Save results
            output_file = os.path.join(asbuilt_folder, f"{view}_{image_name}_construction_percentage.txt")
            with open(output_file, 'w') as f:
                f.write(f"Analysis for image: {image_name}\n")
                f.write("Floor, Constructed Percentage, Constructed Columns, Planned Columns\n")
                for floor in range(1, results['max_floor']):
                    if results['asplanned_counts'][floor] > 0:
                        f.write(f"{floor}, {results['adjusted_percentages'][floor]:.2f}%, "
                               f"{results['adjusted_asbuilt_counts'][floor]}, "
                               f"{results['asplanned_counts'][floor]}\n")
                    else:
                        f.write(f"{floor}, No planned columns\n")
                f.write(f"\nOverall Project Progress: {results['overall_progress']:.2f}%\n")

            # Print results
            print(f"\nResults for {image_name}:")
            print("Floor-by-floor progress:")
            for floor in range(1, results['max_floor']):
                if results['asplanned_counts'][floor] > 0:
                    print(f"Floor {floor}: {results['adjusted_percentages'][floor]:.2f}% "
                          f"({results['adjusted_asbuilt_counts'][floor]}/{results['asplanned_counts'][floor]})")
            print(f"Overall Progress: {results['overall_progress']:.2f}%")
            print(f"Results saved to {output_file}")

        except Exception as e:
            print(f"Error processing {image_name}: {str(e)}")

if __name__ == "__main__":
    main()