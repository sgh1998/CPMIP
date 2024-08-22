import subprocess
import sys

def run_script(script_name):
    try:
        print(f"Running {script_name}...")
        subprocess.run([sys.executable, script_name], check=True)
        print(f"{script_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        sys.exit(1)

def main():
    # Paths to each minor script
    asplanned_script = "asplanned.py"
    asbuilt_script = "asbuilt.py"
    asbuilt_analysis_script = "asbuilt_analysis.py"
    quantification_script = "quantification.py"

    # Run the scripts in the specified order
    run_script(asplanned_script)
    run_script(asbuilt_script)
    run_script(asbuilt_analysis_script)
    run_script(quantification_script)

    print("All scripts completed successfully!")

if __name__ == "__main__":
    main()
