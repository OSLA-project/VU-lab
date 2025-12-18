from laborchestrator.engine.worker_interface import Observable
from laborchestrator.structures import ContainerInfo
from laborchestrator.structures import ProcessStep
from vu_lab.wrappers import DeviceInterface

try:
    from sila2_driver.thermoscientific.teleshake1536 import Client as ShakerClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as ShakerClient


class ShakerWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: ShakerClient,
        **kwargs,
    ) -> Observable:
        pass

    # Start shaking
    # Stop shaking
    # Start shaking runtime

    def start_shake(self, client: ShakerClient, mode: int, duration: float, displacement: float) -> Observable:
        """Start shaking with the specified mode, duration, and displacement.
        :param client: SiLA client for the shaker device
        :param mode: The mode of the shake step (0: linear, 1: orbital or 2: double orbital)
        :param duration: Duration of shaking in seconds
        :param displacement: Displacement value for shaking in mm.

        """
        return client.ShakeController.start_shake_step(mode, duration, displacement)

    def abort_shake(self, client: ShakerClient) -> Observable:
        return client.ShakeController.abort_shake()
