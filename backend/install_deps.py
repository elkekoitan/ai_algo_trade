import subprocess
import sys
import os

def install_dependencies():
    """
    Reads requirements.txt line by line and installs each package individually.
    """
    # Change current directory to the script's directory
    # This ensures that the relative path to requirements.txt is always correct
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Changed current directory to: {os.getcwd()}")
    
    req_path = 'requirements.txt'
    
    if not os.path.exists(req_path):
        print(f"ERROR: Cannot find requirements.txt at {os.path.abspath(req_path)}")
        return

    print(f"Reading dependencies from {os.path.abspath(req_path)}...")
    
    with open(req_path, 'r') as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith('#'):
                print(f"\\n--- Installing {package} ---")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--no-cache-dir"])
                    print(f"--- Successfully installed {package} ---")
                except subprocess.CalledProcessError as e:
                    print(f"--- FAILED to install {package}. Error: {e} ---")
                    # Optionally, decide if you want to stop on failure
                    # return

if __name__ == "__main__":
    install_dependencies() 