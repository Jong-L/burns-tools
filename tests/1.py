import sys
from datetime import datetime, date
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QCalendarWidget, QLabel)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QFont


class ChineseCalendarData:
    """农历和节日数据类"""
    
    # 简化的农历数据（实际应用中应该使用更完整的数据）
    LUNAR_DATA = {
        "2024-01-01": "元旦",
        "2024-02-10": "春节",
        "2024-02-11": "初二",
        "2024-02-12": "初三",
        "2024-02-13": "初四",
        "2024-02-14": "初五",
        "2024-02-15": "初六",
        "2024-02-16": "初七",
        "2024-02-17": "初八",
        "2024-02-18": "初九",
        "2024-02-19": "初十",
        "2024-02-20": "十一",
        "2024-02-21": "十二",
        "2024-02-22": "十三",
        "2024-02-23": "十四",
        "2024-02-24": "十五",
        "2024-03-08": "妇女节",
        "2024-04-04": "清明节",
        "2024-05-01": "劳动节",
        "2024-06-01": "儿童节",
        "2024-09-10": "教师节",
        "2024-10-01": "国庆节",
    }
    
    @classmethod
    def get_lunar_or_festival(cls, date_str):
        """获取指定日期的农历或节日名称"""
        if date_str in cls.LUNAR_DATA:
            return cls.LUNAR_DATA[date_str]
        else:
            # 简化的农历计算（实际应该使用完整的农历算法）
            return cls._calculate_simple_lunar(date_str)
    
    @classmethod
    def _calculate_simple_lunar(cls, date_str):
        """简化农历计算"""
        try:
            # 这里只是一个示例，实际应该使用完整的农历算法
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day = date_obj.day
            month = date_obj.month
            
            # 简单的农历表示
            lunar_months = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
            lunar_days = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
                         "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                         "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
            
            if day <= len(lunar_days):
                return f"{lunar_months[month-1]}月{lunar_days[day-1]}"
            else:
                return f"{lunar_months[month-1]}月{lunar_days[-1]}"
        except:
            return ""


class CustomCalendarWidget(QCalendarWidget):
    """自定义日历控件"""
    
    def __init__(self):
        super().__init__()
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self.setGridVisible(True)
        
        # 设置日历样式
        self.setStyleSheet("""
            QCalendarWidget QToolButton {
                height: 30px;
                width: 100px;
                color: white;
                background-color: #2196F3;
                border: none;
                border-radius: 4px;
            }
            QCalendarWidget QMenu {
                width: 150px;
                left: 20px;
                color: white;
                background-color: rgb(100, 100, 100);
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 #424242, stop: 1 #212121);
            }
            QCalendarWidget QTableView {
                alternate-background-color: rgb(200, 200, 200);
                selection-background-color: #42A5F5;
            }
        """)
        
        # 连接日期选择信号
        self.clicked.connect(self.update_date_format)
        self.currentPageChanged.connect(self.update_calendar_format)
        
        # 初始化格式
        self.update_calendar_format()
    
    def update_date_format(self, date):
        """更新日期格式"""
        pass  # 这里可以添加选中日期的特殊处理
    
    def update_calendar_format(self):
        """更新整个日历的格式"""
        # 清除之前的格式
        self.setDateTextFormat(QDate(), QTextCharFormat())
        
        # 获取当前显示的月份
        current_year = self.yearShown()
        current_month = self.monthShown()
        
        # 为每个月的日期设置格式
        for day in range(1, 32):
            try:
                current_date = QDate(current_year, current_month, day)
                if current_date.isValid():
                    self.set_date_format(current_date)
            except:
                break
    
    def set_date_format(self, qdate):
        """设置单个日期的格式"""
        date_str = qdate.toString("yyyy-MM-dd")
        lunar_or_festival = ChineseCalendarData.get_lunar_or_festival(date_str)
        
        # 创建格式
        format = QTextCharFormat()
        format.setFontPointSize(10)
        
        # 如果是节日，设置特殊颜色
        if lunar_or_festival in ["元旦", "春节", "清明节", "劳动节", "端午节", "中秋节", "国庆节"]:
            format.setForeground(QColor("#FF5722"))
            format.setFontWeight(QFont.Bold)
        elif "节" in lunar_or_festival:
            format.setForeground(QColor("#2196F3"))
        
        # 设置日期文本（这里会被paintCell方法覆盖）
        self.setDateTextFormat(qdate, format)
    
    def paintCell(self, painter, rect, date):
        """自定义绘制单元格"""
        super().paintCell(painter, rect, date)
        
        # 获取日期字符串
        date_str = date.toString("yyyy-MM-dd")
        gregorian_day = date.day()
        lunar_or_festival = ChineseCalendarData.get_lunar_or_festival(date_str)
        
        # 绘制公历日期（较大字体）
        painter.save()
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        # 绘制公历数字
        day_text = str(gregorian_day)
        day_rect = rect.adjusted(0, 2, 0, -rect.height()//2)
        painter.drawText(day_rect, Qt.AlignCenter, day_text)
        
        # 绘制农历或节日（较小字体）
        painter.setPen(Qt.gray)
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        
        lunar_rect = rect.adjusted(0, rect.height()//2, 0, -2)
        painter.drawText(lunar_rect, Qt.AlignCenter, lunar_or_festival)
        
        painter.restore()


class DateSelectionWindow(QMainWindow):
    """日期选择窗口"""
    
    # 定义信号
    date_selected = Signal(str)  # 发送选中的日期字符串，格式为"YYYY-MM-DD"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日期选择器")
        self.setGeometry(300, 300, 400, 350)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建日历控件
        self.calendar = CustomCalendarWidget()
        main_layout.addWidget(self.calendar)
        
        # 创建操作按钮区
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 确认按钮
        self.confirm_button = QPushButton("确认")
        self.confirm_button.setFixedWidth(80)
        self.confirm_button.clicked.connect(self.on_confirm_clicked)
        button_layout.addWidget(self.confirm_button)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedWidth(80)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 设置选中日期为今天
        self.calendar.setSelectedDate(QDate.currentDate())
    
    def on_confirm_clicked(self):
        """确认按钮点击事件"""
        selected_date = self.calendar.selectedDate()
        date_string = selected_date.toString("yyyy-MM-dd")
        self.date_selected.emit(date_string)
        self.close()
    
    def on_cancel_clicked(self):
        """取消按钮点击事件"""
        self.close()
    
    def get_selected_date(self):
        """获取选中的日期"""
        return self.calendar.selectedDate().toString("yyyy-MM-dd")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建并显示日期选择窗口
    window = DateSelectionWindow()
    
    # 连接信号槽
    window.date_selected.connect(lambda date_str: print(f"选中的日期: {date_str}"))
    
    window.show()
    
    # 演示如何使用信号
    def on_date_selected(date_str):
        print(f"接收到选中的日期: {date_str}")
        # 这里可以进行后续处理，比如更新UI等
    
    window.date_selected.connect(on_date_selected)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()