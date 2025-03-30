import json
from typing import Dict, Any
import os 
import ffmpeg
import whisper
import torch
from pathlib import Path
import random
from openai import OpenAI
from google import genai
from dotenv import load_dotenv
import os
from datetime import datetime

######################################快捷控制台######################################
current_dir = os.path.dirname(os.path.abspath(__file__))


ALLOWED_CLASS = ["Sphere", "Cylinder","Cuboid"]#已经完成的体
json_store_location="C:\\Users\\Mark\\Desktop\\xyloweft\\object_system\\XyloMail"
voice_location="C:\\Users\\Mark\\Desktop\\xyloweft\\voices\\test.m4a"

######################################初始化######################################




def test():#测试是否能正确调取
    print("muthaphuckaa")
    return 5

################## Saving and transporting the data ##################

def get_current_time():
    now = datetime.now()
    return f"{now.day:02d}{now.hour:02d}{now.minute:02d}{now.second:02d}"


def create_empty_json(folder_path, file_name):
        # 确保文件夹存在
    os.makedirs(folder_path, exist_ok=True)
        
        # 组合完整路径
    file_path = os.path.join(folder_path, file_name)
        
        # 写入空JSON对象
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, indent=4)

def save_json_string_to_file(json_string, file_path):
    """
    将包含JSON的字符串保存到指定路径的文件中。

    :param json_string: 包含JSON的字符串
    :param file_path: 目标文件路径（包括文件名）
    """
    try:
        # 检查文件是否已存在
        if os.path.exists(file_path):
            print(f"文件 {file_path} 已存在，未覆盖。")

        # 确保目标文件夹存在，如果不存在则创建
        dir_path = os.path.dirname(file_path)
        if dir_path:  # 如果路径包含目录
            os.makedirs(dir_path, exist_ok=True)
            if not os.access(dir_path, os.W_OK):
                print(f"无权限在目录 {dir_path} 中创建文件。")
                return

        # 将字符串解析为JSON对象（确保字符串是有效的JSON）
        json_data = json.loads(json_string)
        file_name=str(get_current_time())+".json"
        # 将JSON数据写入文件
        create_empty_json(json_store_location, file_name)
        file_path = os.path.join(json_store_location,file_name)
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

        print(f"JSON数据已成功保存到 {file_path}")
    except json.JSONDecodeError as e:
        print(f"JSON字符串解析失败: {e}")
    except PermissionError:
        print(f"无权限写入文件或目录: {file_path}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

def search_files_by_time(folder: str):
    pass

#################### Voice to str #################################

#def voice_to_str(location):
    """
    convert an audio to word
    requires and only requires 6gb VRAM
    do not convert mp3 with bgm

    Args:
        models (str): the transcrib model to be used. requires pre-load of model to ensure functionality(see line 4 for detail)
        location (str): specific location of the audio, all "\" need to be converted to "\\" to ensure functionality
    """

    #return voice_model.transcribe(location)

#################### English to JSON Model #################################



def validate_vr_objects(json_data):
    """
    Args:
        json_data (str | dict): JSON-formatted string or a dictionary.

    Returns:
        True if the data is valid JSON, otherwise raises an error.
    """
    try:
        # Convert JSON string to dictionary if needed
        if isinstance(json_data, str):
            json_data = json.loads(json_data)  # Parse JSON string to dict

        if not isinstance(json_data, dict):
            raise ValueError("Input must be a JSON object (dictionary)")

        # Iterate over each object in the JSON dictionary
        for obj_name, obj_data in json_data.items():
            # Validate general attributes: position, traits, and subdivisions
            if "position" not in obj_data or not isinstance(obj_data["position"], list) or len(obj_data["position"]) != 3:
                raise ValueError(f"{obj_name}: 'position' must be a list of three elements")

            if "traits" not in obj_data or not isinstance(obj_data["traits"], dict):
                raise ValueError(f"{obj_name}: Missing or invalid 'traits' dictionary")

            obj_type = obj_data["traits"].get("type")

            if obj_type not in ALLOWED_CLASS:
                raise ValueError(f"{obj_name}: Must be a defined shape")
            
            obj_scale = obj_data.get("scale")

            if any(value <= 0 for value in obj_scale):
                raise ValueError(f"{obj_name}: 'scale' must be a number larger than 0")

            # Validate object-specific attributes
            if obj_type == "Sphere":
                required_keys = ["pivot", "rotation", "radius"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                if any(value <= 0 for value in obj_data["traits"]["radius"]):
                    raise ValueError(f"{obj_name}: 'radius' values must all be positive")

                # Check hollow condition for Sphere
                if "variant" in obj_data and "hollow" in obj_data["variant"] and obj_data["variant"]["hollow"]["enabled"] != 0:
                    if any(inner > outer for inner, outer in zip(obj_data["variant"]["hollow"]["inner_radius"], obj_data["traits"]["radius"])):
                        raise ValueError(f"{obj_name}: 'inner_radius' must not be greater than 'radius'")
                for key in ["pivot", "inner_radius"]:
                    if key not in obj_data["variant"]["hollow"] or not isinstance(obj_data["variant"]["hollow"][key], list) or len(obj_data["variant"]["hollow"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")
                if any(value <= 0 for value in obj_data["variant"]["hollow"]["inner_radius"]):
                    raise ValueError(f"{obj_name}: 'inner_radius' values must all be positive")

                # Check if the subdivision for Sphere is valid
                allowed_subdivisions = [4, 6, 8, 12, 20]
                if obj_data["traits"]["subdivision"] not in allowed_subdivisions:
                    raise ValueError(f"{obj_name}: 'subdivision' for Sphere must be one of {allowed_subdivisions}")

            elif obj_type == "Pyramid":  # Updated to "Pyramid" from "Cylinder"
                required_keys = ["radius_top", "radius_bottom"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], (int, float)):
                        raise ValueError(f"{obj_name}: '{key}' must be a numeric value")
                required_list = ["pivot","rotation"]
                for lst_key in required_list:
                    if lst_key not in obj_data["traits"] or not isinstance(obj_data["traits"][lst_key], list):
                        raise ValueError(f"{obj_name}: '{key}' must be a list value")


                # Check if the subdivision for Pyramid is valid (between 3 and 100)
                if not (3 <= obj_data["traits"]["subdivision"] <= 100):
                    raise ValueError(f"{obj_name}: 'subdivision' for Pyramid must be between 3 and 100")

                # Check hollow condition for Pyramid
                if "variant" in obj_data and "inner_sub_cylinder" in obj_data["variant"] and obj_data["variant"]["inner_sub_cylinder"]["enabled"] != 0:
                    inner_radius_top = obj_data["variant"]["inner_sub_cylinder"].get("inner_radius_top", 0)
                    inner_radius_bottom = obj_data["variant"]["inner_sub_cylinder"].get("inner_radius_bottom", 0)
                    outer_radius_top = obj_data["traits"].get("radius_top", 0)
                    outer_radius_bottom = obj_data["traits"].get("radius_bottom", 0)
                    if inner_radius_top >= outer_radius_top:
                        raise ValueError(f"{obj_name}: 'inner_radius_top' must not be greater than 'radius_top'")
                    if inner_radius_bottom >= outer_radius_bottom:
                        raise ValueError(f"{obj_name}: 'inner_radius_bottom' must not be greater than 'radius_bottom'")
                    if inner_radius_top < 0 :
                        raise ValueError(f"{obj_name}: 'inner_radius_top' must be positive")
                    if inner_radius_bottom < 0:
                        raise ValueError(f"{obj_name}: 'inner_radius_bottom' must be positive")

                # If subdivided is enabled, check both subdivision and inner subdivision must be 20
                if "variant" in obj_data and "subdivided" in obj_data["variant"] and obj_data["variant"]["subdivided"]["enabled"] != 0:
                    if obj_data["traits"]["subdivision"] != 20:
                        raise ValueError(f"{obj_name}: 'subdivision' must be 20 when 'subdivided' is enabled")
                    if "inner_subdivision" in obj_data["variant"]["subdivided"] and obj_data["variant"]["subdivided"]["inner_subdivision"] != 20:
                        raise ValueError(f"{obj_name}: 'inner_subdivision' must be 20 when 'subdivided' is enabled")

            elif obj_type == "Cuboid":
                required_keys = ["pivot", "rotation", "dimension"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                if any(value <= 0 for value in obj_data["traits"]["dimension"]):
                    raise ValueError(f"{obj_name}: 'dimension' values must all be positive")

                # Check hollow condition for Cuboid
                if "variant" in obj_data and "hollow" in obj_data["variant"] and obj_data["variant"]["hollow"]["enabled"] != 0:
                    inner_dimension = obj_data["variant"]["hollow"].get("inner_dimension", [0, 0, 0])
                    if any(inner > outer for inner, outer in zip(inner_dimension, obj_data["traits"]["dimension"])):
                        raise ValueError(f"{obj_name}: 'inner_dimension' must not be greater than 'dimension'")
                    if any(value for value in inner_dimension):
                        raise ValueError(f"{obj_name}: 'inner_dimension' must be positive") 

            else:
                raise ValueError(f"{obj_name}: Unknown object type '{obj_type}'")

        return True  # Validation successful

    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return f"Validation Error: {e}"

######################### Encoding JSON Structure ################################
def generate_unique_key(geotype, class_name, index):
    """
    Generate a unique key based on the first letter of geotype, first letter of class name,
    index in the list, and a random 4-digit number.
    """
    random_number = random.randint(1000, 9999)
    return f"{geotype[0]}{class_name[0]}{index}{random_number}"

def transform_json_list(json_list:list):
    """
    Transform a list of JSON objects into a structured dictionary with encoded keys.
    """
    transformed_data = {}
    
    for index in json_list:
        obj = json_list[index]
        geotype = obj.get("geotype", "S")  # Default to 'S' if missing for simple object
        class_name = obj.get("class", "C")  # Default to 'C' if missing for cuboid
        key = generate_unique_key(geotype, class_name, index)
        
        transformed_data[key] = obj
    
    return transformed_data

