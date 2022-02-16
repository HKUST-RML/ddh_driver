import time
from ddh_driver.gripper import Gripper
from ddh_driver.lsl_streamer import LslStreamer

if __name__ == '__main__':
    gripper = Gripper('default')
    gripper.arm()
    stream = LslStreamer(gripper)
    stream.enabled = True
