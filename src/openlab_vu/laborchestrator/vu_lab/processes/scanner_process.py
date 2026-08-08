"""Duplicate this file and add/modify the missing parts to create new processes"""

from pythonlab.process import PLProcess
from vu_lab.processes.basic_process import BasicProcess
from pythonlab.resource import LabwareResource
from vu_lab.resources.scanner_resource import ScannerResource

DURATION = 10
FREQUENCY = 10
NUM_BEDS = 1
PRIORITY = 3


class ScannerProcess(BasicProcess):
    """A simple test process that moves plates to a scanner, scans them, and returns them to the hotel."""

    def __init__(
        self,
        priority: int = PRIORITY,
        num_beds: int = NUM_BEDS,
        duration: float = DURATION,
        frequency: float = FREQUENCY,
    ):
        super().__init__(
            priority=priority, num_plates=num_beds, process_name="Scanner process"
        )
        self.duration = duration
        self.frequency = frequency

    def init_service_resources(self):
        super().init_service_resources()
        self.container = self.containers[0]
        self.container.set_start_position(self.hotel1, 1)

    def process(self):

        resolution = 640
        # Loop through all containers and scan them
        for idx in range(self.num_mw_plates):
            cont = self.containers[idx]

            # Move all containers to shaker
            self.robot_arm.move(cont, self.scanner1)
            self.scanner1.scan(cont, resolution)
            self.robot_arm.move(cont, self.hotel1)
