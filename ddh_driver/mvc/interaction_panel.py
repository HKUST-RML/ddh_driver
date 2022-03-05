import math
from enum import IntEnum, Enum
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGroupBox
from PyQt5.QtCore import QSize, QPointF, QPoint
from PyQt5.QtGui import QColor, QPalette
import ddh_driver
import numpy as np


class InteractionState(Enum):
    idle = 0
    theta_R0 = 1
    theta_R1 = 2
    theta_L0 = 3
    theta_L1 = 4


clr_link = QColor('black')
clr_joint = clr_link
clr_joint_highlight = QColor('green')
clr_background = QColor('white')

CLICK_RADIUS = 20


def dist_QPointF(pt1: QPointF, pt2: QPointF):
    return math.sqrt((pt1.x()-pt2.x())**2 + (pt1.y()-pt2.y())**2)


class KinematicModel:

    def __init__(self, gripper: ddh_driver.Gripper):
        self.gripper = gripper
        self.origin = np.array([0, 0])
        self.pt_O_l = np.array([0, -self.gripper.geometry_l0/2])
        self.pt_O_r = np.array([0, self.gripper.geometry_l0/2])

    @property
    def pt_r0(self):
        theta = np.deg2rad(self.gripper.R0.theta)
        l1 = self.gripper.geometry_l1
        return l1 * np.array([np.cos(theta), np.sin(theta)]) + self.pt_O_r

    @property
    def pt_r1(self):
        theta = np.deg2rad(self.gripper.R1.theta)
        l1 = self.gripper.geometry_l1
        return l1 * np.array([np.cos(theta), np.sin(theta)]) + self.pt_O_r

    @property
    def pt_l0(self):
        theta = np.deg2rad(self.gripper.L0.theta)
        l1 = self.gripper.geometry_l1
        return l1 * np.array([np.cos(theta), np.sin(theta)]) + self.pt_O_l

    @property
    def pt_l1(self):
        theta = np.deg2rad(self.gripper.L1.theta)
        l1 = self.gripper.geometry_l1
        return l1 * np.array([np.cos(theta), np.sin(theta)]) + self.pt_O_l


class InteractionPanel:

    def __init__(self, model: ddh_driver.Gripper):
        self.model = model
        self.kinematics_model = KinematicModel(model)
        self.fsm = InteractionState.idle
        self.setup_view()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30)

    def setup_view(self):
        self.view = QLabel()
        self.width = 600
        self.height = 600
        self.canvas = QtGui.QPixmap(self.width, self.height)
        self.view.setPixmap(self.canvas)
        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mouseReleaseEvent = self.on_mouse_release
        self.view.mousePressEvent = self.on_mouse_press
        self.scale = 3
        self.center = np.array([self.width/2, self.height/4])  # in ui frame
        self.pen_link = QtGui.QPen()
        self.pen_link.setWidth(5)
        self.pen_link.setColor(clr_link)
        self.pen_link.setBrush(clr_link)

    def refresh(self):
        self.view.pixmap().fill(clr_background)
        painter = QtGui.QPainter(self.view.pixmap())
        painter.setPen(self.pen_link)
        # current points in ui frame
        O_r = self.gripper2ui(self.kinematics_model.pt_O_r)
        O_l = self.gripper2ui(self.kinematics_model.pt_O_l)
        pt_r0 = self.gripper2ui(self.kinematics_model.pt_r0)
        pt_r1 = self.gripper2ui(self.kinematics_model.pt_r1)
        pt_l0 = self.gripper2ui(self.kinematics_model.pt_l0)
        pt_l1 = self.gripper2ui(self.kinematics_model.pt_l1)
        # draw the proximal links
        painter.drawLine(O_r, pt_r0)
        painter.drawLine(O_r, pt_r1)
        painter.drawLine(O_l, pt_l0)
        painter.drawLine(O_l, pt_l1)
        # draw joint
        painter.setBrush(clr_link)
        painter.drawEllipse(pt_r0, 10, 10)
        painter.drawEllipse(pt_r1, 10, 10)
        painter.drawEllipse(pt_l0, 10, 10)
        painter.drawEllipse(pt_l1, 10, 10)
        painter.end()
        self.view.update()

    def ui2gripper(self, pt: np.ndarray):
        """
        Convert 2D Point from UI frame to Gripper Frame
        """
        pt = (pt - self.center) / self.scale
        return np.array([pt[1], pt[0]])

    def gripper2ui(self, pt):
        """
        Convert 2D Point from Gripper Frame to UI Frame
        """
        pt = pt * self.scale
        pt = np.array([pt[1], pt[0]]) + self.center
        return QtCore.QPointF(pt[0], pt[1])

    def cmd_r0(self, pt):
        v = pt-self.kinematics_model.pt_O_r
        theta = np.rad2deg(math.atan2(v[1], v[0]))
        self.model.R0.setpoint = theta

    def cmd_r1(self, pt):
        v = pt-self.kinematics_model.pt_O_r
        theta = np.rad2deg(math.atan2(v[1], v[0]))
        self.model.R1.setpoint = theta

    def cmd_l0(self, pt):
        v = pt-self.kinematics_model.pt_O_l
        theta = np.rad2deg(math.atan2(v[1], v[0]))
        self.model.L0.setpoint = theta

    def cmd_l1(self, pt):
        v = pt-self.kinematics_model.pt_O_l
        theta = np.rad2deg(math.atan2(v[1], v[0]))
        self.model.L1.setpoint = theta

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        if self.fsm is InteractionState.idle:
            return
        pos = e.localPos()
        pt = np.array([pos.x(), pos.y()])
        pt = self.ui2gripper(pt)
        if self.fsm is InteractionState.theta_R0:
            self.cmd_r0(pt)
        elif self.fsm is InteractionState.theta_R1:
            self.cmd_r1(pt)
        elif self.fsm is InteractionState.theta_L0:
            self.cmd_l0(pt)
        elif self.fsm is InteractionState.theta_L1:
            self.cmd_l1(pt)

    def on_mouse_release(self, e):
        self.fsm = InteractionState.idle

    def on_mouse_press(self, e):
        pt_r0 = self.gripper2ui(self.kinematics_model.pt_r0)
        pt_r1 = self.gripper2ui(self.kinematics_model.pt_r1)
        pt_l0 = self.gripper2ui(self.kinematics_model.pt_l0)
        pt_l1 = self.gripper2ui(self.kinematics_model.pt_l1)
        click_pos = e.localPos()
        if dist_QPointF(pt_r0, click_pos) < CLICK_RADIUS:
            self.fsm = InteractionState.theta_R0
        elif dist_QPointF(pt_r1, click_pos) < CLICK_RADIUS:
            self.fsm = InteractionState.theta_R1
        elif dist_QPointF(pt_l0, click_pos) < CLICK_RADIUS:
            self.fsm = InteractionState.theta_L0
        elif dist_QPointF(pt_l1, click_pos) < CLICK_RADIUS:
            self.fsm = InteractionState.theta_L1
