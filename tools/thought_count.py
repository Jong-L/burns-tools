
import os
import sys
import json


from PySide6.QtWidgets import (QApplication,QWidget,QMessageBox, QDialog)
from PySide6.QtCore import (QDate)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib import rcParams





from thought_count_design import Ui_Form
if __name__ == '__main__':
    # 添加项目根目录到 Python 路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.dlg_info_design import Ui_Dialog
from tools.dlg_calendar import CalendarDialog

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False

class ThoughtCounterWindow(QWidget,Ui_Form):
    def __init__(self,main_window):
        super().__init__()
        self.main_window=main_window
        self.count_data={}# 数据字典
        self.current_count=0
        self.today=self.date=QDate.currentDate().toString("yyyy-MM-dd")
        self.setupUi(self)
        self.load_data()

        self.pushButton_4.clicked.connect(self.decrease_count)
        self.pushButton_3.clicked.connect(self.increase_count)
        self.pushButton_5.clicked.connect(self.set_time)
        self.pushButton_2.clicked.connect(self.save_count)
        self.pushButton.clicked.connect(self.show_statistics)

    def set_time(self):
        dlg=CalendarDialog()
        if dlg.exec()==QDialog.Accepted:
            self.date=dlg.calendarWidget.selectedDate().toString("yyyy-MM-dd")
            if self.date!=self.today:
                self.pushButton_5.setText(self.date)
                #更新计数显示
                self.current_count=self.count_data.get(self.date,0)
                self.label_2.setText(str(self.current_count))
            else:
                self.pushButton_5.setText("今天")
                self.current_count=self.count_data.get(self.today,0)
                self.label_2.setText(str(self.current_count))


    def load_data(self):
        try:
            count_file="data/消极思维计数.json"
            if os.path.exists(count_file):
                with open(count_file, "r") as f:
                    self.count_data = json.load(f)
            else:
                count_data={}
            #加载今日数据
            self.current_count=self.count_data.get(self.today,0)
            self.label_2.setText(str(self.current_count))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据失败: {e}")

    def increase_count(self):
        self.current_count+=1
        self.label_2.setText(str(self.current_count))

    def decrease_count(self):
        if self.current_count>0:
            self.current_count-=1
        self.label_2.setText(str(self.current_count))
    
    def save_count(self):
        """ 保存数据"""
        try:
            self.count_data[self.date]=self.current_count
            #写入文件
            with open("data/消极思维计数.json", "w", encoding="utf-8") as f:
                json.dump(self.count_data, f, ensure_ascii=False, indent=2)
            dlg = QDialog(self)  # 创建QDialog实例
            ui = Ui_Dialog()     # 创建UI实例
            ui.setupUi(dlg)      # 设置UI
            ui.label_text.setText("保存成功")
            dlg.exec()           # 显示对话框
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {e}")

    def show_statistics(self):
        print("显示统计")

    def closeEvent(self, event):
        # 通知主窗口清理
        if self.main_window and hasattr(self.main_window, 'close_tool'):
            self.main_window.close_tool("消极思维计数器")

if __name__ == '__main__':
    app = QApplication([])
    window = ThoughtCounterWindow(main_window=None)
    window.show()
    app.exec()