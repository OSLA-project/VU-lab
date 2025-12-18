from __future__ import annotations
import time
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from laborchestrator.engine.worker_interface import Observable
    from laborchestrator.structures import ContainerInfo
    from laborchestrator.structures import ProcessStep
    from sila2.client import SilaClient


class DeviceInterface(ABC):
    """Abstract base class for all device wrappers in the VU lab laborchestrator."""

    @staticmethod
    @abstractmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: SilaClient,
        **kwargs: dict[str, Any],
    ) -> Observable:
        """Provides an Observable(, i.e., ClientObservableCommandInstance or ObservableProtocolHandler which emulates
        a ClientObservableCommandInstance),
        for the specified function on this device which
        provides functions to enquiry the status and remaining time of this protocol.

        :param sila_client:
        :param step:
        :param cont:
        :return: An ObservableProtocolHandler or ClientObservableCommandInstance.
        """


def finish_observable_command(cmd: Observable) -> None:
    """Utility function that waits until the command finishes.

    :param cmd:
    :return:
    """
    while not cmd.done:
        time.sleep(0.1)
