



from PySide6.QtWidgets import (QFrame,QVBoxLayout,QLabel, QPushButton)
from PySide6.QtGui import (QFont)
from PySide6.QtCore import Qt,Signal

class ToolCard(QFrame):
    clicked=Signal(str)#点击信号，传递工具名称
    def __init__(self, tool_name, tool_description):
        super().__init__()
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.setup_ui()

    def setup_ui(self):
        """ 工具卡片的UI设置 """

        # 创建布局
        layout_text = QVBoxLayout(self)
        layout_text.setContentsMargins(20, 20, 20, 20)
        layout_text.setSpacing(2)

        #工具名称
        name_label = QLabel(self.tool_name)
        name_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #2c3e50;")
        layout_text.addWidget(name_label)

        #工具描述
        desc_label = QLabel(self.tool_description)
        desc_label.setFont(QFont("Microsoft YaHei", 10))
        desc_label.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d;")
        layout_text.addWidget(desc_label)

        # 设置卡片样式
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
            }
            QFrame:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            QLabel:hover {
                background-color: transparent;
                border: none;
            }
        """)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMinimumSize(300, 150)
        self.setMaximumSize(400, 200)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool_name)
        super().mousePressEvent(event)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    main_window = ToolCard("工具名称", "工具描述")
    main_window.show()
    sys.exit(app.exec())