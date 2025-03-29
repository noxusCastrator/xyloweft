import os
import sys

# Print debugging info
print("Step 1: Start script")

# Get the absolute path of the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Add 'lib/' to sys.path so Python can find it
lib_dir = os.path.join(base_dir, "lib")
sys.path.append(lib_dir)

print("Step 2: sys.path updated")
print(sys.path)  # Print the paths to check if 'lib/' is there

# Try to import main.py
try:
    import main
    print("Step 3: Successfully imported main.py")
except ModuleNotFoundError:
    print("Error: main.py was not found! Check your paths.")

print("Step 4: End of script")