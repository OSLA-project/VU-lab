import logging
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.engine.worker_interface import ObservableProtocolHandler
from laborchestrator.structures import ContainerInfo
from laborchestrator.structures import MoveStep
from .device_interface import DeviceInterface
from .device_interface import finish_observable_command

logger = logging.getLogger(__name__)

try:
    from genericroboticarm.sila_server import Client as ArmClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as ArmClient

    logger.warning("Generic robotic arm seems to be not installed")


class GenericRobotArmWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: MoveStep,
        cont: ContainerInfo,
        sila_client: ArmClient,
        intermediate_actions: list[str] | None = None,
        **kwargs,
    ) -> Observable:
        if intermediate_actions is None:
            intermediate_actions = []

        origin_site = (cont.current_device, cont.current_pos)
        target_site = (step.target_device.name, step.destination_pos)
        if not intermediate_actions:
            return sila_client.RobotController.MovePlate(origin_site, target_site)

        # with intermediate actions we need to use the standard sila labware transfer feature

        class TransferHandler(ObservableProtocolHandler):
            def _protocol(self, client: ArmClient, **kwargs) -> None:
                pick_cmd = client.LabwareTransferManipulatorController.GetLabware(
                    HandoverPosition=(
                        cont.current_device,
                        cont.current_pos + 1,
                    ),  # counting start at 1 there
                    IntermediateActions=intermediate_actions,
                )
                finish_observable_command(pick_cmd)
                # PlacePlate is blocking and not observable
                client.RobotController.PlacePlate(target_site)

        observable = TransferHandler()
        logger.info("Starting transfer with intermediate actions: %s", intermediate_actions)
        # starts _protocol and handles the status
        observable.run_protocol(sila_client)
        return observable
