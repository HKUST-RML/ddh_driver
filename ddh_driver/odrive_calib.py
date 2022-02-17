import time

import odrive
from odrive.enums import *
import fibre
from odrive.configuration import *
import dpath.util as dpath
from ddh_driver.utils import *

logger = fibre.Logger(verbose=False)


def init_odrive(sn):
    od = odrive.find_any(serial_number=sn)
    try:
        od.erase_configuration()
    except fibre.ObjectLostError:
        print('ODrive disconnected!')
    od = odrive.find_any(serial_number=sn)
    print('connected again')
    odrive_config_path = get_abs_path('odrive_config/GB54-2.json')
    print(odrive_config_path)
    restore_config(od, odrive_config_path, logger)
    od.save_configuration()
    try:
        od.reboot()
    except fibre.ObjectLostError:
        print('ODrive rebooted!')


def ask_for_reboot(sn):
    od = odrive.find_any(serial_number=sn)
    print('Power off ODrive completely, make sure the green lights on the ODrive boards are off too.')
    try:
        while od.axis0.current_state >= 0:
            time.sleep(0.1)
    except Exception as e:
        print('Lost connection, do not power back on yet, wait a few more seconds...')
    time.sleep(3)
    print('Now power back on!')
    od = odrive.find_any(serial_number=sn)
    print('Reconnected!')


def calib_axis(axis, od_name, ax_name):
    if not axis.motor.config.pre_calibrated:
        print('Axis %s%s not pre_calibrated' % (od_name, ax_name))
        axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        while axis.requested_state is AXIS_STATE_FULL_CALIBRATION_SEQUENCE or axis.current_state > AXIS_STATE_IDLE:
            time.sleep(0.1)
            print('Calibrating...', end="\r")
        axis.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
        while axis.requested_state is AXIS_STATE_FULL_CALIBRATION_SEQUENCE or axis.current_state > AXIS_STATE_IDLE:
            time.sleep(0.1)
            print('Calibrating...', end="\r")
        if axis.motor.is_calibrated and axis.encoder.is_ready:
            axis.motor.config.pre_calibrated = True
            axis.encoder.config.pre_calibrated = True
    else:
        print('Axis %s%s pre_calibrated' % (od_name, ax_name))


def calib_odrive(sn, od_name):
    od = odrive.find_any(serial_number=sn)
    calib_axis(od.axis0, od_name, '0')
    calib_axis(od.axis1, od_name, '1')
    od.save_configuration()
    try:
        od.reboot()
    except fibre.ObjectLostError:
        print('ODrive rebooted!')


def arm_motors(sn):
    od = odrive.find_any(serial_number=sn)
    od.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    od.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL


def print_encoder_reading(sn):
    od = odrive.find_any(serial_number=sn)
    while True:
        time.sleep(0.1)
        print(od.axis0.encoder)


if __name__ == '__main__':
    config = load_ddh_config('default')
    SN_R = dpath.get(config, 'odrive_serial/R')
    SN_L = dpath.get(config, 'odrive_serial/L')
    ask_for_reboot(SN_R)
    #init_odrive(SN_R)
    #calib_odrive(SN_R, 'R')
    #arm_motors(SN_R)

    # odrive_R.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    # while odrive_R.axis0.current_state > AXIS_STATE_IDLE or odrive_R.axis0.requested_state == AXIS_STATE_FULL_CALIBRATION_SEQUENCE:
    #      time.sleep(0.1)
    # print('stoppped')
    # print(odrive_R.axis0.error)
