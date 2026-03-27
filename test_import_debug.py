#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试 PyQt6 导入问题"""

import sys
import os

# 添加 PyQt6 的 bin 目录到 PATH 环境变量
pyqt6_path = r"C:\Users\86180\AppData\Roaming\Python\Python313\site-packages\PyQt6\Qt6\bin"
if pyqt6_path not in os.environ.get('PATH', ''):
    os.environ['PATH'] = pyqt6_path + ';' + os.environ.get('PATH', '')

print(f"Python 版本: {sys.version}")
print(f"Python 位置: {sys.executable}")
print(f"PATH 环境变量中的 PyQt6 bin: {pyqt6_path in os.environ.get('PATH', '')}")
print()

# 测试 PyQt6
try:
    print("尝试导入 PyQt6.QtCore...")
    from PyQt6 import QtCore
    print(f"✓ PyQt6 导入成功!")
    print(f"  QtCore 版本: {QtCore.QT_VERSION_STR}")
    print(f"  QtCore 文件位置: {QtCore.__file__}")
except ImportError as e:
    print(f"✗ PyQt6 导入失败: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ 其他错误: {e}")
    import traceback
    traceback.print_exc()