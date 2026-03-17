import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
import pyqtgraph as pg

class ElegantPlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("精美折线图示例 - PySide6 + PyQtGraph")
        self.resize(1000, 600)

        # 设置整体样式（可选：深色主题更现代）
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #1e1e1e; color: #dcdcdc; }
            QLabel { color: #ffffff; }
        """)

        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建 PyQtGraph 的 PlotWidget
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        # 美化 PlotWidget 样式
        self.setup_plot()

    def setup_plot(self):
        # --- 1. 设置背景和主题 ---
        self.plot_widget.setBackground("#1e1e1e")  # 深色背景
        self.plot_widget.getPlotItem().getAxis('bottom').setPen(pg.mkPen(color='#cccccc', width=1.5))
        self.plot_widget.getPlotItem().getAxis('left').setPen(pg.mkPen(color='#cccccc', width=1.5))
        self.plot_widget.getPlotItem().getAxis('bottom').setTextPen(pg.mkPen(color='#ffffff', size=12))
        self.plot_widget.getPlotItem().getAxis('left').setTextPen(pg.mkPen(color='#ffffff', size=12))

        # --- 2. 添加网格 ---
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # --- 3. 设置标题 ---
        title_style = "<span style='font-size: 18px; color: #ffffff; font-family: Microsoft YaHei;'>"
        self.plot_widget.setTitle("传感器数据趋势分析", color='#ffffff', size="18px", font="Microsoft YaHei")

        # --- 4. 生成示例数据 ---
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x) * np.exp(-x * 0.2) + 0.1 * np.random.normal(size=x.shape)
        y2 = np.cos(x) * np.exp(-x * 0.3) + 0.1 * np.random.normal(size=x.shape)

        # --- 5. 绘制多条折线，使用不同颜色和样式 ---
        pen1 = pg.mkPen(color='#FF6B6B', width=2.5, style=Qt.SolidLine)  # 红色
        pen2 = pg.mkPen(color='#4ECDC4', width=2.5, style=Qt.DashLine)   # 青色虚线

        curve1 = self.plot_widget.plot(x, y1, name="传感器A", pen=pen1, symbol='o', symbolSize=6, symbolBrush='#FF6B6B', symbolPen=None)
        curve2 = self.plot_widget.plot(x, y2, name="传感器B", pen=pen2, symbol='t', symbolSize=7, symbolBrush='#4ECDC4', symbolPen=None)

        # --- 6. 添加图例 ---
        legend = self.plot_widget.addLegend(offset=(10, 10))
        legend.setBrush(pg.mkColor('#333333'))
        legend.setLabelTextColor('#ffffff')
        legend.setPen(pg.mkPen(color='#666666', width=1))

        # --- 7. 设置坐标轴标签 ---
        self.plot_widget.setLabel('left', '信号强度', units='V', color='white', **{'font-size': '14px'})
        self.plot_widget.setLabel('bottom', '时间', units='s', color='white', **{'font-size': '14px'})

        # --- 8. 可选：添加注释 ---
        text_item = pg.TextItem("峰值区域", color=(200, 200, 200), anchor=(0.5, 1))
        text_item.setFont(pg.Qt.QtGui.QFont("Microsoft YaHei", 10))
        peak_x = x[np.argmax(y1)]
        peak_y = np.max(y1)
        text_item.setPos(peak_x, peak_y + 0.2)
        self.plot_widget.addItem(text_item)

        # --- 9. 美化缩放和交互体验 ---
        # PyQtGraph 默认支持缩放/平移，无需额外代码
        # 可以禁用某些交互 if needed:
        # self.plot_widget.setMouseEnabled(x=True, y=True)


def main():
    app = QApplication(sys.argv)
    window = ElegantPlotWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()