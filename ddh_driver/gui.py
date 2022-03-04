import math
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import QSize
import pyqtgraph as pg
import numpy as np
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
        self.r0_plot = TimePlotController()
        self.r1_plot = TimePlotController()
        self.setup_view()

    def setup_view(self):
        self.view = QWidget()
        self.view.setLayout(QVBoxLayout())
        self.view.layout().addWidget(self.r0_plot.view)
        self.view.layout().addWidget(self.r1_plot.view)


class TimePlotController:
    def __init__(self):
        self.t0 = time.perf_counter()
        self.vx = []
        self.vy = []
        self.setup_view()
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(20)

    def setup_view(self):
        self.view = pg.PlotWidget(name='Plot')
        self.line = self.view.plot()

    def update_plot(self):
        dt = time.perf_counter() - self.t0
        self.vx.append(dt)
        self.vy.append(math.sin(dt))
        self.line.setData(x=self.vx, y=self.vy)



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

