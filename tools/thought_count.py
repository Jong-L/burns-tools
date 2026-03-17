
import os
import sys
import json
from datetime import datetime,timedelta


from PySide6.QtWidgets import (QWidget,QMessageBox, QDialog)
from PySide6.QtCore import (QDate)
import matplotlib.dates as mdates
from matplotlib import rcParams
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np

from tools.thought_count_design import Ui_Form
from components.dlg_info_design import Ui_Dialog
from tools.dlg_calendar import CalendarDialog
from tools.thought_count_plot_ui import Ui_Form as ThoughtCounterPlotUi

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False


class ThoughtCounterPlotWindow(QWidget):
    def __init__(self,count_data={},today=""):
        super().__init__()
        self.count_data=count_data
        self.today=datetime.strptime(today,"%Y-%m-%d")
        self.ui=ThoughtCounterPlotUi()
        self.ui.setupUi(self)
        self.ui.comboBox.currentIndexChanged.connect(self.update_plot)

        #提前得到时间列表
        self.time_list_7=[self.today-timedelta(days=i) for i in range(7)];self.time_list_7.reverse()
        self.time_list_30=[self.today-timedelta(days=i) for i in range(30)];self.time_list_30.reverse()
        self.time_list_90=[self.today-timedelta(days=i) for i in range(90)];self.time_list_90.reverse()
        self.time_list_180=[self.today-timedelta(days=i) for i in range(180)];self.time_list_180.reverse()
        self.time_list_365=[self.today-timedelta(days=i) for i in range(365)];self.time_list_365.reverse()
        
        self.update_plot(0)
    def update_plot(self, index):
        """更新图表显示
        Args:
            index: 时间范围索引（0:近7天，1:近30天，2:近90天，3:近180天，4:近365天）
        """
        # 验证输入参数
        if not (0 <= index <= 4):
            raise ValueError("无效的时间范围索引")
        
        # 获取对应时间范围的数据
        time_list = self._get_time_list(index)
        if not time_list:
            return
        
        count_list = self._get_count_list(time_list)
        
        # 更新图表
        self._clear_plot()
        self._configure_plot_style()
        self._plot_main_line(time_list, count_list)
        self._add_fill_area(time_list, count_list)
        self._set_plot_title(index)
        self._set_axis_labels()
        self._configure_y_axis(count_list)
        self._configure_x_axis(time_list, index)
        self._beautify_axes()
        self._add_data_annotations(time_list, count_list)
        self._finalize_plot()

    def _get_time_list(self, index):
        """获取指定时间范围的时间列表"""
        time_lists = {
            0: self.time_list_7,
            1: self.time_list_30,
            2: self.time_list_90,
            3: self.time_list_180,
            4: self.time_list_365
        }
        return time_lists.get(index)

    def _get_count_list(self, time_list):
        """获取计数列表"""
        if not self.count_data:
            return [0] * len(time_list)
        return [self.count_data.get(date.strftime("%Y-%m-%d"), 0) for date in time_list]

    def _clear_plot(self):
        """清除之前的图表"""
        self.ui.mplWidget.axes.cla()

    def _configure_plot_style(self):
        """配置图表基本样式"""
        self.ui.mplWidget.figure.patch.set_facecolor('#f8f9fa')
        self.ui.mplWidget.axes.set_facecolor('#ffffff')

    def _plot_main_line(self, time_list, count_list):
        """绘制主线条"""
        self.ui.mplWidget.axes.plot(time_list, count_list,
                                linewidth=3,
                                color='#2E86AB',
                                alpha=0.8,
                                marker='o',
                                markersize=6,
                                markerfacecolor='#A23B72',
                                markeredgecolor='#ffffff',
                                markeredgewidth=2,
                                zorder=3)

    def _add_fill_area(self, time_list, count_list):
        """添加填充区域"""
        self.ui.mplWidget.axes.fill_between(time_list, count_list,
                                        alpha=0.3,
                                        color='#2E86AB',
                                        zorder=1)

    def _set_plot_title(self, index):
        """设置图表标题"""
        titles = {
            0: "近7天",
            1: "近30天",
            2: "近90天",
            3: "近180天",
            4: "近365天"
        }
        self.ui.mplWidget.axes.set_title(f"计数统计 - {titles.get(index)}",
                                        fontsize=16,
                                        fontweight='bold',
                                        color='#2c3e50',
                                        pad=20)

    def _set_axis_labels(self):
        """设置坐标轴标签"""
        self.ui.mplWidget.axes.set_xlabel("日期",
                                        fontsize=12,
                                        fontweight='bold',
                                        color='#34495e')
        self.ui.mplWidget.axes.set_ylabel("消极思维出现次数",
                                        fontsize=12,
                                        fontweight='bold',
                                        color='#34495e')

    def _configure_y_axis(self, count_list):
        """配置Y轴"""
        max_count = max(count_list) if count_list else 0
        self.ui.mplWidget.axes.set_ylim(0, max_count + 1)
        self.ui.mplWidget.axes.yaxis.set_major_locator(MultipleLocator(1))

    def _configure_x_axis(self, time_list, index):
        """配置X轴"""
        intervals = {
            0: 1,
            1: 4,
            2: 10,
            3: 18,
            4: 36
        }
        self.ui.mplWidget.axes.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        self.ui.mplWidget.axes.xaxis.set_major_locator(mdates.DayLocator(interval=intervals.get(index)))

    def _beautify_axes(self):
        """美化坐标轴"""
        self.ui.mplWidget.axes.tick_params(axis='x',
                                        rotation=20,
                                        colors='#7f8c8d',
                                        labelsize=10)
        self.ui.mplWidget.axes.tick_params(axis='y',
                                        colors='#7f8c8d',
                                        labelsize=10)
        
        self.ui.mplWidget.axes.grid(True,
                                alpha=0.3,
                                linestyle='--',
                                color='#bdc3c7',
                                zorder=0)
        
        for spine in self.ui.mplWidget.axes.spines.values():
            spine.set_edgecolor('#bdc3c7')
            spine.set_linewidth(1.5)

    def _add_data_annotations(self, time_list, count_list):
        """添加数据点标注"""
        for date, count in zip(time_list, count_list):
            if count > 0:
                self.ui.mplWidget.axes.annotate(str(count),
                                            (date, count),
                                            textcoords="offset points",
                                            xytext=(0, 10),
                                            ha='center',
                                            fontsize=9,
                                            color='#e74c3c',
                                            fontweight='bold',
                                            bbox=dict(boxstyle="round,pad=0.3",
                                                    facecolor='#ffffff',
                                                    edgecolor='#e74c3c',
                                                    alpha=0.8))

    def _finalize_plot(self):
        """完成图表绘制"""
        self.ui.mplWidget.figure.autofmt_xdate()
        self.ui.mplWidget.figure.tight_layout()
        self.ui.mplWidget.canvas.draw()



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
        DATA_DIR = "data"
        COUNT_FILE = os.path.join(DATA_DIR, "消极思维计数.json")
        
        try:
            # 确保数据目录存在
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # 初始化或加载计数数据
            if not os.path.exists(COUNT_FILE) or os.path.getsize(COUNT_FILE) == 0:
                self.count_data = {}
                self._save_count_data(COUNT_FILE)
            else:
                with open(COUNT_FILE, "r", encoding='utf-8') as f:
                    self.count_data = json.load(f)
            
            # 加载今日数据
            self.current_count = self.count_data.get(self.today, 0)
            self.label_2.setText(str(self.current_count))
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "错误", f"JSON数据格式错误: {e}")
        except PermissionError as e:
            QMessageBox.warning(self, "错误", f"文件权限错误: {e}")
        except OSError as e:
            QMessageBox.warning(self, "错误", f"文件操作错误: {e}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据失败: {e}")

    def _save_count_data(self, file_path):
        """首次运行时的辅助方法：保存计数数据到文件"""
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(self.count_data, f, ensure_ascii=False, indent=2)


    def increase_count(self):
        self.current_count+=1
        self.label_2.setText(str(self.current_count))

    def decrease_count(self):
        if self.current_count>0:
            self.current_count-=1
        self.label_2.setText(str(self.current_count))
    
    def save_count(self):
        """ 保存数据"""
        self.count_data[self.date]=self.current_count
        try:
            #写入文件
            with open("data/消极思维计数.json", "w", encoding="utf-8") as f:
                json.dump(self.count_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {e}")
        else:
            dlg = QDialog(self)  # 创建QDialog实例
            ui = Ui_Dialog()     # 创建UI实例
            ui.setupUi(dlg)      # 设置UI
            ui.label_text.setText("保存成功")
            dlg.exec()           # 显示对话框

    def show_statistics(self):
        """ 打开数据统计窗口 """
        self.statistics_window=ThoughtCounterPlotWindow(count_data=self.count_data,today=self.today)
        self.statistics_window.show()
        

    def closeEvent(self, event):
        # 通知主窗口清理
        if self.main_window and hasattr(self.main_window, 'close_tool'):
            self.main_window.close_tool("消极思维计数器")
