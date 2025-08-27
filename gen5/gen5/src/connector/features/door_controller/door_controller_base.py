import abc
from unitelabs.cdk import sila


class ReadInProgressError(sila.DefinedExecutionError):
    """
    This action can not be performed while a read is in progress.
    """


class DoorControllerBase(sila.Feature, metaclass=abc.ABCMeta):
    """
    Controls the carrier and door of a device and provides functions to monitor its state. Devices include plate readers
    and thermocyclers.
    """

    def __init__(self):
        super().__init__(
            originator="io.unitelabs",
            category="examples",
            version="0.1",
            maturity_level="Draft",
        )

    @abc.abstractmethod
    @sila.ObservableProperty()
    async def subscribe_door_open(self) -> sila.Stream[bool]:
        """
        Subscribe to the state of the door.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_door_open_once(self) -> bool:
        """
        Retrieve the door state once.
        """

    @abc.abstractmethod
    @sila.ObservableCommand(errors=[ReadInProgressError])
    @sila.IntermediateResponse(name="Process status")
    @sila.Response(name="Door open")
    @sila.Response(name="End of process status")
    async def open_door(self, *, status: sila.Status, intermediate: sila.Intermediate[str]) -> tuple[bool, str]:
        """
        The abstract method to open the door.

        .. yield:: The current status of the door opening process as a string.

        .. return:: The state of the door where true means open.
        .. return:: The end status of the door as a string.
        """

    @abc.abstractmethod
    @sila.ObservableCommand(errors=[ReadInProgressError])
    @sila.IntermediateResponse(name="Process status")
    @sila.Response(name="Door Open")
    @sila.Response(name="End of process status")
    async def close_door(self, *, status: sila.Status, intermediate: sila.Intermediate[str]) -> tuple[bool, str]:
        """
        The abstract method to close the door.

        .. yield:: The current status of the door opening process as a string.

        .. return:: The state of the door where true means open.
        .. return:: The end status of the door as a string.
        """


class DoorMalfunctionError(sila.DefinedExecutionError):
    """
    A hardware malfunction was detected, and the called door method cannot be completed.
    Please manually check the device and refer to the device manual for reparation instructions.
    """
