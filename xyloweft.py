import os
import sys

print("programme initiated")

base_dir = os.path.abspath(os.path.dirname(__file__))

lib_dir = os.path.join(base_dir, "lib")
sys.path.append(lib_dir)

#print(sys.path)  
try:
    import main
    print("Successfully imported main.py")
except ModuleNotFoundError:
    print("Error: main.py was not found")

while True:
    x=input("welcome to temp os, type run to initiate the program, type break to end the program")
    if x=="run":
        string=main.voice_to_str(main.voice_location)
        json=main.parse_shape_instruction()
        print("json")
        print("done")
    elif x=="break":
        break




