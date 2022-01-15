#!/usr/bin/python3

import os
import time
import numpy as np
from numpy import deg2rad, rad2deg
import odrive
from odrive.enums import *
import yaml
import dpath.util as dpath
from .actuator import Actuator

def arm(axis, gain, BW):
    axis.controller.config.input_mode = INPUT_MODE_POS_FILTER #INPUT_MODE_PASSTHROUGH
    axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    axis.controller.config.pos_gain = gain
    axis.controller.config.vel_gain = 1
    axis.controller.config.input_filter_bandwidth = BW

def disarm(axis):
    axis.requested_state = AXIS_STATE_IDLE

def set_pos_gain(axis, pos_gain):
    axis.controller.config.pos_gain = pos_gain 

def set_input_bandwidth(axis, BW):
    axis.controller.config.input_filter_bandwidth = BW


class DDGripper(object):

    def __init__(self, config_name):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', config_name + '.yaml')
        print('load config %s' % os.path.abspath(config_path))
        with open(config_path, 'r') as stream:
            try:
                print('reading gripper config...')
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.odrive_serial_R = dpath.get(config, 'odrive_serial/R')
        self.odrive_serial_L = dpath.get(config, 'odrive_serial/L')
        self.R0_offset = dpath.get(config, 'motors/R0/offset')
        self.R0_dir = dpath.get(config, 'motors/R0/dir')
        self.R1_offset = dpath.get(config, 'motors/R1/offset')
        self.R1_dir = dpath.get(config, 'motors/R1/dir')
        self.L0_offset = dpath.get(config, 'motors/L0/offset')
        self.L0_dir = dpath.get(config, 'motors/L0/dir')
        self.L1_offset = dpath.get(config, 'motors/L1/offset')
        self.L1_dir = dpath.get(config, 'motors/L1/dir')
        self.R0_link = dpath.get(config, 'linkages/R0')
        self.R1_link = dpath.get(config, 'linkages/R1')
        self.L0_link = dpath.get(config, 'linkages/L0')
        self.L1_link = dpath.get(config, 'linkages/L1')
        self.geometry_l1 = dpath.get(config, 'geometry/l1')
        self.geometry_l2 = dpath.get(config, 'geometry/l2')
        self.geometry_beta = dpath.get(config, 'geometry/beta')
        self.geometry_l3 = dpath.get(config, 'geometry/l3')
        self.geometry_gamma = dpath.get(config, 'geometry/gamma')
        self.r_max_offset = dpath.get(config, 'geometry/r_max_offset')
        self.r_min_offset = dpath.get(config, 'geometry/r_min_offset')

        # virtual link formed by l2 and l3
        self._l3 = np.sqrt(self.geometry_l2**2 + self.geometry_l3**2 - 2 * self.geometry_l2 * self.geometry_l3 * np.cos(deg2rad(self.geometry_gamma)))
        # angle between l2 and _l3
        self._gamma = rad2deg(np.arcsin(np.sin(deg2rad(self.geometry_gamma))/self._l3*self.geometry_l3))
        # range of IK for the distal joint
        self.r_min = np.sqrt(self.geometry_l1**2 - self.geometry_l2**2) + self.r_min_offset
        self.r_max = self.geometry_l1 + self.geometry_l2 - self.r_max_offset

        print('connecting to odrive...')
        self.finger_L = odrive.find_any(serial_number=self.odrive_serial_L)
        print('found left finger')
        self.finger_R = odrive.find_any(serial_number=self.odrive_serial_R)
        print('found right finger')

        self.R0 = Actuator(self.finger_R.axis0, self.R0_offset, self.R0_dir, self.R0_link)
        self.R1 = Actuator(self.finger_R.axis1, self.R1_offset, self.R1_dir, self.R1_link)
        self.L0 = Actuator(self.finger_L.axis0, self.L0_offset, self.L0_dir, self.L0_link)
        self.L1 = Actuator(self.finger_L.axis1, self.L1_offset, self.L1_dir, self.L1_link)

    def arm(self, gain=250, BW=500):
        arm(self.finger_L.axis0, gain, BW)
        arm(self.finger_L.axis1, gain, BW)
        arm(self.finger_R.axis0, gain, BW)
        arm(self.finger_R.axis1, gain, BW)

    def disarm(self):
        disarm(self.finger_L.axis0)
        disarm(self.finger_L.axis1)
        disarm(self.finger_R.axis0)
        disarm(self.finger_R.axis1)

    def set_stiffness(self, gain, finger='LR'):
        if finger == 'LR':
            set_pos_gain(self.finger_L.axis0, gain)
            set_pos_gain(self.finger_L.axis1, gain)
            set_pos_gain(self.finger_R.axis0, gain)
            set_pos_gain(self.finger_R.axis1, gain)
        elif finger == 'L':
            set_pos_gain(self.finger_L.axis0, gain)
            set_pos_gain(self.finger_L.axis1, gain)
        elif finger == 'R':
            set_pos_gain(self.finger_R.axis0, gain)
            set_pos_gain(self.finger_R.axis1, gain)
        else:
            print("Invalid finger argument.")

    def set_bandwidth(self, BW):
        set_input_bandwidth(self.finger_L.axis0, BW)
        set_input_bandwidth(self.finger_L.axis1, BW)
        set_input_bandwidth(self.finger_R.axis0, BW)
        set_input_bandwidth(self.finger_R.axis1, BW)

    @property
    def motor_pos_r0(self):
        return 360 * self.R0_dir * (self.finger_R.axis0.encoder.pos_estimate - self.R0_offset)

    @property
    def motor_pos_r1(self):
        return 360 * self.R1_dir * (self.finger_R.axis1.encoder.pos_estimate - self.R1_offset)

    @property
    def motor_pos_l0(self):
        return 360 * self.L0_dir * (self.finger_L.axis0.encoder.pos_estimate - self.L0_offset)

    @property
    def motor_pos_l1(self):
        return 360 * self.L1_dir * (self.finger_L.axis1.encoder.pos_estimate - self.L1_offset)

    @property
    def link_pos_r0(self):
        return self.motor_pos_r0 + self.R0_link

    @property
    def link_pos_r1(self):
        return self.motor_pos_r1 + self.R1_link

    @property
    def link_pos_l0(self):
        return self.motor_pos_l0 + self.L0_link

    @property
    def link_pos_l1(self):
        return self.motor_pos_l1 + self.L1_link

    @property
    def right_a1(self):
        return (self.link_pos_r0+self.link_pos_r1)/2

    @property
    def right_a2(self):
        return (self.link_pos_r1-self.link_pos_r0)/2

    @property
    def left_a1(self):
        return (self.link_pos_l0+self.link_pos_l1)/2

    @property
    def left_a2(self):
        return (self.link_pos_l0-self.link_pos_l1)/2

    # r: distance from motor joint to distal joint (base joint of finger)

    @property
    def left_finger_dist(self):
        return self.geometry_l1*np.cos(deg2rad(self.left_a2)) + np.sqrt(self.geometry_l2**2 - (self.geometry_l1*np.sin(deg2rad(self.left_a2)))**2)

    @property
    def right_finger_dist(self):
        return self.geometry_l1*np.cos(deg2rad(self.right_a2)) + np.sqrt(self.geometry_l2**2 - (self.geometry_l1*np.sin(deg2rad(self.right_a2)))**2)

    # position of distal joint (base joint of finger) in motor frame

    @property
    def left_finger_pos(self): 
        x = self.left_finger_dist * np.cos(deg2rad(self.left_a1))
        y = self.left_finger_dist * np.sin(deg2rad(self.left_a1))
        return x, y

    @property
    def right_finger_pos(self): 
        x = self.right_finger_dist * np.cos(deg2rad(self.right_a1))
        y = self.right_finger_dist * np.sin(deg2rad(self.right_a1))
        return x, y

    # a3: angle between distal link (L2) and vector from origin to distal joint

    @property
    def left_a3(self):
        return rad2deg(np.arccos((self.geometry_l1**2 - self.geometry_l2**2 - self.left_finger_dist**2)/(-2 * self.geometry_l2 * self.left_finger_dist)))

    @property
    def right_a3(self):
        return rad2deg(np.arccos((self.geometry_l1**2 - self.geometry_l2**2 - self.right_finger_dist**2)/(-2 * self.geometry_l2 * self.right_finger_dist)))

    # phi: angle of finger surface relative to x axis

    @property
    def left_phi(self):
        return self.left_a1 + self.left_a3 + self.geometry_beta - 180

    @property
    def right_phi(self):
        return self.right_a1 - (self.right_a3 + self.geometry_beta - 180)

    # position of fingertip in motor frame

    @property
    def left_tip_pos(self):
        # angle of l3 relative to x axis
        q_tip = self.left_a1 + self.left_a3 + self.geometry_gamma - 180
        x = self.left_finger_pos[0] + self.geometry_l3 * np.cos(deg2rad(q_tip))
        y = self.left_finger_pos[1] + self.geometry_l3 * np.sin(deg2rad(q_tip))
        return x, y

    @property
    def right_tip_pos(self):
        # angle of l3 relative to x axis
        q_tip = self.right_a1 - (self.right_a3 + self.geometry_gamma - 180)
        x = self.right_finger_pos[0] + self.geometry_l3 * np.cos(deg2rad(q_tip))
        y = self.right_finger_pos[1] + self.geometry_l3 * np.sin(deg2rad(q_tip))
        return x, y

    # first control the position of individual links

    def set_link_pos_r0(self, link_pos):
        motor_pos = link_pos - self.R0_link
        motor_pos = motor_pos/360.
        motor_input = motor_pos * self.R0_dir + self.R0_offset
        self.finger_R.axis0.controller.input_pos = motor_input

    def set_link_pos_r1(self, link_pos):
        motor_pos = link_pos - self.R1_link
        motor_pos = motor_pos/360.
        motor_input = motor_pos * self.R1_dir + self.R1_offset
        self.finger_R.axis1.controller.input_pos = motor_input

    def set_link_pos_l0(self, link_pos):
        motor_pos = link_pos - self.L0_link
        motor_pos = motor_pos/360.
        motor_input = motor_pos * self.L0_dir + self.L0_offset
        self.finger_L.axis0.controller.input_pos = motor_input

    def set_link_pos_l1(self, link_pos):
        motor_pos = link_pos - self.L1_link
        motor_pos = motor_pos/360.
        motor_input = motor_pos * self.L1_dir + self.L1_offset
        self.finger_L.axis1.controller.input_pos = motor_input

    # then control the finger (a1,a2)

    def set_right_a1(self, a1):
        a2 = self.right_a2
        self.set_link_pos_r0(a1-a2)
        self.set_link_pos_r1(a1+a2)

    def set_right_a2(self, a2):
        a1 = self.right_a1
        self.set_link_pos_r0(a1-a2)
        self.set_link_pos_r1(a1+a2)

    def set_right_a1_a2(self, a1, a2):
        self.set_link_pos_r0(a1-a2)
        self.set_link_pos_r1(a1+a2)

    def set_left_a1(self, a1):
        a2 = self.left_a2
        self.set_link_pos_l0(a1+a2)
        self.set_link_pos_l1(a1-a2)

    def set_left_a2(self, a2):
        a1 = self.left_a1
        self.set_link_pos_l0(a1+a2)
        self.set_link_pos_l1(a1-a2)

    def set_left_a1_a2(self, a1, a2):
        self.set_link_pos_l0(a1+a2)
        self.set_link_pos_l1(a1-a2)

    # then add inverse kinematics

    def ik_right_a1_phi(self, a1, phi):
        a2_rad = np.arcsin(np.sin(-deg2rad(a1)+deg2rad(self.geometry_beta)+deg2rad(phi))*self.geometry_l2/self.geometry_l1)
        return a1, rad2deg(a2_rad)

    def set_right_a1_phi(self, a1, phi):
        cmd_a1, cmd_a2 = self.ik_right_a1_phi(a1, phi)
        self.set_right_a1_a2(cmd_a1, cmd_a2)

    def ik_left_a1_phi(self, a1, phi):
        a2_rad = np.arcsin(np.sin(deg2rad(a1)+deg2rad(self.geometry_beta)-deg2rad(phi))*self.geometry_l2/self.geometry_l1)
        return a1, rad2deg(a2_rad)

    def set_left_a1_phi(self, a1, phi):
        cmd_a1, cmd_a2 = self.ik_left_a1_phi(a1, phi)
        self.set_left_a1_a2(cmd_a1, cmd_a2)

    # ik of finger joint pos

    def ik_finger_pos(self, pos):
        x, y = pos
        r = np.sqrt(x**2+y**2)
        r = max(self.r_min,min(r, self.r_max))
        a1 = rad2deg(np.arctan2(y,x))
        a2 = rad2deg(np.arccos((self.geometry_l2**2-self.geometry_l1**2-r**2)/(-2*self.geometry_l1*r)))
        return a1, a2

    def set_left_finger_pos(self, pos):
        cmd_a1, cmd_a2 = self.ik_finger_pos(pos)
        self.set_left_a1_a2(cmd_a1, cmd_a2)

    def set_right_finger_pos(self, pos):
        cmd_a1, cmd_a2 = self.ik_finger_pos(pos)
        self.set_right_a1_a2(cmd_a1, cmd_a2)

    # ik of fingertip

    def ik_finger_tip(self, pos, finger):
        np.seterr(all = "raise")
        x_tip, y_tip = pos
        # link from origin to tip
        l_tip = np.sqrt(x_tip**2+y_tip**2)
        # angle of l_tip relative to x axis
        q_tip = rad2deg(np.arctan2(y_tip,x_tip))
        # angle between l1 and l_tip
        q_1_tip = rad2deg(np.arccos((self._l3**2 - self.geometry_l1**2 - l_tip**2)/(-2 * self.geometry_l1 * l_tip)))
        # angle of l1 relative to x axis
        if finger == 'L': # left finger
            q1 =  q_tip - q_1_tip
        elif finger == 'R': # right finger
            q1 = q_tip + q_1_tip
        # angle between l1 and _l3
        q_1__3 = rad2deg(np.arccos((l_tip**2 - self.geometry_l1**2 - self._l3**2)/(-2 * self.geometry_l1 * self._l3)))
        # angle between l1 and l2
        q21 = q_1__3 - self._gamma
        # angle of l2 relative to x axis
        if finger == 'L': # left finger
            q2 = 180 - q21 + q1
        elif finger == 'R': # right finger
            q2 = -180 + q21 + q1
        # target position of distal joint
        x = self.geometry_l1 * np.cos(deg2rad(q1)) + self.geometry_l2 * np.cos(deg2rad(q2))
        y = self.geometry_l1 * np.sin(deg2rad(q1)) + self.geometry_l2 * np.sin(deg2rad(q2))
        return self.ik_finger_pos((x,y))

    def set_left_tip(self, pos):
        print("Setting left tip:", pos)
        try:
            cmd_a1, cmd_a2 = self.ik_finger_tip(pos, 'L')
        except:
            print('Target position out of finger workspace!')
            return
        self.set_left_a1_a2(cmd_a1, cmd_a2)

    def set_right_tip(self, pos):
        print("Setting right tip:", pos)
        try:
            cmd_a1, cmd_a2 = self.ik_finger_tip(pos, 'R')
        except:
            print('Target position out of finger workspace!')
            return
        self.set_right_a1_a2(cmd_a1, cmd_a2)

    # parallel jaw

    def set_parallel_jaw(self, angle, phi):
        self.set_left_a1_phi(-angle, phi)
        self.set_right_a1_phi(angle, phi)

    def startup_dance(self):
        self.set_left_a1_a2(-90, 25)
        self.set_right_a1_a2(90, 25)
        time.sleep(0.5)
        self.set_parallel_jaw(-15, 0)
        time.sleep(0.5)
        self.set_parallel_jaw(25, 0)
        time.sleep(0.5)
        self.set_parallel_jaw(-15, 0)
        time.sleep(0.5)
        self.set_parallel_jaw(-10, 15)
        time.sleep(0.5)
        self.set_parallel_jaw(-10, -15)
        time.sleep(0.5)
        self.set_parallel_jaw(0, 0)