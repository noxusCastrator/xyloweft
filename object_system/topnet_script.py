import os
import hou
import json

class GeoGenerator:
    def __init__(self, work_item):
        """
        初始化时从 work_item 中读取 JSON 文件的相关属性，
        加载 JSON 数据，并获取 /obj 作为父级节点
        """

        self.work_item = work_item
        self.data = self.load_json()
        self.obj_context = hou.node("/obj")

    def load_json(self):
        """
        从 work_item 中获取目录、文件名和扩展名，
        拼接成完整路径后加载 JSON 数据
        """

        # 从工作项获取相关属性
        dirpath   = str(self.work_item.attribValue("directory"))
        filename  = str(self.work_item.attribValue("filename"))
        extension = str(self.work_item.attribValue("extension"))

        json_path = os.path.join(dirpath, filename + extension)
        # hou.ui.displayMessage("Loading JSON from:\n" + json_path)
        with open(json_path, "r") as f:
            data = json.load(f)
        return data

    def create_geo_node(self, geo_name, position, rotate, scale):
        """
        在 /obj 下创建或获取与 geo_name 同名的 geo 节点，
        并设置其平移位置
        """

        geo_node = self.obj_context.node(geo_name)
        if not geo_node:
            geo_node = self.obj_context.createNode("geo", geo_name)
            # 删除自动生成的默认 file1 节点
            default_file = geo_node.node("file1")
            if default_file:
                default_file.destroy()

        geo_node.parmTuple("t").set(tuple(position))
        geo_node.parmTuple("r").set(tuple(rotate))
        geo_node.parmTuple("s").set(tuple(scale))
        return geo_node

    def create_sphere(self, geo_node, traits, variants):
        """
        在指定的 geo_node 内创建或复用一个 sphere 节点，
        并根据 traits 设置半径（radius）参数。
        traits 应包含 "radius": [radx, rady, radz]
        """

        sop_name = "sphere_sop"
        existing_sop = geo_node.node(sop_name)

        if existing_sop and existing_sop.type().name() != "sphere":
            existing_sop.destroy()
            existing_sop = None

        if existing_sop is None:
            sphere_sop = geo_node.createNode("sphere", sop_name)
            sphere_sop.setDisplayFlag(True)
            sphere_sop.setRenderFlag(True)
        else:
            sphere_sop = existing_sop

        sphere_sop.parm("type").set(1)

        whether_subdivided = variants.get("subdivided")

        if whether_subdivided.get("enabled") == 1:
            # 创建一个 subdivide 节点
            subdivide_sop = geo_node.createNode("subdivide", "subdivide_sop")

            # 让 subdivide_sop 以 sphere_sop 为输入
            subdivide_sop.setFirstInput(sphere_sop)

            # 将 subdivide_sop 作为最终显示节点
            subdivide_sop.setDisplayFlag(True)
            subdivide_sop.setRenderFlag(True)
            # 同时把 sphere_sop 的显示渲染标志关掉
            sphere_sop.setDisplayFlag(False)
            sphere_sop.setRenderFlag(False)

            # 美观排列节点
            subdivide_sop.moveToGoodPosition()

        radius = traits.get("radius")

        sphere_sop.parmTuple("rad").set(tuple(radius))

        return sphere_sop

    def create_cuboid(self, geo_node, traits):
        """
        在指定的 geo_node 内创建或复用一个 box 节点，
        并根据 traits 设置尺寸参数。
        traits 应包含 "width", "height", "depth"
        """

        print("开始生成长方体")
        sop_name = "cuboid_sop"
        existing_sop = geo_node.node(sop_name)

        if existing_sop and existing_sop.type().name() != "box":
            existing_sop.destroy()
            existing_sop = None

        if existing_sop is None:
            box_sop = geo_node.createNode("box", sop_name)
            box_sop.setDisplayFlag(True)
            box_sop.setRenderFlag(True)
        else:
            box_sop = existing_sop

        dimension = traits.get("dimension")
        box_sop.parmTuple("size").set(tuple(dimension))

        return box_sop

    def create_cylinder(self, geo_node, traits):
        """
        在指定的 geo_node 内创建或复用一个 tube 节点，
        并根据 traits 设置参数。
        traits 应包含 "radius": [rad1, rad2] 和 "height"
        """

        sop_name = "cylinder_sop"
        existing_sop = geo_node.node(sop_name)

        if existing_sop and existing_sop.type().name() != "tube":
            existing_sop.destroy()
            existing_sop = None

        if existing_sop is None:
            tube_sop = geo_node.createNode("tube", sop_name)
            tube_sop.setDisplayFlag(True)
            tube_sop.setRenderFlag(True)
        else:
            tube_sop = existing_sop

        radius = traits.get("radius", [1,1])
        height = traits.get("height", 1)
        tube_sop.parm("rad1").set(radius[0])
        tube_sop.parm("rad2").set(radius[1])
        tube_sop.parm("height").set(height)
        return tube_sop

    def generate(self):
        """
        遍历 JSON 数据，为每个物体生成对应的 geo 节点及内部 SOP 节点
        JSON 文件格式示例：
        {
          "Sphere1": {
              "position": [0, 0, 0],
              "traits": { "type": "Sphere", "radius": [5, 5, 5] },
              "variant": { ... }
          },
          "Cuboid1": {
              "position": [10, 0, 0],
              "traits": { "type": "Cuboid", "width": 6, "height": 4, "depth": 3 },
              "variant": { ... }
          },
          "Cylinder1": {
              "position": [0, 10, 0],
              "traits": { "type": "Cylinder", "radius": [3, 3], "height": 8 },
              "variant": { ... }
          }
        }
        """

        for geo_name, geo_data in self.data.items():
            # 获取物体平移位置
            position = geo_data.get("position")
            rotate = geo_data.get("rotate")
            scale = geo_data.get("scale")
            # 获取属性数据
            traits = geo_data.get("traits")
            # 获取变体数据
            variants = geo_data.get("variant")
            # 获取物体类型（转为小写便于比较）
            geo_type = traits.get("type").lower()
            # 创建或获取 /obj 下与 geo_name 同名的 geo 节点
            geo_node = self.create_geo_node(geo_name, position, rotate, scale)

            # 根据类型调用相应的创建方法
            if geo_type == "sphere":
                self.create_sphere(geo_node, traits, variants)
            elif geo_type == "cuboid":
                self.create_cuboid(geo_node, traits)
            elif geo_type == "cylinder":
                self.create_cylinder(geo_node, traits)
            else:
                hou.ui.displayMessage("Unknown geometry type for %s: %s" % (geo_name, geo_type))

# ---------------------------
# 执行部分：
# 在 TOP 网络中运行该脚本时，work_item 全局变量应已由上游 File Pattern 节点传入
generator = GeoGenerator(work_item)
generator.generate()