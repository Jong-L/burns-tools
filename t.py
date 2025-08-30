import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


# import os
# import sys
# from pathlib import Path

# if getattr(sys, 'frozen', False):
#     bundle_dir = Path(sys._MEIPASS)
# else:
#     bundle_dir = Path(__file__).parent

# plugin_path = bundle_dir / "PySide6/plugins/platforms/qwindows.dll"
# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("PySide6 示例界面")
        self.setGeometry(100, 100, 400, 200)  # x, y, width, height
        
        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 添加标题标签
        title_label = QLabel("欢迎使用 PySide6")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 添加水平布局用于输入框和按钮
        input_layout = QHBoxLayout()
        
        # 创建输入框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请输入您的名字")
        input_layout.addWidget(self.input_field)
        
        # 创建按钮
        self.greet_button = QPushButton("问候")
        self.greet_button.clicked.connect(self.show_greeting)
        input_layout.addWidget(self.greet_button)
        
        main_layout.addLayout(input_layout)
        
        # 添加退出按钮
        self.exit_button = QPushButton("退出")
        self.exit_button.clicked.connect(self.close)
        main_layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)
    
    def show_greeting(self):
        """显示问候信息"""
        name = self.input_field.text().strip()
        if name:
            QMessageBox.information(self, "问候", f"你好, {name}!")
        else:
            QMessageBox.warning(self, "警告", "请输入您的名字!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
