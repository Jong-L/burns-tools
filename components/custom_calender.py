
from PySide6.QtWidgets import QApplication,QCalendarWidget


class CustomCalendarWidget(QCalendarWidget):
    """自定义日历控件"""
    def __init__(self):
        super().__init__()
        #self.navigationBarVisible=False


if __name__ == '__main__':
    app=QApplication()
    cal=CustomCalendarWidget()
    cal.show()
    app.exec()