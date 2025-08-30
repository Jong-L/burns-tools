import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QComboBox, QLabel)
from PySide6.QtCore import QDate, Qt

class CustomCalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- 自定义导航栏 ---
        nav_layout = QHBoxLayout()

        # 上一月按钮
        self.prev_month_btn = QPushButton("◀")
        self.prev_month_btn.clicked.connect(self.show_previous_month)

        # 年份选择下拉框
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        # 假设显示当前年份前后20年
        for year in range(current_year - 20, current_year + 21):
            self.year_combo.addItem(str(year), year)
        self.year_combo.currentIndexChanged.connect(self.update_calendar_date)

        # 月份选择下拉框 (1-12)
        self.month_combo = QComboBox()
        months = ["一月", "二月", "三月", "四月", "五月", "六月",
                  "七月", "八月", "九月", "十月", "十一月", "十二月"]
        for i, month in enumerate(months, start=1):
            self.month_combo.addItem(month, i)
        self.month_combo.currentIndexChanged.connect(self.update_calendar_date)

        # 下一月按钮
        self.next_month_btn = QPushButton("▶")
        self.next_month_btn.clicked.connect(self.show_next_month)

        # 添加到导航布局
        nav_layout.addWidget(self.prev_month_btn)
        nav_layout.addWidget(self.year_combo)
        nav_layout.addWidget(self.month_combo)
        nav_layout.addWidget(self.next_month_btn)
        nav_layout.addStretch()  # 可选，使导航栏左对齐

        # --- QCalendarWidget ---
        # 创建日历控件
        from PySide6.QtWidgets import QCalendarWidget
        self.calendar = QCalendarWidget()

        # 关键：使用样式表隐藏默认的导航栏
        # 注意：这依赖于内部对象名称，可能在不同 Qt 版本或主题下需要调整
        self.calendar.setStyleSheet("""
            QCalendarWidget QToolButton {
                /* 隐藏 "上一月" 和 "下一月" 按钮 */
                /* 也可以尝试设置 min-width: 0; min-height: 0; padding: 0; margin: 0; */
                /* 或者更彻底地，隐藏包含它们的 QToolButton */
                /* 有时需要隐藏整个导航栏 */
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                /* 隐藏整个导航栏 (Qt 5.15+ / 6.x 常用) */
                background-color: transparent;
                border: none;
                min-height: 0;
                max-height: 0;
            }
            /* 如果上面的不行，尝试更具体的选择器 */
            QCalendarWidget QToolButton:up-arrow, QCalendarWidget QToolButton:down-arrow {
                /* 隐藏左右箭头 */
                image: none;
            }
            /* 或者直接隐藏所有 QToolButton (如果导航栏只有它们) */
            /* QCalendarWidget QToolButton { */
            /*     min-width: 0; */
            /*     min-height: 0; */
            /*     width: 0; */
            /*     height: 0; */
            /*     padding: 0; */
            /*     margin: 0; */
            /* } */
        """)

        # 连接日历的 currentPageChanged 信号，用于更新自定义导航栏的显示
        self.calendar.currentPageChanged.connect(self.on_calendar_page_changed)

        # --- 将布局组合起来 ---
        layout.addLayout(nav_layout)
        layout.addWidget(self.calendar)
        self.setLayout(layout)

        # 初始化：设置当前日期，并同步自定义导航栏
        current_date = QDate.currentDate()
        self.calendar.setSelectedDate(current_date)
        self.update_combo_boxes(current_date.year(), current_date.month())

        self.setWindowTitle("自定义日历导航栏")
        self.setGeometry(300, 300, 400, 300)

    def show_previous_month(self):
        """显示上一个月"""
        self.calendar.showPreviousMonth()

    def show_next_month(self):
        """显示下一个月"""
        self.calendar.showNextMonth()

    def update_calendar_date(self):
        """根据下拉框选择更新日历显示的月份"""
        selected_year = self.year_combo.currentData()
        selected_month = self.month_combo.currentData()
        if selected_year is not None and selected_month is not None:
            new_date = QDate(selected_year, selected_month, 1)
            if new_date.isValid():
                # 注意：setSelectedDate 会改变选中日期，showSelectedDate 只改变显示
                # 通常我们想改变显示的月份，但不一定改变选中日期
                # 这里使用 showSelectedDate 或者先记住选中日期再设置
                # 为了简单，这里直接设置显示
                self.calendar.setCurrentPage(selected_year, selected_month)
                # 或者使用：self.calendar.setSelectedDate(new_date)
                # 但 setSelectedDate 会把选中日期设为该月1号

    def on_calendar_page_changed(self, year, month):
        """当日历的页面（年月）改变时，更新下拉框"""
        self.update_combo_boxes(year, month)

    def update_combo_boxes(self, year, month):
        """更新年份和月份下拉框的选中项"""
        index = self.year_combo.findData(year)
        if index >= 0:
            self.year_combo.blockSignals(True)  # 防止触发 update_calendar_date
            self.year_combo.setCurrentIndex(index)
            self.year_combo.blockSignals(False)

        index = self.month_combo.findData(month)
        if index >= 0:
            self.month_combo.blockSignals(True)
            self.month_combo.setCurrentIndex(index)
            self.month_combo.blockSignals(False)

def main():
    app = QApplication(sys.argv)
    window = CustomCalendarWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()