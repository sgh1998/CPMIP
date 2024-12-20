import os
import yaml
import subprocess

def load_config(config_file="user.yaml"):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_full_path(major_folder, relative_path):
    return os.path.join(major_folder, relative_path.replace('\\', '/'))

def create_directories(config):
    major_folder = config['major_folder']
    paths = config['paths']

    # Ensure all directories exist
    for key, path in paths.items():
        full_path = get_full_path(major_folder, path)
        if os.path.splitext(full_path)[1]:  # if it's a file path
            directory = os.path.dirname(full_path)
        else:
            directory = full_path
        os.makedirs(directory, exist_ok=True)
        print(f"Directory created or already exists: {directory}")

def copy_model_file():
    config = load_config()
    major_folder = config['major_folder']
    paths = config['paths']
    
    # Construct full path for the YOLO model
    model_path = get_full_path(major_folder, paths['model'])

    create_directories(config)

    # Path to the model file in the repository
    repo_model_path = os.path.join(os.path.dirname(__file__), 'trained_models', 'best.pt')
    
    if not os.path.exists(repo_model_path):
        raise FileNotFoundError(f"Model file not found in repository: {repo_model_path}")

    # Copy the model file from the repository to the target directory
    with open(repo_model_path, 'rb') as src_file:
        with open(model_path, 'wb') as dst_file:
            dst_file.write(src_file.read())
    print(f"Model file copied to: {model_path}")

def clone_yolov5(repo_url="https://github.com/ultralytics/yolov5.git", clone_dir="yolov5"):
    if not os.path.exists(clone_dir):
        print(f"Cloning YOLOv5 repository into {clone_dir}...")
        subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
        print("YOLOv5 repository cloned successfully.")
    else:
        print(f"YOLOv5 repository already exists in {clone_dir}.")

def setup():
    clone_yolov5()
    copy_model_file()
    print("Setup complete. All directories created, files copied, and YOLOv5 repository cloned.")

if __name__ == "__main__":
    setup()
