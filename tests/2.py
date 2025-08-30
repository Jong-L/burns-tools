from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
import sys

app = QApplication(sys.argv)

# 创建一个 QLabel
label = QLabel()

# 假设原始文本是 "Hello, this is a sample text with some words in blue."
# 我们想把 "some words" 变成蓝色

original_text = "Hello, this is a sample text with some words in blue."

# 使用 HTML 来标记特定范围
# 方法1: 使用 <span style="color: blue;">
styled_text = (
    original_text[:31] +  # "Hello, this is a sample text with "
    '<span style="color: blue;">some words</span>' +
    original_text[40:]    # " in blue."
)

# 方法2: 使用 <font color="blue"> (较老的方式，但依然有效)
# styled_text = (
#     original_text[:31] +
#     '<font color="blue">some words</font>' +
#     original_text[40:]
# )

label.setText(styled_text)
# QLabel 默认会自动检测 HTML，但为了确保，可以设置：
label.setTextFormat(Qt.TextFormat.RichText)  # 或者 Qt.RichText

# 显示标签
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(label)
window.setLayout(layout)
window.show()

sys.exit(app.exec())