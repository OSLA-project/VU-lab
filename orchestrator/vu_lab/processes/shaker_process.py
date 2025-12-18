"""Duplicate this file and add/modify the missing parts to create new processes."""

from vu_lab.processes.basic_process import BasicProcess

DURATION = 10
FREQUENCY = 10
NUM_PLATES = 6
PRIORITY = 3


class ShakerProcess(BasicProcess):
    """A simple test process that moves plates to shakers, shakes them, and returns them to  the hotel."""

    def __init__(
        self,
        priority: int = PRIORITY,
        num_plates: int = NUM_PLATES,
        duration: float = DURATION,
        frequency: float = FREQUENCY,
    ):
        super().__init__(priority=priority, num_plates=num_plates, process_name="Vu Test Process")
        self.duration = duration
        self.frequency = frequency

    def init_service_resources(self) -> None:
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i + 1)

    def process(self) -> None:
        # loop through all containers
        for idx in range(self.num_mw_plates):
            cont = self.containers[idx]

            # Move all containers to shaker
            self.robot_arm.move(cont, self.shaker_pool)
            self.shaker_pool.shake_plate(cont, self.duration, self.frequency)
            self.robot_arm.move(cont, self.hotel1)
