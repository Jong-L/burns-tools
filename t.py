# main.py
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QCheckBox
from PySide6.QtCore import Qt
import colors

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        #是否追加描述
        self.descCheck=QCheckBox("追加描述")
        self.descCheck.setChecked(True)
        layout.addWidget(self.descCheck)

        btn = QPushButton("Click Me")
        btn.setStyleSheet(f"""
            background: {colors.COLORS['pacific_cyan']};
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
        """)
        layout.addWidget(btn)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()