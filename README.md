# CPMIP: Construction Project Monitoring and Inspection Pipeline

CPMIP automates the monitoring and inspection of construction projects using computer vision techniques. This project leverages YOLOv5 for object detection, processes as-built images, and extracts relevant data from IFC files.

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

    ```sh
    python setup.py
    ```

## Usage

1. **Configure the `user.yaml` File**

    Update paths and parameters in `user.yaml` to match your setup.

2. **Run the Main Script**

    ```sh
    python CPM.py
    ```

## Project Structure

