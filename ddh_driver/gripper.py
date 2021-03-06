import os
import time
import numpy as np
from numpy import deg2rad, rad2deg
import odrive
import dpath.util as dpath
from .actuator import Actuator
from .utils import *


class Gripper(object):

    def __init__(self, config_name):
        config = load_ddh_config(config_name)
        self.odrive_serial_R = dpath.get(config, 'odrive_serial/R')
        self.odrive_serial_L = dpath.get(config, 'odrive_serial/L')
        self.R0_offset = dpath.get(config, 'motors/R0/offset')
        self.R1_offset = dpath.get(config, 'motors/R1/offset')
        self.L0_offset = dpath.get(config, 'motors/L0/offset')
        self.L1_offset = dpath.get(config, 'motors/L1/offset')
        self.R0_dir = dpath.get(config, 'motors/R0/dir')
        self.R1_dir = dpath.get(config, 'motors/R1/dir')
        self.L0_dir = dpath.get(config, 'motors/L0/dir')
        self.L1_dir = dpath.get(config, 'motors/L1/dir')
        self.R0_link = dpath.get(config, 'linkages/R0')
        self.R1_link = dpath.get(config, 'linkages/R1')
        self.L0_link = dpath.get(config, 'linkages/L0')
        self.L1_link = dpath.get(config, 'linkages/L1')
        self.geometry_l1 = dpath.get(config, 'geometry/l1')
        self.geometry_l2 = dpath.get(config, 'geometry/l2')
        self.geometry_l3 = dpath.get(config, 'geometry/l3')
        self.geometry_beta = dpath.get(config, 'geometry/beta')
        self.geometry_gamma = dpath.get(config, 'geometry/gamma')
        self.r_max_offset = dpath.get(config, 'geometry/r_max_offset')
        self.r_min_offset = dpath.get(config, 'geometry/r_min_offset')

        # a2 when distal links in singularity (collinear)
        self.a2_sing = rad2deg(np.arcsin(self.geometry_l2/self.geometry_l1))
        # virtual link formed by l2 and l3
        self._l3 = np.sqrt(self.geometry_l2**2 + self.geometry_l3**2 - 2 * self.geometry_l2 * self.geometry_l3 * np.cos(deg2rad(self.geometry_gamma)))
        # angle between l2 and _l3
        self._gamma = rad2deg(np.arcsin(np.sin(deg2rad(self.geometry_gamma))/self._l3*self.geometry_l3))
        # range of IK for the distal joint
        self.r_min = np.sqrt(self.geometry_l1**2 - self.geometry_l2**2) + self.r_min_offset
        self.r_max = self.geometry_l1 + self.geometry_l2 - self.r_max_offset

        print('Connecting to Odrive(s)...')
        self.odrive_L = odrive.find_any(serial_number=self.odrive_serial_L)
        print('Found Odrive_L')
        self.odrive_R = odrive.find_any(serial_number=self.odrive_serial_R)
        print('Found Odrive_R')

        self.R0 = Actuator(self.odrive_R.axis0, self.R0_offset, self.R0_dir, self.R0_link)
        self.R1 = Actuator(self.odrive_R.axis1, self.R1_offset, self.R1_dir, self.R1_link)
        self.L0 = Actuator(self.odrive_L.axis0, self.L0_offset, self.L0_dir, self.L0_link)
        self.L1 = Actuator(self.odrive_L.axis1, self.L1_offset, self.L1_dir, self.L1_link)

    def get_actuators(self, finger='LR'):
        if finger == 'LR':
            return [self.R0, self.R1, self.L0, self.L1]
        elif finger == 'L':
            return [self.L0, self.L1]
        elif finger == 'R':
            return [self.R0, self.R1]

    def arm(self, pos_gain=250, vel_gain = 1, BW=500, finger='LR'):
        for actuator in self.get_actuators(finger):
            actuator.bandwidth = BW
            actuator.stiffness = pos_gain
            actuator.vel_gain = vel_gain
            actuator.armed = True

    def disarm(self, finger='LR'):
        for actuator in self.get_actuators(finger):
            actuator.armed = False

    def set_stiffness(self, gain, finger='LR'):
        for actuator in self.get_actuators(finger):
            actuator.stiffness = gain
        
    def set_vel_gain(self, gain, finger='LR'):
        for actuator in self.get_actuators(finger):
            actuator.vel_gain = gain

    def set_bandwidth(self, BW, finger='LR'):
        for actuator in self.get_actuators(finger):
            actuator.bandwidth = BW

    # alpha1-alpha2 parameterization

    def set_right_a1_a2(self, a1, a2):
        self.R0.theta = a1-a2
        self.R1.theta = a1+a2

    def set_left_a1_a2(self, a1, a2):
        self.L0.theta = a1+a2
        self.L1.theta = a1-a2

    # forward kinematics function: link angles to a1, a2 angle 
    def link_to_a1(self, l0, l1):
        return (l0+l1)/2
    def link_to_a2(self, l0, l1):
        return np.absolute(l0-l1)/2

    @property
    def right_a1(self):
        return self.link_to_a1(self.R0.theta, self.R1.theta)

    @right_a1.setter
    def right_a1(self, a1):
        self.set_right_a1_a2(a1, self.right_a2)

    @property
    def right_a2(self):
        return self.link_to_a2(self.R0.theta, self.R1.theta)

    @right_a2.setter
    def right_a2(self, a2):
        self.set_right_a1_a2(self.right_a1, a2)

    @property
    def left_a1(self):
        return self.link_to_a1(self.L0.theta, self.L1.theta)

    @left_a1.setter
    def left_a1(self, a1):
        self.set_left_a1_a2(a1, self.left_a2)

    @property
    def left_a2(self):
        return self.link_to_a2(self.L0.theta, self.L1.theta)

    @left_a2.setter
    def left_a2(self, a2):
        self.set_left_a1_a2(self.left_a1, a2)

    # r: distance from motor joint to distal joint (base joint of finger)
    # forward kinematics function: a2 angle to r distance
    def a2_to_r(self, a2):
        if a2 > self.a2_sing:
            return  self.geometry_l1*np.cos(deg2rad(a2))
        else: 
            return self.geometry_l1*np.cos(deg2rad(a2)) + np.sqrt(self.geometry_l2**2 - (self.geometry_l1*np.sin(deg2rad(a2)))**2)

    @property
    def left_finger_dist(self):
        return self.a2_to_r(self.left_a2)

    @property
    def right_finger_dist(self):
        return self.a2_to_r(self.right_a2)

    # forward kinematics function: r, a2 angle to distal joint coordinate
    def r_a1_to_rx_ry(self, r, a1):
        # rx, ry
        return r * np.cos(deg2rad(a1)), r * np.sin(deg2rad(a1))

    # position of distal joint (base joint of finger) in motor frame
    @property
    def left_finger_pos(self): 
        return self.r_a1_to_rx_ry(self.left_finger_dist, self.left_a1)

    @property
    def right_finger_pos(self): 
        return self.r_a1_to_rx_ry(self.right_finger_dist, self.right_a1)

    # a3: angle between distal link (L2) and vector from origin to distal joint
    # forward kinematics function: r distance to a3 angle
    def r_to_a3(self, r):
        return rad2deg(np.arccos((self.geometry_l1**2 - self.geometry_l2**2 - r**2)/(-2 * self.geometry_l2 * r)))

    @property
    def left_a3(self):
        return self.r_to_a3(self.left_finger_dist)

    @property
    def right_a3(self):
        return self.r_to_a3(self.right_finger_dist)

    # phi: angle of finger surface relative to x axis
    # forward kinematics function: link angles to phi angle
    def link_to_phi(self, l0, l1, finger):
        a1 = self.link_to_a1(l0,l1)
        r = self.a2_to_r(self.link_to_a2(l0,l1))
        a3 = self.r_to_a3(r)
        if finger == 'L':
            return self.a1a3_to_L_phi(a1,a3)
        elif finger == 'R':
            return self.a1a3_to_R_phi(a1,a3)
    
    # forward kinematics function: a1, a3 angles to finger phi angle
    def a1a3_to_L_phi(self, a1, a3):
        return a1 + a3 + self.geometry_beta - 180
    def a1a3_to_R_phi(self, a1, a3):
        return a1 - (a3 + self.geometry_beta - 180)

    @property
    def left_phi(self):
        return self.a1a3_to_L_phi(self.left_a1, self.left_a3)

    @property
    def right_phi(self):
        return self.a1a3_to_R_phi(self.right_a1, self.right_a3)

    # position of fingertip in motor frame
    # forward kinematics function: link angles to tip coordinate
    def link_to_tip(self, l0, l1, finger):
        a1 = self.link_to_a1(l0,l1)
        r = self.a2_to_r(self.link_to_a2(l0,l1))
        a3 = self.r_to_a3(r)
        rxry = self.r_a1_to_rx_ry(r, a1)
        return self.a1a3rxy_to_tip(a1, a3, rxry, finger)

    # forward kinematics function: a1, a3 angles and joint coordinate to tip coordinate
    def a1a3rxy_to_tip(self, a1, a3, rxry, finger):
        # angle of l3 relative to x axis
        if finger == 'L':
            q_tip = a1 + a3 + self.geometry_gamma - 180
        elif finger == 'R':
            q_tip = a1 - (a3 + self.geometry_gamma - 180)
        x = rxry[0] + self.geometry_l3 * np.cos(deg2rad(q_tip))
        y = rxry[1] + self.geometry_l3 * np.sin(deg2rad(q_tip))
        return x, y

    @property
    def left_tip_pos(self):
        return self.a1a3rxy_to_tip(self.left_a1, self.left_a3, self.left_finger_pos, 'L')

    @property
    def right_tip_pos(self):
        return self.a1a3rxy_to_tip(self.right_a1, self.right_a3, self.right_finger_pos, 'R')

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
