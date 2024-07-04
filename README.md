# CPMIP: Construction Project Monitoring and Inspection Pipeline

CPMIP automates the monitoring and inspection of construction projects using computer vision techniques. This project leverages YOLOv5 for object detection, processes as-built images, and extracts relevant data from IFC files.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.7 or higher
- Git

### Setup

1. **Clone the Repository**

    ```sh
    git clone https://github.com/sgh1998/CPMIP
    cd CPMIP
    ```

2. **Create a Virtual Environment**

    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install Required Packages**

    ```sh
    pip install -r requirements.txt
    ```

4. **Run the Setup Script**

    The setup script will create necessary directories, copy the model file, and clone the YOLOv5 repository.

    ```sh
    python setup.py
    ```

## Configuration

1. **Specify the Viewpoint**

    Open the `user.yaml` file and set the `view_direction` to one of the following values: `east`, `west`, `north`, or `south`.

    ```yaml
    view_direction: "east"
    ```

2. **Copy Your IFC File and As-Built Images**

    - Copy your IFC file to the path specified in `ifc_model` in the `user.yaml` file.
    - Copy your as-built images to the path specified in `asbuilt_images` in the `user.yaml` file.

### Example `user.yaml`

```yaml
# Base folder for all relative paths
major_folder: "G:/CPMIP_Data"

# The following section is used by code: DO NOT CHANGE IT
paths:
  model: "advanced/yolo_model/best.pt"
  asbuilt_images: "user_inputs/asbuilt_images"  # user input
  ifc_model: "user_inputs/ifc_model/Project52.ifc"  # user input
  detect_save_folder: "advanced/detection_results"
  output_folder_base: "advanced/asbuilt_coordinates"
  east_txt_path: "advanced/asplanned_coordinates/east.txt"  # Path for the east output text file
  west_txt_path: "advanced/asplanned_coordinates/west.txt"  # Path for the west output text file
  north_txt_path: "advanced/asplanned_coordinates/north.txt"  # Path for the north output text file
  south_txt_path: "advanced/asplanned_coordinates/south.txt"  # Path for the south output text file

# User-defined parameter for view direction (east, west, north, south)
view_direction: "east"
