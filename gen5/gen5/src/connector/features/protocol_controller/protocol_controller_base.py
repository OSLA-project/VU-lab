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


class NoExperimentError(sila.DefinedExecutionError):
    """
    This action can not be performed while there is no experiment open.
    """


class ProtocolControllerBase(sila.Feature, metaclass=abc.ABCMeta):
    """
    Control shake by setting a target shake that should be reached and held.
    """

    def __init__(self):
        super().__init__(
            originator="io.unitelabs",
            category="gen5",
            version="0.1",
            maturity_level="Draft",
        )

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[ReadInProgressError, ExperimentAlreadyOpenError])
    async def initialize_empty_protocol(self):
        """
        Initializes an empty protocol.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_step_list(self) -> list[str]:
        """
        Returns the list of steps in the current protocol.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    @sila.Response("Step Information")
    async def get_step(self, index: int) -> str:
        """
        Returns the step at the given index.

        .. parameter:: The index of the step to return.

        .. return:: The step at the given index.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    async def delete_step(self, index: int):
        """
        Deletes the step at the given index.

        .. parameter:: The index of the step to delete.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    async def add_absorbance_step(self, index: int, wavelengths: str, read_speed: int, wavelength_switching: bool):
        """
        Start an absorbance step with the given parameters. This creates a new experiment with only the absorbance step.
        Any previous experiment has to be closed before calling this method.
        Closing an experiment will discard all unsaved data of the experiment.

        .. parameter:: The index of the absorbance step.
        .. parameter:: Wavelegth(s) to measure. For multiple wavelengths, use comma separated values.
        .. parameter:: The speed of the read step (0: normal, 1: sweep).
        .. parameter:: Whether to switch wavelengths per well. Only if multiple wavelengths are provided.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    async def add_shake_step(
        self, index: int, mode: int, duration_sec: float, displacement_mm: int, orbital_speed: int
    ):
        """
        Start a shake step with the given parameters. This creates a new experiment with only the shake step.
        Any previous experiment has to be closed before calling this method.
        Closing an experiment will discard all unsaved data of the experiment.

        .. parameter:: The index of the shake step.
        .. parameter:: The mode of the shake step (0: linear, 1: orbital or 2: double orbital).
        .. parameter:: The duration of the shake step in seconds.
        .. parameter:: The displacement of the shake step in millimetres.
        .. parameter:: The orbital speed of the shake step (0: slow, 1: fast). Only for orbital and double orbital mode.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_plate_type(self) -> str:
        """
        Returns the type of the plate.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_supported_plate_types(self) -> list[str]:
        """
        Returns the supported plate types.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    async def set_plate_type(self, plate_type: str, use_lid: bool):
        """
        Sets the type of the plate.

        .. parameter:: The type of the plate. This has to be one of the supported plate types.
        """
