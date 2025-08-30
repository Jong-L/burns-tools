from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # 添加自定义标题栏内容
        title_label = QLabel("自定义标题")
        layout.addWidget(title_label)
        
        # 添加关闭按钮
        close_button = QPushButton("X")
        close_button.clicked.connect(parent.close)
        layout.addWidget(close_button)

app = QApplication()
window = QMainWindow()

# 设置无边框窗口
window.setWindowFlags(Qt.WindowType.FramelessWindowHint)

# 创建自定义标题栏
title_bar = CustomTitleBar(window)
window.setMenuWidget(title_bar)

window.show()
app.exec()
