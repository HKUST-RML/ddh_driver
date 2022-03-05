from odrive.enums import *


class Actuator(object):

    def __init__(self, name, axis, encoder_offset, direction, link_offset):
        self.name = name
        self.axis = axis
        self.encoder_offset = encoder_offset
        self.direction = direction
        self.link_offset = link_offset

    def motor2theta(self, q):
        return q + self.link_offset

    def encoder2motor(self, q):
        return 360 * self.direction * (q - self.encoder_offset)

    def encoder2theta(self, q):
        return self.motor2theta(self.encoder2motor(q))

    @property
    def encoder(self):
        return self.axis.encoder.pos_estimate

    @property
    def motor_pos(self):
        return 360 * self.direction * (self.axis.encoder.pos_estimate - self.encoder_offset)

    @motor_pos.setter
    def motor_pos(self, setpoint):
        self.axis.controller.input_pos = (setpoint / 360.) * self.direction + self.encoder_offset

    @property
    def setpoint(self):
        return self.encoder2theta(self.axis.controller.input_pos)

    @setpoint.setter
    def setpoint(self, val):
        self.motor_pos = val - self.link_offset

    @property
    def theta(self):
        return self.motor_pos + self.link_offset

    @theta.setter
    def theta(self, setpoint):
        self.setpoint = setpoint

    @property
    def armed(self):
        return self.axis.current_state is AXIS_STATE_CLOSED_LOOP_CONTROL

    @armed.setter
    def armed(self, val):
        if val:  # arm
            self.axis.controller.config.input_mode = INPUT_MODE_POS_FILTER  # INPUT_MODE_PASSTHROUGH
            self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        else:  # disarm
            self.axis.requested_state = AXIS_STATE_IDLE

    @property
    def stiffness(self):
        return self.axis.controller.config.pos_gain

    @stiffness.setter
    def stiffness(self, val):
        self.axis.controller.config.pos_gain = val

    @property
    def vel_gain(self):
        return self.axis.controller.config.vel_gain

    @vel_gain.setter
    def vel_gain(self, val):
        self.axis.controller.config.vel_gain = val

    @property
    def bandwidth(self):
        return self.axis.controller.config.input_filter_bandwidth

    @bandwidth.setter
    def bandwidth(self, val):
        self.axis.controller.config.input_filter_bandwidth = val
