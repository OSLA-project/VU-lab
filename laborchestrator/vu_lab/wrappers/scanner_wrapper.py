from laborchestrator.structures import ProcessStep, ContainerInfo
from laborchestrator.engine.worker_interface import Observable

from vu_lab.wrappers import DeviceInterface

from sila2.client import SilaClient as ScannerClient


class ScannerWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: ScannerClient,
        **kwargs,
    ) -> Observable:
        pass

    # Start scanning
    # Stop scanning
    # Start scan runtime

    def start_scan(
        self,
        client: ScannerClient,
        resolution: int,
    ) -> Observable:
        """
        Start scanning with the specified mode, duration, and displacement.
        :param client: SiLA client for the shaker device
        :param resolution: The scanner resolution.
        """

        return client.ScanController.start_scan_step(resolution)

    def abort_scan(self, client: ScannerClient) -> Observable:

        return client.ScanController.abort_shake()
