"""
伯恩斯情绪工具集 - 主程序入口
Burns Emotion Toolkit - Main Entry Point
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette,QColor

from main_window import MainWindow


if __name__=="__main__":
    app=QApplication()
    #app.setStyle("Fusion")
    app.setApplicationName("伯恩斯情绪工具集")
    app.setApplicationVersion("1.0.0")
    
    main_window=MainWindow()
    main_window.show()
    _=app.exec()