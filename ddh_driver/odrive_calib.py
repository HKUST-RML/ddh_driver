import time

import odrive
from odrive.enums import *
import fibre
from odrive.configuration import *
import dpath.util as dpath
from ddh_driver.utils import *

logger = fibre.Logger(verbose=False)


def reset_odrive_config(sn):
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
    print('YOUR ACTION REQUIRED: Power off ODrive completely, make sure the green lights on the ODrive boards are off too.')
    try:
        while od.axis0.current_state >= 0:
            time.sleep(0.1)
    except Exception as e:
        print('Lost connection, do not power back on yet, wait a few more seconds...')
    time.sleep(3)
    print('YOUR ACTION REQUIRED: Now power back on!')
    od = odrive.find_any(serial_number=sn)
    print('Reconnected!')


def calibrate_axis(axis, od_name, ax_name):
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
            print('Axis %s%s calibrated' % (od_name, ax_name))
            axis.motor.config.pre_calibrated = True
            axis.encoder.config.pre_calibrated = True
    else:
        print('Axis %s%s pre_calibrated' % (od_name, ax_name))


def calibrate_motors(sn, od_name):
    od = odrive.find_any(serial_number=sn)
    calibrate_axis(od.axis0, od_name, '0')
    calibrate_axis(od.axis1, od_name, '1')
    od.save_configuration()
    try:
        od.reboot()
    except fibre.ObjectLostError:
        print('ODrive rebooted!')


def arm_motors(sn):
    od = odrive.find_any(serial_number=sn)
    print('Warming Up')
    time.sleep(3)
    print('Arm Motors')
    od.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    od.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    print('The motors should be stiff')


def print_encoder_reading(sn):
    od = odrive.find_any(serial_number=sn)
    while True:
        time.sleep(0.1)
        print(od.axis0.encoder)


def need_calibration(sn, name):
    od = odrive.find_any(serial_number=sn)
    if od.axis0.motor.config.pre_calibrated and od.axis1.motor.config.pre_calibrated and od.axis0.encoder.config.pre_calibrated and od.axis1.encoder.config.pre_calibrated:
        ans = input('ODrive_%s seems already calibrated, calibrate anyway? (y/n)' % name)
        return len(ans) == 0 or ans == 'y' or ans == 'Y'
    else:
        return True


def calibrate_odrive(sn, name):
    if need_calibration(sn, name):
        reset_odrive_config(sn)
        ask_for_reboot(sn)
        calibrate_motors(sn, name)
        ask_for_reboot(sn)
        arm_motors(sn)
    else:
        print('Calibration Skipped')


if __name__ == '__main__':
    config = load_ddh_config('default')
    SN_R = dpath.get(config, 'odrive_serial/R')
    SN_L = dpath.get(config, 'odrive_serial/L')
    calibrate_odrive(SN_R, 'R')
    calibrate_odrive(SN_L, 'L')
    print('ODrive Calibration Complete!')
