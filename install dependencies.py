import subprocess
import sys
import importlib

# List of pip-installable dependencies
dependencies = ["Pillow"]

def install(package):
    """Install a pip package using the current Python executable"""
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("Checking Python dependencies...\n")

# 1️⃣ Install pip packages
for package in dependencies:
    try:
        importlib.import_module(package)
        print(f"{package} is already installed ✅")
    except ImportError:
        print(f"{package} not found. Installing...")
        install(package)

# 2️⃣ Check tkinter (built-in, but may be missing on some Windows installs)
try:
    import tkinter
    print("tkinter is available ✅")
except ImportError:
    print("WARNING: tkinter is NOT available ❌")
    print("GUI will not work. Make sure your Python installation includes 'tcl/tk'.")

print("\nAll dependencies are ready!")