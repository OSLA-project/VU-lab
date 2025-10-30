"""Duplicate this file and add/modify the missing parts to create new processes
"""
from pythonlab.resources.services.shaker import ShakerServiceResource

from vu_lab.processes.basic_process import BasicProcess
from vu_lab.wrappers.shaker_wrapper import ShakerWrapper

DURATION = 10
FREQUENCY = 10

class VUTestProcess(BasicProcess):
    def __init__(self):
        super().__init__(priority=3, num_plates=3, process_name="Vu Test Process")
        self.duration = DURATION
        self.frequency = FREQUENCY

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i+1)

    def process(self):
        # loop through all containers
        for idx in range(self.num_mw_plates):
            cont = self.containers[idx]

            shaker_idx = idx % len(self.shakers)

            # Move all containers to shaker
            self.robot_arm.move(cont, self.shakers[shaker_idx])
            self.shakers[shaker_idx].shake_plate(cont, self.duration, self.frequency)
            self.robot_arm.move(cont, self.hotel1)

