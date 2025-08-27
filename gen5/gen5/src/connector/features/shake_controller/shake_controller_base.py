import abc

from unitelabs.cdk import sila


class ReadInProgressError(sila.DefinedExecutionError):
    """
    This action can not be performed while a read is in progress.
    """


class ExperimentAlreadyOpenError(sila.DefinedExecutionError):
    """
    An experiment is already open. Please (save and) close the current experiment before creating a new one.
    """


class InvalidParameterError(sila.DefinedExecutionError):
    """
    The given parameter is invalid.
    """


class NoActivePlateError(sila.DefinedExecutionError):
    """
    This action can not be performed while there is no plate activated.
    """


class NoActiveShakeError(sila.DefinedExecutionError):
    """
    This action can not be performed while there is no active shake (read).
    """


class ShakeStartError(sila.DefinedExecutionError):
    """
    Unexpected error while starting the shake.
    Please first check the connection to the device.
    """


class ShakeControllerBase(sila.Feature, metaclass=abc.ABCMeta):
    """
    Control shake by setting a target shake that should be reached and held.
    """

    def __init__(self):
        super().__init__(
            originator="io.unitelabs",
            category="shake",
            version="0.1",
            maturity_level="Draft",
        )

    @abc.abstractmethod
    @sila.UnobservableCommand(
        errors=[ReadInProgressError, ExperimentAlreadyOpenError, InvalidParameterError, ShakeStartError]
    )
    async def start_shake_step(self, mode: int, duration_sec: float, displacement_mm: int, orbital_speed: int):
        """
        Start a shake step with the given parameters. This creates a new experiment with only the shake step.
        Any previous experiment has to be closed before calling this method.
        Closing an experiment will discard all unsaved data of the experiment.

        .. parameter:: The mode of the shake step (0: linear, 1: orbital or 2: double orbital).
        .. parameter:: The duration of the shake step in seconds.
        .. parameter:: The displacement of the shake step in millimeters.
        .. parameter:: The orbital speed of the shake step (0: slow, 1: fast). Only for orbital and double orbital mode.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, NoActiveShakeError])
    @sila.Response("Confirmation")
    async def abort_shake(self) -> str:
        """
        Abort the current read step.
        Shaking is considered a read step.
        Is the same as gen5_service.abort_read().

        .. return:: A confirmation message that the read was aborted.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_shake_in_progress(self) -> bool:
        """
        Return True if a read is currently in progress.
        Shaking is considered a read in progress.
        Does the same as gen5_service.get_read_in_progress()
        """
