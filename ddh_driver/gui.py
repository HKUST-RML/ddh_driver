from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QSize
import sys
from ddh_driver import Gripper


class DDHModel:

    def __init__(self):
        pass
        #self.gripper = Gripper('default')


class ActuatorsPanelController:

    def __init__(self, model):
        self.model = model
        self.view = QWidget()
        self.view.setLayout(QVBoxLayout())


class PlotPanelController:

    def __init__(self, model):
        self.model = model
        self.view = QWidget()
        self.view.setLayout(QVBoxLayout())


class InteractPanelController:

    def __init__(self, model):
        self.model = model
        self.view = QWidget()


class ControlPanelController:

    def __init__(self):
        self.model = DDHModel()
        # setup sub-controllers
        self.actuators_panel = ActuatorsPanelController(self.model)
        self.plot_panel = PlotPanelController(self.model)
        self.interact_panel = InteractPanelController(self.model)
        # setup view
        self.view = QWidget()
        self.init_view()

    def init_view(self):
        self.view.setWindowTitle('Direct-Drive Hand Control Panel')
        self.view.setFixedSize(QSize(800, 600))
        self.view.setLayout(QHBoxLayout())
        self.view.layout().addWidget(self.actuators_panel.view)
        self.view.layout().addWidget(self.plot_panel.view)
        self.view.layout().addWidget(self.interact_panel.view)


def main():
    app = QApplication(sys.argv)
    control_panel = ControlPanelController()
    control_panel.view.show()
    app.exec()


if __name__ == '__main__':
    main()

