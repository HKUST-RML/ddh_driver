import threading

import numpy as np
from pylsl import StreamInfo, StreamOutlet, local_clock
import time


class LslStreamer(object):

    def __init__(self, gripper):
        self.gripper = gripper
        self.keep_alive = False
        self.thread = None
        self.hz = 100
        self.info_actuators = self.build_info_actuators()
        self.outlet_actuators = StreamOutlet(self.info_actuators)

    def build_info_actuators(self):
        info = StreamInfo('ddh_actuators', 'data', 12, 100, 'float32', 'ddh')
        channel_names = []
        for actuator in ['R0', 'R1', 'L0', 'L1']:
            channel_names.append(actuator + "_encoder")
            channel_names.append(actuator + "_motor")
            channel_names.append(actuator + "_link")
        # append some meta-data
        info.desc().append_child_value("manufacturer", "LearningRNW")
        channels = info.desc().append_child("channels")
        for label in channel_names:
            ch = channels.append_child("channel")
            ch.append_child_value("label", label)
        info.desc().append_child_value("manufacturer", "LSLExamples")
        cap = info.desc().append_child("cap")
        cap.append_child_value("name", "ComfyCap")
        cap.append_child_value("size", "54")
        cap.append_child_value("labelscheme", "10-20")
        return info

    def thread_body(self):
        while self.keep_alive:
            time.sleep(1./self.hz)
            data = []
            for actuator in self.gripper.actuators:
                data.extend([actuator.encoder, actuator.motor_pos, actuator.theta])
            self.outlet_actuators.push_sample(data)

    @property
    def enabled(self):
        return self.thread is not None

    @enabled.setter
    def enabled(self, enable):
        if enable and not self.enabled:
            self.thread_start()
        if not enable and self.enabled:
            self.thread_stop()

    def thread_start(self):
        self.keep_alive = True
        self.thread = threading.Thread(target=self.thread_body)
        self.thread.start()

    def thread_stop(self):
        self.keep_alive = False
        self.thread.join()
        print('[lsl_streamer] thread terminated')
        self.thread = None
