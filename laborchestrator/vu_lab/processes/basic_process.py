from abc import ABC  # noqa: I001
from typing import Never

from pythonlab.process import PLProcess
from pythonlab.resource import LabwareResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.shaker import ShakerServiceResource


class BasicProcess(PLProcess, ABC):
    """Contains the basic setup for a process with the available devices in the VU lab."""

    def __init__(
        self,
        process_name: str,
        num_plates: int = 0,
        priority: int = 7,
    ):  # 0 has highest priority
        self.num_mw_plates = num_plates
        self.name = process_name

        super().__init__(priority=priority)

    def create_resources(self) -> None:
        """Define the available labware and devices in the process."""
        # the device names should match the ones in the platform_config
        self.hotel1 = LabwareStorageResource(proc=self, name="hotel_1_d_pos_")
        self.robot_arm = MoverServiceResource(proc=self, name="robot_arm")
        self.shaker1 = ShakerServiceResource(proc=self, name="shaker_1_d_pos_1")
        self.shaker2 = ShakerServiceResource(proc=self, name="shaker_2_d_pos_1")
        self.shaker3 = ShakerServiceResource(proc=self, name="shaker_3_d_pos_1")
        self.shaker4 = ShakerServiceResource(proc=self, name="shaker_4_d_pos_1")
        self.shaker5 = ShakerServiceResource(proc=self, name="shaker_5_d_pos_1")
        self.shaker6 = ShakerServiceResource(proc=self, name="shaker_6_d_pos_1")

        self.shaker_pool = ShakerServiceResource(proc=self, name=None)

        # the containers are automatically named/enumerated. You can change the naming without causing problems
        self.containers = [
            LabwareResource(
                proc=self,
                name=f"{self.name}_container_{cont}",
                lidded=False,
                filled=False,
            )
            for cont in range(self.num_mw_plates)
        ]

    def process(self) -> Never:
        """Workflow to be implemented by subclasses."""
        raise NotImplementedError
