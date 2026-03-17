from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class ToolCard(QFrame):
    clicked = Signal(str)

    def __init__(self, tool_id: str, tool_name: str, tool_description: str):
        super().__init__()
        self.tool_id = tool_id
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.setup_ui()

    def setup_ui(self) -> None:
        """工具卡片的 UI 设置。"""
        layout_text = QVBoxLayout(self)
        layout_text.setContentsMargins(20, 20, 20, 20)
        layout_text.setSpacing(8)

        name_label = QLabel(self.tool_name)
        name_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #35543d;")
        layout_text.addWidget(name_label)

        desc_label = QLabel(self.tool_description)
        desc_label.setFont(QFont("Microsoft YaHei", 10))
        desc_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c7f70;")
        layout_text.addWidget(desc_label)

        self.setStyleSheet(
            """
            QFrame {
                background-color: rgba(252, 253, 249, 0.96);
                border: 1px solid #d5e4d1;
                border-radius: 18px;
            }
            QFrame:hover {
                border: 1px solid #70aa7a;
                background-color: #f7fbf5;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            QLabel:hover {
                background-color: transparent;
                border: none;
            }
            """
        )

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMinimumSize(300, 150)
        self.setMaximumSize(400, 200)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool_id)
        super().mousePressEvent(event)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    main_window = ToolCard("thought_journal", "工具名称", "工具描述")
    main_window.show()
    sys.exit(app.exec())
