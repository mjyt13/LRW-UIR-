from gui1 import QtWidgets, Ui_DashBoard
import sys

def exe():
    app = QtWidgets.QApplication(sys.argv)
    DashBoard = QtWidgets.QMainWindow()
    ui = Ui_DashBoard()
    ui.setupUi(DashBoard)
    DashBoard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    exe()
