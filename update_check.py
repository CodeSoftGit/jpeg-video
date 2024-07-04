import os
import requests
import zipfile
import subprocess
import json
import sys
from packaging import version

# Constants
APP_PATH = r"C:\Program Files\CodeSoft\JPEG Video"
GITHUB_REPO = "CodeSoftGit/jpeg-video"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
CONFIG_FILE = os.path.join(APP_PATH, "config.json")
EXE_PATH = os.path.join(APP_PATH, "jpeg-video.exe")

def get_current_version():
    version_file = os.path.join(APP_PATH, "version.txt")
    with open(version_file, "r") as f:
        return f.read().strip()

def get_latest_version():
    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()
    return response.json()["tag_name"]

def download_and_extract_update(download_url):
    response = requests.get(download_url)
    response.raise_for_status()
    
    zip_path = os.path.join(APP_PATH, "jpeg-video.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)
    
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(APP_PATH)
    
    os.remove(zip_path)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"auto_update": True}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def check_for_updates():
    config = load_config()
    
    try:
        current_version = get_current_version()
        latest_version = get_latest_version()
        
        if version.parse(latest_version) > version.parse(current_version):
            print(f"New version available: {latest_version}")
            if config["auto_update"]:
                print("Downloading and installing update...")
                download_url = f"https://github.com/{GITHUB_REPO}/releases/download/{latest_version}/jpeg-video.zip"
                download_and_extract_update(download_url)
                print("Update installed successfully.")
            else:
                print("Auto-update is disabled. Please update manually.")
        else:
            print("You are using the latest version.")
    
    except Exception as e:
        print(f"Error checking for updates: {e}")

def toggle_auto_update():
    config = load_config()
    config["auto_update"] = not config["auto_update"]
    save_config(config)
    status = "enabled" if config["auto_update"] else "disabled"
    print(f"Auto-update is now {status}.")

def run_application():
    try:
        subprocess.Popen(EXE_PATH)
    except Exception as e:
        print(f"Error launching the application: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--toggle-auto-update":
        toggle_auto_update()
    else:
        check_for_updates()
        run_application()