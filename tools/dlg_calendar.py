import json

from PySide6.QtWidgets import QDialog,QApplication, QDialogButtonBox,QMessageBox
from PySide6.QtCore import Qt,QDate


from tools.dlg_calendar_design import Ui_Dialog



class CalendarDialog(QDialog,Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        ok_btn = self.buttonBox.button(QDialogButtonBox.Ok)
        cancel_btn = self.buttonBox.button(QDialogButtonBox.Cancel)
        ok_btn.setText("确定")
        cancel_btn.setText("取消")
        cancel_btn.setStyleSheet("""
            QPushButton{
            background-color: rgb(195, 195, 195);
            }
            QPushButton:hover{
            background-color: rgb(159, 159, 159);
            }
        """)
        #设置下拉框的选项
        try:
            with open("data/date_trans_dict.json","r",encoding="utf-8") as f:
                self.date_trans_dict = json.load(f)
        except Exception as e:
            QMessageBox.warning(self,"警告",f"日期转换文件读取失败:",{e})
        # 使用QDate替代datetime
        start_date = QDate.fromString(self.date_trans_dict["start_date"], "yyyy-MM-dd")
        end_date = QDate.fromString(self.date_trans_dict["end_date"], "yyyy-MM-dd")
        # QDate可以直接获取年份
        for year in range(start_date.year(), end_date.year() + 1):
            self.comboBox.addItem(str(year), year)
        #下拉框选择信号
        self.comboBox.currentIndexChanged.connect(self.update_calendar_date)#emit Signal(int)
        self.comboBox_2.currentIndexChanged.connect(self.update_calendar_date)
        #按钮点击信号
        self.pushButtonPreYear.clicked.connect(self.calendarWidget.showPreviousYear)
        self.pushButtonPreMonth.clicked.connect(self.calendarWidget.showPreviousMonth)
        self.pushButtonNextMonth.clicked.connect(self.calendarWidget.showNextMonth)
        self.pushButtonNextYear.clicked.connect(self.calendarWidget.showNextYear)
        #日历页面改变时更新下拉框选择
        self.calendarWidget.currentPageChanged.connect(self.update_combo_boxes)#emit Signal(int,int)
        #初始化为当前日期
        current_date=QDate.currentDate()
        self.calendarWidget.setSelectedDate(current_date)
        self.update_combo_boxes(current_date.year(),current_date.month())

    def update_calendar_date(self):
        """ 根据下拉框选择更新日历日期 """
        selected_year:int = self.comboBox.currentData()
        selected_month:int = self.comboBox_2.currentIndex() + 1
        if selected_year and selected_month:
            self.calendarWidget.setCurrentPage(selected_year,selected_month)
    def update_combo_boxes(self,year,month):
        """ 日历页面改变时更新下拉框选择 """
        index=self.comboBox.findData(year)
        if index>=0:
            self.comboBox.blockSignals(True)
            self.comboBox.setCurrentIndex(index)
            self.comboBox.blockSignals(False)

            self.comboBox_2.blockSignals(True)
            self.comboBox_2.setCurrentIndex(month-1)
            self.comboBox_2.blockSignals(False)

if __name__ == '__main__':
    app = QApplication()
    dlg = CalendarDialog()
    dlg.show()
    app.exec()