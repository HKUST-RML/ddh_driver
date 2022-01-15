from odrive.enums import *


class Actuator(object):

    def __init__(self, axis, encoder_offset, direction, link_offset):
        self.axis = axis
        self.encoder_offset = encoder_offset
        self.direction = direction
        self.link_offset = link_offset

    @property
    def motor_pos(self):
        return 360 * self.direction * (self.axis.encoder.pos_estimate - self.encoder_offset)

    @motor_pos.setter
    def motor_pos(self, setpoint):
        self.axis.controller.input_pos = (setpoint / 360.) * self.direction + self.encoder_offset

    @property
    def theta(self):
        return self.motor_pos + self.link_offset

    @theta.setter
    def theta(self, setpoint):
        self.motor_pos = setpoint - self.link_offset

    @property
    def armed(self):
        return self.axis.requested_state is AXIS_STATE_CLOSED_LOOP_CONTROL

    @armed.setter
    def armed(self, val):
        if val:  # arm
            self.axis.controller.config.input_mode = INPUT_MODE_POS_FILTER  # INPUT_MODE_PASSTHROUGH
            self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            self.axis.controller.config.vel_gain = 1
        else:  # disarm
            self.axis.requested_state = AXIS_STATE_IDLE

    @property
    def stiffness(self):
        return self.axis.controller.config.pos_gain

    @stiffness.setter
    def stiffness(self, val):
        self.axis.controller.config.pos_gain = val

    @property
    def bandwidth(self):
        return self.axis.controller.config.input_filter_bandwidth

    @bandwidth.setter
    def bandwidth(self, val):
        self.axis.controller.config.input_filter_bandwidth = val
