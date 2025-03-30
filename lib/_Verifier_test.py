# Verifier_test
import json
import os
with open('shape.json', 'r', encoding='utf-8') as file_shape:
    # 加载 JSON 数据
    shape = json.load(file_shape)

ALLOWED_CLASS = ["Sphere", "Pyramid", "Cuboid"]  # Updated to include "Pyramid"





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
                    if inner_radius_top <= 0 :
                        raise ValueError(f"{obj_name}: 'inner_radius_top' must be positive")
                    if inner_radius_bottom <= 0:
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


def main():
    print(validate_vr_objects(shape))

main()