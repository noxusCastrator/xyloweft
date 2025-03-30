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

ALLOWED_CLASS = ["Sphere", "Cylinder","Cuboid"]
device = 'cuda' if torch.cuda.is_available() else 'cpu'
voice_model=whisper.load_model('turbo').to(device)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get API keys
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
o3_api_key = os.getenv("O3_API_KEY")

json_store_location=("C:\\Users\\Mark\\Desktop\\xyloweft\\object_system\\XyloMail\\data.json")

client = genai.Client(api_key=gemini_api_key)




with open(os.path.join(current_dir, 'education.json'), 'r', encoding='utf-8') as file_education:
    education = json.load(file_education)
with open(os.path.join(current_dir, 'shape.json'), 'r', encoding='utf-8') as file_shape:
    shape = json.load(file_shape)




def test():
    print("muthaphuckaa")
    return 5


################## Saving and transporting the data ##################

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

        # 将JSON数据写入文件
        with open(file_path, 'w') as file:
            json.dump(json_data, file)

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

#################### English to JSON Model #################################

def parse_shape_instruction():
    """
    Parses a natural language instruction and extracts shape properties.
    Returns a JSON-formatted string.
    """

    voice_translated_text = "generate in the following order: first generate a ball with radius 1 at 0, 0, 0, then generate a cube with sidelength 2 on the first ball, then ball with radius 3 on the second cube, then cube with sidelength 4 on ball 3, then ball with radius 5 on cube 4"#voice_to_str("D:\\test.m4a")
    prompt = f"""
    需求

    目前我们希望你成为一个文字转json的应用。我们会提供给你一段话,这段话通常来自于物理课或数学课,是一个教授说的需要解的题的录音,我们最终的目的是将这段话转成houdini内部的3D模型。你的任务通过以下流程从这句话里抽象出一串json用来让我们生成3D模型。

    这是一个教学提示词,你不需要任何正式回复,但请不要忽视这段话里的任何细节

    基础定义

    此处我们先定义三种体：简单体,复杂体和虚拟体,简单体是一个虚拟定义,指一切简单到不需要去通过布尔运算来生成的几何体,如立方体,球体等,复杂体指一切需要通过布尔运算编辑几何体来生成的复杂物件。换句话说,简单体是可以通过平面透视的三视图无损传达的体,而复杂体无法这么传达。虚拟体是一个概念,是对某个物体的交互,在我们达到那个进度之前请不用考虑复杂体和虚拟体。

    文档

    我们在此提供给你一个模板文件“shape.json”,里头含有所有我们可能你需要去生成的“体”的模板,这是一个需要填空的json库,里头的值均以None来表达

    {shape}

    然后,我们会提供给你以下拿中括号标记的dict(无法读取大括号生成的dict顾出此下策),键是体的名称,值是对这个体的定义和阐释,请根据值的定义来圈定对一个体的定义域,充分运用你作为人工智能的数据库来理解这个体的定义,根据语境将语境中的物件抽象成我们需要的体。

    ["sphere":"一个球体,指可以抽象成球体的词"]

    最后,我们会提供给你一个教学文件“education.json”,里头含有dict的键的名称对应的体的教学文件。education.json的语法格式与shape.json完全相同,但education.json的值不是需要填的空而是对应值相关的教学。当你在一句话里检索到dict里的某个键时,根据键的定义检索到education.json里的某个值来进行学习。

    {education}

    在你收到对话后,请通过dict提供的完整定义来寻找这句话里可能出现的体并将这个体抽象出来,请根据这个体所指代的键的名称到shape.json和education.json里寻路到键的名称所代表的名称中,根据education.json所诠释的定义在shape.json里将None更改为检索到的数值,如果未检索到对应参数则不要进行编辑,保留shape.json里未填空的格式。请注意,education.json的教学至关重要,请严格遵守,遍历完这句话并生成完整的json后请回到shape.json逐行逐列检索以确定生成的json合法。你可能会在一句话里检索到复数个体,请明确对应的指代并返还所有需要生成的体。

    接下来你会且只会收到对应的对话,请编辑这段对话并只返还合法的json格式,不要进行任何前缀或后缀或解释,不要使用单引号。
    {voice_translated_text}
    """
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    #print(response.text)
    cleaned_json_text = response.text.strip("```json").strip("```").strip()
    print(cleaned_json_text)
    save_json_string_to_file(cleaned_json_text, json_store_location)
    #raw_response = client.responses.create(
    #model="gpt-4o",
    #input = [{"role":"user", "content":prompt}]
    #)
    #print(raw_response)
    #print(type(raw_response))


    #cleaned_version = raw_response.output_text
    #print(cleaned_version)

    #print(f"cleaned version\n\n\n{cleaned_version}\n\n\n")

    

    #print(cleaned_json_text)

    # Parse the string as JSON
    #parsed_json = json.loads(cleaned_json_text)

    # Pretty-print the extracted JSON
    #print(json.dumps(parsed_json, indent=4))

parse_shape_instruction()


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

                # Check hollow condition for Sphere
                if "variant" in obj_data and "hollow" in obj_data["variant"] and obj_data["variant"]["hollow"]["enabled"] != 0:
                    if any(inner > outer for inner, outer in zip(obj_data["variant"]["hollow"]["inner_radius"], obj_data["traits"]["radius"])):
                        raise ValueError(f"{obj_name}: 'inner_radius' must not be greater than 'radius'")

            elif obj_type == "Cylinder":
                required_keys = ["pivot", "rotation"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                for key in ["radius_top", "radius_bottom"]:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], (int, float)) or obj_data["traits"][key] <= 0:
                        raise ValueError(f"{obj_name}: '{key}' must be a positive numeric value")

                # Check hollow condition for Cylinder
                if "variant" in obj_data and "inner_sub_cylinder" in obj_data["variant"] and obj_data["variant"]["inner_sub_cylinder"]["enabled"] != 0:
                    inner_radius_top = obj_data["variant"]["inner_sub_cylinder"].get("inner_radius_top", [0, 0])
                    inner_radius_bottom = obj_data["variant"]["inner_sub_cylinder"].get("inner_radius_bottom", [0, 0])
                    outer_radius_top = obj_data["traits"].get("radius_top", [0, 0])
                    outer_radius_bottom = obj_data["traits"].get("radius_bottom", [0, 0])
                    if any(inner > outer for inner, outer in zip(inner_radius_top, outer_radius_top)):
                        raise ValueError(f"{obj_name}: 'inner_radius_top' must not be greater than 'radius_top'")
                    if any(inner > outer for inner, outer in zip(inner_radius_bottom, outer_radius_bottom)):
                        raise ValueError(f"{obj_name}: 'inner_radius_bottom' must not be greater than 'radius_bottom'")

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

