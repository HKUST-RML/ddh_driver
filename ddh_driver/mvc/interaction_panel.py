from enum import IntEnum, Enum

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGroupBox


class InteractionPanel:

    class InteractionState(Enum):
        idle = 0
        theta_R0 = 1
        theta_R1 = 2
        theta_L0 = 3
        theta_L1 = 4

    def __init__(self, model):
        self.model = model
        self.view = QWidget()
        self.view.setMinimumWidth(600)
