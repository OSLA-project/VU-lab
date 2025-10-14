from laborchestrator.structures import ProcessStep, ContainerInfo
from laborchestrator.engine.worker_interface import Observable

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
    # Go home
    # Start shaking
    # Stop shaking
    # Start shaking runtime
