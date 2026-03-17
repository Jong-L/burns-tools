from datetime import datetime, timedelta


from PySide6.QtWidgets import QWidget, QMessageBox, QDialog, QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import QDate
import matplotlib.dates as mdates
from matplotlib import rcParams
from matplotlib.ticker import MultipleLocator

from services.local_store import LocalStore
from tools.thought_count_design import Ui_Form
from components.dlg_info_design import Ui_Dialog
from tools.dlg_calendar import CalendarDialog
from tools.thought_count_plot_ui import Ui_Form as ThoughtCounterPlotUi

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False


class ThoughtCounterPlotWindow(QWidget):
    def __init__(self, count_data: dict[str, int] | None = None, today: str = ""):
        super().__init__()
        self.count_data = count_data or {}
        self.today = datetime.strptime(today, "%Y-%m-%d")
        self.ui = ThoughtCounterPlotUi()
        self.ui.setupUi(self)
        self.setObjectName("thoughtCounterPlotWindow")
        self._apply_styles()
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
        self.ui.mplWidget.figure.patch.set_facecolor('#f4f8f2')

    def _plot_main_line(self, time_list, count_list):
        """绘制主线条"""
        self.ui.mplWidget.axes.plot(time_list, count_list,
                                linewidth=3,
                                color='#4f9c61',
                                alpha=0.88,
                                marker='o',
                                markersize=6,
                                markerfacecolor='#dff0de',
                                markeredgecolor='#ffffff',
                                markeredgewidth=2,
                                zorder=3)

    def _add_fill_area(self, time_list, count_list):
        """添加填充区域"""
        self.ui.mplWidget.axes.fill_between(time_list, count_list,
                                        alpha=0.3,
                                        color='#7fc58c',
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
                                        color='#35543d',
                                        pad=20)

    def _set_axis_labels(self):
        """设置坐标轴标签"""
        self.ui.mplWidget.axes.set_xlabel("日期",
                                        fontsize=12,
                                        fontweight='bold',
                                        color='#48624e')
        self.ui.mplWidget.axes.set_ylabel("消极思维出现次数",
                                        fontsize=12,
                                        fontweight='bold',
                                        color='#48624e')

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
                                        colors='#768878',
                                        labelsize=10)
        self.ui.mplWidget.axes.tick_params(axis='y',
                                        colors='#768878',
                                        labelsize=10)
        
        self.ui.mplWidget.axes.grid(True,
                                alpha=0.3,
                                linestyle='--',
                                color='#c8d8c3',
                                zorder=0)
        
        for spine in self.ui.mplWidget.axes.spines.values():
            spine.set_edgecolor('#c5d6c0')
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
                                            color='#416247',
                                            fontweight='bold',
                                            bbox=dict(boxstyle="round,pad=0.3",
                                                    facecolor='#f9fcf8',
                                                    edgecolor='#8ec59a',
                                                    alpha=0.8))

    def _finalize_plot(self):
        """完成图表绘制"""
        self.ui.mplWidget.figure.autofmt_xdate()
        self.ui.mplWidget.figure.tight_layout()
        self.ui.mplWidget.canvas.draw()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget#thoughtCounterPlotWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #eef4ee,
                    stop: 0.55 #f7f6ef,
                    stop: 1 #e8f0e7
                );
                font-family: "Microsoft YaHei";
                color: #2b3f30;
            }
            QComboBox {
                min-width: 120px;
                padding: 8px 12px;
                border-radius: 12px;
                border: 1px solid #bfd2ba;
                background-color: #fbfdf9;
                color: #33503a;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            """
        )


