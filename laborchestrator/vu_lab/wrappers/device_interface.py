from __future__ import annotations
from abc import ABC, abstractmethod
from laborchestrator.structures import ProcessStep, ContainerInfo
from laborchestrator.engine.worker_interface import Observable
from sila2.client import SilaClient
import time


class DeviceInterface(ABC):
    @staticmethod
    @abstractmethod
    def get_SiLA_handler(
        step: ProcessStep, cont: ContainerInfo, sila_client: SilaClient, **kwargs
    ) -> Observable:
        """
        Provides an Observable(, i.e., ClientObservableCommandInstance or ObservableProtocolHandler which emulates
        a ClientObservableCommandInstance),
        for the specified function on this device which
        provides functions to enquiry the status and remaining time of this protocol
        :param sila_client:
        :param step:
        :param cont:
        :return: An ObservableProtocolHandler or ClientObservableCommandInstance
        """


def finish_observable_command(cmd: Observable):
    """
    Utility function that waits until the command finishes
    :param cmd:
    :return:
    """
    while not cmd.done:
        time.sleep(0.1)
