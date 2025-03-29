# Verifier_test
import json
import os
with open('shape.json', 'r', encoding='utf-8') as file_shape:
    # 加载 JSON 数据
    shape = json.load(file_shape)

ALLOWED_CLASS = ["Sphere", "Cylinder","Cuboid"]
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

            if ("subdivision" not in obj_data["traits"] or not isinstance(obj_data["traits"]["subdivision"], (int, float)) or obj_data["traits"]["subdivision"] < 4) and not obj_type == "Cuboid":
                raise ValueError(f"{obj_name}: 'subdivision' must be a numeric value (20 >= value >= 4)")

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
                
                if obj_data["variant"]["hollow"]["enabled"]:
                    if len(obj_data["variant"]["hollow"]["inner_radius"]) != 3 or any(value <= 0 for value in obj_data["variant"]["hollow"]["inner_radius"]):
                        raise ValueError(f"{obj_name}: 'radius' must be a list of three elements and all values must be positive")

            elif obj_type == "Cylinder":
                required_keys = ["pivot", "rotation"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                for key in ["radius_top", "radius_bottom"]:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], (list)) or len(obj_data["traits"][key]) != 2:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of two elements")
                    if obj_data["traits"][key][0] <= 0 or obj_data["traits"][key][1] <= 0:
                        raise ValueError(f"{obj_name}: '{key}' values must all be positive")

                if obj_data["traits"]["height"] <= 0:
                    raise ValueError(f"height: 'height' must be a positive int value")
                
                if obj_data["variant"]["inner_sub_cylinder"]["enabled"]:
                    for key in ["inner_radius_top", "inner_radius_bottom"]:
                        if key not in obj_data["variant"]["inner_sub_cylinder"] or not isinstance(obj_data["variant"]["inner_sub_cylinder"][key], (list)) or len(obj_data["variant"]["inner_sub_cylinder"][key]) != 2:
                            raise ValueError(f"{obj_name}: '{key}' must be a list of two elements")
                        if any(value <= 0 for value in obj_data["variant"]["inner_sub_cylinder"][key]):
                            raise ValueError(f"{obj_name}: '{key}' all values must be positive")

            elif obj_type == "Cuboid":
                required_keys = ["pivot", "rotation", "dimension"]
                for key in required_keys:
                    if key not in obj_data["traits"] or not isinstance(obj_data["traits"][key], list) or len(obj_data["traits"][key]) != 3:
                        raise ValueError(f"{obj_name}: '{key}' must be a list of three elements")

                if any(value <= 0 for value in obj_data["traits"]["dimension"]):
                    raise ValueError(f"{obj_name}: 'dimension' values must all be positive")

                if obj_data["variant"]["hollow"]["enabled"]:
                    if len(obj_data["variant"]["hollow"]["inner_dimension"]) != 3 or any(value <= 0 for value in obj_data["variant"]["hollow"]["inner_dimension"]):
                        raise ValueError(f"{obj_name}: 'inner_dimension' must be a list of three elements and all values must be positive")

            else:
                raise ValueError(f"{obj_name}: Unknown object type '{obj_type}'")

        return True  # Validation successful
    
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return f"Validation Error: {e}"
    
def main():
    print(validate_vr_objects(shape))

main()