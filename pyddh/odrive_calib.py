import time

import odrive
from odrive.enums import *
import fibre
from odrive.configuration import *
import dpath.util as dpath
from .utils import *

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


def print_encoder_reading(od):
    while True:
        time.sleep(0.1)
        print(od.axis0.encoder)

if __name__ == '__main__':
    config = load_ddh_config('test_calib')
    odrive_serial_R = dpath.get(config, 'odrive_serial/R')
    odrive_serial_L = dpath.get(config, 'odrive_serial/L')
    od_R = odrive.find_any(serial_number=odrive_serial_R)
    print_encoder_reading(od_R)
    #init_odrive(odrive_serial_R)

    # odrive_R.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    # while odrive_R.axis0.current_state > AXIS_STATE_IDLE or odrive_R.axis0.requested_state == AXIS_STATE_FULL_CALIBRATION_SEQUENCE:
    #      time.sleep(0.1)
    # print('stoppped')
    # print(odrive_R.axis0.error)
