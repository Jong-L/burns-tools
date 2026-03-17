from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader


from mplwidget import MplWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主窗口")
        self.resize(800,600)

        loader = QUiLoader()
        loader.registerCustomWidget(MplWidget)
        self.ui= loader.load("tools/thought_count_plot.ui")

        self.ui.mplWidget.axes.plot([1,2,3,4,5],[1,4,9,16,25])
        
        self.setCentralWidget(self.ui)

app= QApplication([])
window = MainWindow()
window.show()
app.exec()
