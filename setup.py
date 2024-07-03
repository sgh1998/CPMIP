import os
import yaml
import requests

def load_config(config_file="user.yaml"):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_full_path(major_folder, relative_path):
    return os.path.join(major_folder, relative_path)

def create_directories(config):
    major_folder = config['major_folder']
    paths = config['paths']

    # Ensure all directories exist
    for key, path in paths.items():
        full_path = get_full_path(major_folder, path)
        directory = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Check if the download was successful
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def main():
    config = load_config()
    major_folder = config['major_folder']
    paths = config['paths']
    
    # Construct full path for the YOLO model
    model_path = get_full_path(major_folder, paths['model'])

    create_directories(config)

    # URL for the YOLO model
    yolo_model_url = "https://drive.google.com/uc?export=download&id=12AAP83n_-zfKLlIqsZO5M0pzBFotPyE1"
    
    # Download the YOLO model
    download_file(yolo_model_url, model_path)

    print("Setup complete. All directories created and files downloaded.")

if __name__ == "__main__":
    main()
