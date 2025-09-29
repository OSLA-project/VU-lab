""" """

import logging
from random import randint
from typing import Any
from typing import NamedTuple
from typing import Optional
from laborchestrator.database_integration import StatusDBInterface
from laborchestrator.engine import ScheduleManager
from laborchestrator.engine.worker_interface import DummyHandler
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.engine.worker_interface import WorkerInterface
from laborchestrator.structures import MoveStep
from laborchestrator.structures import SchedulingInstance
from laborchestrator.structures import SMProcess
from sila2.client import SilaClient
from vu_lab.wrappers import GenericRobotArmWrapper
from vu_lab.wrappers.device_interface import DeviceInterface

# Out comment those you want to simulate the steps instead of calling an actual sila server
USE_REAL_SERVERS = [
    "GenericArm",
]

# maps the device names (from the platform_config and process description) to the correct wrappers
device_wrappers: dict[str, type[DeviceInterface]] = dict(
    GenericArm=GenericRobotArmWrapper,
)

# maps the device names (from the platform_config and process description) to the correct sila server names
# those without a sila server can be left out
sila_server_name: dict[str, str] = dict(
    GenericArm="Dummy",
)


class Worker(WorkerInterface):
    # save the clients for repeated use
    clients: dict[str, SilaClient]

    def __init__(
        self,
        jssp: SchedulingInstance,
        schedule_manager: ScheduleManager,
        db_client: StatusDBInterface,
    ):
        super().__init__(jssp, schedule_manager, db_client)
        self.clients = {}

    def execute_process_step(
        self, step_id: str, device: str, device_kwargs: dict[str, Any],
    ) -> Observable:
        print(f"Execute {step_id} on device {device}")
        # get all information about the process step
        step = self.jssp.step_by_id[step_id]
        cont = self.jssp.container_info_by_name[step.cont_names[0]]
        if device in USE_REAL_SERVERS:
            client = self.get_client(device_name=device)
            if client:
                wrapper = device_wrappers[device]
                # starts the command on the device and returns an Observable
                observable = wrapper.get_SiLA_handler(
                    step, cont, client, **device_kwargs,
                )
                return observable
        # for all simulated devices, this simply wraps a sleep command into an Observable
        # TODO you can change the time to for example step.duration/2
        handler = DummyHandler(randint(2, 12))
        # the protocol will take between 2 and 12 seconds
        handler.run_protocol(None)
        return handler

    def get_client(self, device_name, timeout: float = 5) -> SilaClient | None:
        server_name = sila_server_name.get(device_name)
        if server_name:
            client = self.clients.get(device_name, None)
            if client:
                # check if the server still responds
                try:
                    name = client.SiLAService.ServerName.get()
                    assert name == server_name
                except AssertionError:
                    logging.exception(
                        f"The server on {client.address}:{client.port} has changed its name",
                    )
                except ConnectionError:
                    # the server seems to be offline
                    self.clients.pop(device_name)
            # try to discover the matching server by its server name
            try:
                client = SilaClient.discover(
                    server_name=server_name, insecure=True, timeout=timeout,
                )
                self.clients[device_name] = client
                return client
            except TimeoutError as error:
                logging.exception(f"Could not connect to {server_name}:\n{error}")
        return None

    def process_step_finished(self, step_id: str, result: Optional[NamedTuple]):
        # get all information about the process step
        step = self.jssp.step_by_id[step_id]
        container = self.jssp.container_info_by_name[step.cont]
        # TODO: Insert custom thing to do after finishing a step.
        # custom kwargs given to steps (see mover_test for example) are also available in step.data
        if "read_barcode" in step.data:
            # TODO: Insert you own way to retrieve a barcode from a barcode reader
            container.barcode = f"Nice_Barcode{randint(1, 9999)}"
            # saves the barcode to the database.
            self.db_client.set_barcode(container)
        super().process_step_finished(step_id, result)

    def check_prerequisites(self, process: SMProcess) -> tuple[bool, str]:
        # TODO implement your custom checks here.
        # For example whether need protocols exists or all devices are online
        return True, "Nothing to report."

    def determine_destination_position(self, step: MoveStep) -> int | None:
        # TODO change this to  customized positioning if necessary

        # checks the database for the free position with the lowest index
        return super().determine_destination_position(step)
