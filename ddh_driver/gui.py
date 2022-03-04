from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel
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
        self.R0_controller = ActuatorController(model, 'R0')
        self.R1_controller = ActuatorController(model, 'R1')
        self.L0_controller = ActuatorController(model, 'L0')
        self.L1_controller = ActuatorController(model, 'L1')

        self.view = QWidget()
        self.view.setLayout(QVBoxLayout())
        self.view.layout().addWidget(self.R0_controller.view)
        self.view.layout().addWidget(self.R1_controller.view)
        self.view.layout().addWidget(self.L0_controller.view)
        self.view.layout().addWidget(self.L1_controller.view)


class ActuatorController:

    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.setup_view()

    def setup_view(self):
        self.view = QWidget()
        self.view.setLayout(QVBoxLayout())
        self.view_title = QLabel()
        self.view_title.setText(self.name)
        self.view.layout().addWidget(self.view_title)


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

