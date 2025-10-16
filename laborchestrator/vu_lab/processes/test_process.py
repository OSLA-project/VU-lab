"""Duplicate this file and add/modify the missing parts to create new processes
"""
from pythonlab.resources.services.shaker import ShakerServiceResource

from .basic_process import BasicProcess
from ..wrappers.shaker_wrapper import ShakerWrapper

DURATION = 10
FREQUENCY = 10

class VUTestProcess(BasicProcess):
    def __init__(self):
        super().__init__(priority=3, num_plates=3, process_name="Vu Test Process")

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i)

    def process(self):
        # loop through all containers
        for idx, cont in enumerate(self.containers):
            shaker: ShakerServiceResource = self.shaker1 if idx % 2 == 0 else self.shaker2

            # Move all containers to shaker
            self.robot_arm.move(cont, shaker)
            shaker.shake_plate(cont, DURATION, FREQUENCY)
            self.robot_arm.move(cont, self.hotel2)

