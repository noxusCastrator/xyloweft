import json
from typing import Dict, Any
import os 
import ffmpeg
import whisper
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
voice_model=whisper.load_model('turbo').to(device)

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

def voice_to_str(location:str):
    pass

def parse_shape_instruction(instruction: str, library:str) -> str:
    pass

def replacing_defaults(input_data):
    pass

def validate_vr_objects(json_data):
    pass

def generate_unique_key(geotype, class_name, index):
    pass




def main():
    pass