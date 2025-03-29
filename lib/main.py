import json
from typing import Dict, Any
import os 
# import ffmpeg
import whisper
import torch
from pathlib import Path
import random
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
import os


device = 'cuda' if torch.cuda.is_available() else 'cpu'
voice_model=whisper.load_model('turbo').to(device)


# Load the .env file
load_dotenv()

# Get API keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
o3_api_key = os.getenv("O3_API_KEY")

if not gemini_api_key or not o3_api_key:
    raise ValueError("API keys are missing. Make sure they are set in the .env file.")

print("API keys loaded successfully!")

################## Saving and transporting the data ##################

def save_json_string_to_file(json_string, file_path):
    """
    将包含JSON的字符串保存到指定路径的文件中。

    :param json_string: 包含JSON的字符串
    :param file_path: 目标文件路径（包括文件名）
    :param overwrite: 是否覆盖已存在的文件(默认为False)
    """
    try:
        # 检查文件是否已存在
        if os.path.exists(file_path):
            print(f"文件 {file_path} 已存在，未覆盖。")
            return

        # 确保目标文件夹存在，如果不存在则创建
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 将字符串解析为JSON对象（确保字符串是有效的JSON）
        json_data = json.loads(json_string)

        # 将JSON数据写入文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)

        print(f"JSON数据已成功保存到 {file_path}")
    except json.JSONDecodeError as e:
        print(f"JSON字符串解析失败: {e}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

def search_files_by_time(folder: str):
    pass

#################### Voice to str #################################

def voice_to_str(location):
    """
    convert an audio to word
    requires and only requires 6gb VRAM
    do not convert mp3 with bgm

    Args:
        models (str): the transcrib model to be used. requires pre-load of model to ensure functionality(see line 4 for detail)
        location (str): specific location of the audio, all "\" need to be converted to "\\" to ensure functionality
    """

    return voice_model.transcribe(location)


with open('education.json', 'r', encoding='utf-8') as file_education:
    # 加载 JSON 数据
    education = json.load(file_education)
with open('shape.json', 'r', encoding='utf-8') as file_shape:
    # 加载 JSON 数据
    shape = json.load(file_shape)


def parse_shape_instruction(instruction: str, library:str) -> str:
    pass

def replacing_defaults(input_data):
    pass

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

            if "subdivision" not in obj_data["traits"] or not isinstance(obj_data["traits"]["subdivision"], (int, float)) or obj_data["traits"]["subdivision"] < 4:
                raise ValueError(f"{obj_name}: 'subdivision' must be a numeric value >= 4")

            if obj_type not in ALLOWED_CLASS:
                raise ValueError(f"{obj_name}: Must be a defined shape")

            # Validate object-specific attributes
            if obj_type == "Sphere":
                required_keys = ["pivot", "rotation", "radius"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                if any(value <= 0 for value in obj_data["traits"]["radius"]):
                    raise ValueError(f"{obj_name}: 'radius' values must all be positive")

            elif obj_type == "Cylinder":
                required_keys = ["pivot", "rotation"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                for key in ["radius_positive", "radius_negative"]:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], (int, float)) or obj_data["traits"][key] <= 0:
                        raise ValueError(f"{obj_name}: '{key}' must be a positive numeric value")

            elif obj_type == "Cuboid":
                required_keys = ["pivot", "rotation", "dimension"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                if any(value <= 0 for value in obj_data["traits"]["dimension"]):
                    raise ValueError(f"{obj_name}: 'dimension' values must all be positive")

            else:
                raise ValueError(f"{obj_name}: Unknown object type '{obj_type}'")

        return True  # Validation successful

    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return f"Validation Error: {e}"

def generate_unique_key(geotype, class_name, index):
    pass




def main():
    pass