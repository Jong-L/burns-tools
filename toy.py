#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检验 PySide6 是否安装成功的测试脚本
"""

import sys

def test_pyside6_import():
    """测试 PySide6 模块导入"""
    try:
        from PySide6 import QtCore, QtWidgets
        print("✓ PySide6 导入成功")
        print(f"  - QtCore 版本: {QtCore.__version__}")
        print(f"  - QtWidgets 模块可用")
        return True
    except ImportError as e:
        print("✗ PySide6 导入失败")
        print(f"  错误信息: {e}")
        return False

def test_basic_window():
    """测试创建基础窗口"""
    try:
        from PySide6 import QtWidgets, QtCore
        
        # 创建应用程序实例
        app = QtWidgets.QApplication(sys.argv)
        
        # 创建主窗口
        window = QtWidgets.QMainWindow()
        window.setWindowTitle("PySide6 测试窗口")
        window.setGeometry(100, 100, 400, 300)
        
        # 添加标签显示成功信息
        label = QtWidgets.QLabel("PySide6 安装成功！✓")
        label.setAlignment(QtCore.Qt.AlignCenter)
        window.setCentralWidget(label)
        
        print("✓ 基础窗口创建成功")
        print("  提示: 窗口已创建，但为了测试脚本不阻塞，这里不显示窗口")
        
        return True
    except Exception as e:
        print("✗ 窗口创建失败")
        print(f"  错误信息: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("PySide6 安装测试")
    print("=" * 50)
    print()
    
    # 测试 1: 导入模块
    print("[测试 1] 导入 PySide6 模块...")
    import_success = test_pyside6_import()
    print()
    
    if import_success:
        # 测试 2: 创建窗口
        print("[测试 2] 创建基础窗口...")
        window_success = test_basic_window()
        print()
        
        if window_success:
            print("=" * 50)
            print("所有测试通过！PySide6 安装成功！")
            print("=" * 50)
            return 0
    
    print("=" * 50)
    print("测试失败！请检查 PySide6 安装：")
    print("  可以使用命令: pip install PySide6")
    print("=" * 50)
    return 1

if __name__ == "__main__":
    sys.exit(main())