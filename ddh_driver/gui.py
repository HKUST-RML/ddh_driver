import math
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import QSize
import pyqtgraph as pg
import numpy as np
import sys
import ddh_driver


class DDHModel:

    def __init__(self):
        self.gripper = ddh_driver.Gripper('default')
        self.gripper.arm()
        self.gripper.left_a1 = 0
        self.gripper.left_a2 = 20
        self.gripper.right_a1 = 0
        self.gripper.right_a2 = 20


class ActuatorsPanel:

    def __init__(self, model):
        self.model = model
        self.R0_controller = ActuatorEntry(model, 'R0')
        self.R1_controller = ActuatorEntry(model, 'R1')
        self.L0_controller = ActuatorEntry(model, 'L0')
        self.L1_controller = ActuatorEntry(model, 'L1')

        self.view = QWidget()
        self.view.setLayout(QVBoxLayout())
        self.view.layout().addWidget(self.R0_controller.view)
        self.view.layout().addWidget(self.R1_controller.view)
        self.view.layout().addWidget(self.L0_controller.view)
        self.view.layout().addWidget(self.L1_controller.view)


class ActuatorEntry:

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


class PlotPanel:

    def __init__(self, model: DDHModel):
        self.model = model
        self.r0_plot = StateSetpointPlot(model.gripper.R0)
        self.r1_plot = StateSetpointPlot(model.gripper.R1)
        self.l0_plot = StateSetpointPlot(model.gripper.L0)
        self.l1_plot = StateSetpointPlot(model.gripper.L1)
        self.setup_view()

    def setup_view(self):
        self.view = QWidget()
        self.view.setLayout(QVBoxLayout())
        self.view.layout().addWidget(self.r0_plot.view)
        self.view.layout().addWidget(self.r1_plot.view)
        self.view.layout().addWidget(self.l0_plot.view)
        self.view.layout().addWidget(self.l1_plot.view)


class StateSetpointPlot:
    def __init__(self, model: ddh_driver.Actuator):
        self.model = model
        self.t0 = time.perf_counter()
        self.state_vt = []
        self.state_v = []
        self.sp_vt = []
        self.sp_v = []
        self.setup_view()
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(20)

    def setup_view(self):
        self.view = pg.PlotWidget(name='Plot')
        self.line_sp = self.view.plot()
        self.line_state = self.view.plot()
        self.line_state.setPen('r')
        self.line_sp.setPen('g')

    def update_plot(self):
        dt = time.perf_counter() - self.t0
        self.state_vt.append(dt)
        self.state_v.append(self.model.theta)
        if self.model.armed:
            self.sp_vt.append(dt)
            self.sp_v.append(self.model.setpoint)
        self.line_state.setData(x=self.state_vt, y=self.state_v)
        self.line_sp.setData(x=self.sp_vt, y=self.sp_v)


class InteractPanel:

    def __init__(self, model):
        self.model = model
        self.view = QWidget()


class ControlPanel:

    def __init__(self):
        self.model = DDHModel()
        # setup sub-controllers
        self.actuators_panel = ActuatorsPanel(self.model)
        self.plot_panel = PlotPanel(self.model)
        self.interact_panel = InteractPanel(self.model)
        # setup view
        self.view = QWidget()
        self.init_view()

    def init_view(self):
        self.view.setWindowTitle('Direct-Drive Hand Control Panel')
        self.view.setMinimumSize(QSize(800, 600))
        self.view.setLayout(QHBoxLayout())
        self.view.layout().addWidget(self.actuators_panel.view)
        self.view.layout().addWidget(self.plot_panel.view)
        self.view.layout().addWidget(self.interact_panel.view)


def main():
    app = QApplication(sys.argv)
    control_panel = ControlPanel()
    control_panel.view.show()
    app.exec()


if __name__ == '__main__':
    main()

