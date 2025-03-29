import os
import sys

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 添加 lib 文件夹到 Python 路径
lib_dir = os.path.join(current_dir, 'lib')
sys.path.insert(0, lib_dir)

# 导入 lib/main.py 中的函数
from main import test  # 替换 your_function_name 为实际的函数名

# 调用函数
test()