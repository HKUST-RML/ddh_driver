import time
from .gripper import Gripper

if __name__ == '__main__':
    gripper = Gripper('default')
    print('------------------------------')
    print('Press ENTER to take a snapshot')
    print('------------------------------')
    while True:
        time.sleep(1./100.)
        print('R0: {0:.15f}, R1: {1:.15f}, L0: {2:.15f}, L1: {3:.15f}'.format(gripper.R0.encoder, gripper.R1.encoder, gripper.L0.encoder, gripper.L1.encoder), end="\r")
