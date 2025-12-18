"""Duplicate this file and add/modify the missing parts to create new processes."""

from lab_adaption.processes.basic_process import BasicProcess
from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401


# todo change process name
class MyProcess(BasicProcess):
    """Example process to be modified."""

    def __init__(self):
        # todo change platenumber and name
        super().__init__(
            # priority=5,  # noqa: ERA001
            num_plates=4,
            process_name="MyProcess",
        )

    def create_resources(self) -> None:
        """Define additional resources needed for the process.

        Implement this method if you need additional resources beyond the ones defined in BasicProcess.
        """
        super().create_resources()
        # todo create additional reagents
        # self.lysate = ReagentResource(proc=self, name=f"Lysate", filled=True, outside_cost=20, priority=10) #noqa: ERA001 E501

    def init_service_resources(self) -> None:
        """Sets the starting position of containers.

        You can change the starting position. default is the first [num_plates] slots in Hotel1
        """
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i)
        # self.lysate.set_start_position(self.hotel2, 11) # noqa: ERA001

    def process(self) -> None:
        """Define the experimental workflow here."""
