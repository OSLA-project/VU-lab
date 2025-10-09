from vu_lab.wrappers.device_interface import DeviceInterface
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.engine.worker_interface import ObservableProtocolHandler
from laborchestrator.structures import ContainerInfo, MoveStep
from sila2.client import SilaClient as Gen5Client

class Gen5Wrapper(DeviceInterface):
    def get_SiLA_handler(
            step: MoveStep,
            cont: ContainerInfo,
            sila_client: Gen5Client,
            intermediate_actions: list[str] | None = None,
            **kwargs,
    ) -> Observable:
        if intermediate_actions is None:
            intermediate_actions = []

        class PlateReaderHandler(ObservableProtocolHandler):
            def _protocol(self, client: Gen5Client, **kwargs):
                client.activate_plate(plate_id=cont.name)
                # Activate plate

                # Start read

                # Read status