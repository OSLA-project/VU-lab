from abc import ABC

from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.human import HumanServiceResource
from pythonlab.resources.services.hello_world import GreeterServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
from pythonlab.resource import LabwareResource

# TODO: add whatever resources you need
from pythonlab.process import PLProcess


class BasicProcess(PLProcess, ABC):
    def __init__(
        self, process_name: str, num_plates: int = 0, priority=7
    ):  # 0 has highest priority
        self.num_mw_plates = num_plates
        self.name = process_name

        super().__init__(priority=priority)

    def create_resources(self):
        # the device names should match the ones in the platform_config
        self.hotel1 = LabwareStorageResource(proc=self, name="Hotel1")
        self.hotel2 = LabwareStorageResource(proc=self, name="Hotel2")
        self.hotel3 = LabwareStorageResource(proc=self, name="Hotel3")
        self.robot_arm = MoverServiceResource(proc=self, name="GenericArm")
        self.human = HumanServiceResource(proc=self, name="Human")
        self.greeter = GreeterServiceResource(proc=self, name="Greeter")
        # TODO: add your resources here with names matching the platform_config

        # the continers are automatically named/enumerated. You can change the naming without causing problems
        self.containers = [
            LabwareResource(
                proc=self, name=f"{self.name}_cont_{cont}", lidded=True, filled=False
            )
            for cont in range(self.num_mw_plates)
        ]

    def process(self):
        raise NotImplementedError
