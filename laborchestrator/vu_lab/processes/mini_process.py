from vu_lab.processes.basic_process import BasicProcess


class MiniProcess(BasicProcess):

    def __init__(self):
        # There is only one container in this mini process
        super().__init__(process_name="Mini Process", num_plates=1, priority=5)


    def init_service_resources(self):
        """ Put the one and only container at position 1 in hotel1 """
        super().init_service_resources()

        self.container = self.containers[0]
        self.container.set_start_position(self.hotel1, 1)

    def process(self) -> None:
        """Move the container from hotel1 position 1 to position 8 and back."""
        self.robot_arm.move(self.container, self.hotel1, position=7)
        self.robot_arm.move(self.container, self.hotel1, position=1)
