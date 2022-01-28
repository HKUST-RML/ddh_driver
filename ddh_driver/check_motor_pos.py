import time
from .gripper import Gripper

if __name__ == '__main__':
    gripper = Gripper('default')
    print('------------------------------')
    print('Press ENTER to take a snapshot')
    print('------------------------------')
    while True:
        time.sleep(1./100.)
        print('R0: {0:.5f}, R1: {1:.5f}, L0: {2:.5f}, L1: {3:.5f}'.format(gripper.R0.motor_pos, gripper.R1.motor_pos, gripper.L0.motor_pos, gripper.L1.motor_pos), end="\r")
