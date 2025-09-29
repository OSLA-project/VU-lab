"""Duplicate this file and add/modify the missing parts to create new processes
"""

from .basic_process import BasicProcess


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
        for cont in self.containers:
            # move all containers to hotel2 and read their barcodes
            self.robot_arm.move(cont, self.hotel2)
            # move all containers to the human for inspection (it can hold up to two)
            self.robot_arm.move(cont, self.hotel1)