class ThoughtCounterWindow(QWidget, Ui_Form):
    def __init__(self, main_window, storage: LocalStore):
        super().__init__()
        self.main_window = main_window
        self.storage = storage
        self.count_data: dict[str, int] = {}
        self.current_count = 0
        self.today = self.date = QDate.currentDate().toString("yyyy-MM-dd")
        self.setupUi(self)
        self.setObjectName("thoughtCounterWindow")
        self._build_green_shell()
        self._apply_styles()
        self.load_data()

        self.pushButton_4.clicked.connect(self.decrease_count)
        self.pushButton_3.clicked.connect(self.increase_count)
        self.pushButton_5.clicked.connect(self.set_time)
        self.pushButton_2.clicked.connect(self.save_count)
        self.pushButton.clicked.connect(self.show_statistics)

    def _build_green_shell(self) -> None:
        self.label.setParent(None)
        self.verticalLayout_2.insertWidget(0, self._create_header_card())

        self.frame.setObjectName("counterPanel")
        self.pushButton_5.setObjectName("dateButton")
        self.pushButton_2.setObjectName("saveButton")
        self.pushButton.setObjectName("statsButton")
        self.pushButton_3.setObjectName("plusButton")
        self.pushButton_4.setObjectName("minusButton")
        self.label_2.setObjectName("countLabel")

    def _create_header_card(self) -> QFrame:
        header_card = QFrame(self)
        header_card.setObjectName("heroCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(22, 16, 22, 16)
        header_layout.setSpacing(4)

        eyebrow = QLabel("Gentle Counter")
        eyebrow.setObjectName("heroEyebrow")
        header_layout.addWidget(eyebrow)

        title = QLabel("消极思维计数器")
        title.setObjectName("heroTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("轻量记录今天出现的次数，用趋势代替自责。")
        subtitle.setObjectName("heroSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        return header_card

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget#thoughtCounterWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #eef4ee,
                    stop: 0.45 #f6f5ef,
                    stop: 1 #e6efe7
                );
                font-family: "Microsoft YaHei";
                color: #24362a;
            }
            QFrame#heroCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5ba76c,
                    stop: 1 #408f57
                );
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 18px;
            }
            QLabel#heroEyebrow {
                color: rgba(245, 255, 245, 0.78);
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QLabel#heroTitle {
                color: white;
                font-size: 22px;
                font-weight: 700;
            }
            QLabel#heroSubtitle {
                color: rgba(246, 255, 246, 0.9);
                font-size: 12px;
            }
            QFrame#counterPanel {
                background-color: rgba(255, 255, 255, 0.86);
                border: 1px solid #d4e4cf;
                border-radius: 22px;
                padding: 22px;
            }
            QPushButton#dateButton {
                background-color: #eef5ea;
                color: #44614b;
                border: 1px solid #c7d9c1;
                border-radius: 14px;
                padding: 10px 12px;
                text-align: left;
            }
            QPushButton#dateButton:hover {
                background-color: #e4efe1;
            }
            QLabel#countLabel {
                color: #4c9b5f;
                font-size: 44px;
                font-weight: 700;
            }
            QPushButton#minusButton, QPushButton#plusButton {
                min-width: 56px;
                min-height: 56px;
                border-radius: 28px;
                border: none;
                color: white;
                font-size: 22px;
                font-weight: 700;
            }
            QPushButton#minusButton {
                background-color: #c96f6b;
            }
            QPushButton#minusButton:hover {
                background-color: #b85f5b;
            }
            QPushButton#plusButton {
                background-color: #56a368;
            }
            QPushButton#plusButton:hover {
                background-color: #4a955c;
            }
            QPushButton#saveButton, QPushButton#statsButton {
                min-height: 44px;
                border-radius: 14px;
                font-size: 13px;
                font-weight: 600;
                border: none;
                padding: 10px 18px;
            }
            QPushButton#saveButton {
                background-color: #4f9c61;
                color: white;
            }
            QPushButton#saveButton:hover {
                background-color: #458c56;
            }
            QPushButton#statsButton {
                background-color: #edf5ea;
                color: #44614b;
                border: 1px solid #c7d9c1;
            }
            QPushButton#statsButton:hover {
                background-color: #e5efe0;
            }
            """
        )

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
            self.count_data = self.storage.get_thought_counts()
            self.current_count = self.count_data.get(self.today, 0)
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
        self.count_data[self.date] = self.current_count
        try:
            self.storage.save_thought_count(self.date, self.current_count)
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
        self.statistics_window = ThoughtCounterPlotWindow(count_data=self.count_data, today=self.today)
        self.statistics_window.show()
        

    def closeEvent(self, event):
        # 通知主窗口清理
        if self.main_window and hasattr(self.main_window, 'close_tool'):
            self.main_window.close_tool("thought_counter")
        super().closeEvent(event)
