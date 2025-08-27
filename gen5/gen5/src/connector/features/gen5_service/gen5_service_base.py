import abc

from unitelabs.cdk import sila


class ReadInProgressError(sila.DefinedExecutionError):
    """
    This action can not be performed while a read is in progress.
    """


class PathNotFoundError(sila.DefinedExecutionError):
    """
    The path specified does not exist.
    """


class NoActivePlateError(sila.DefinedExecutionError):
    """
    This action can not be performed while there is no plate activated.
    """


class NoExperimentError(sila.DefinedExecutionError):
    """
    This action can not be performed while there is no experiment open.
    """


class ExperimentAlreadyOpenError(sila.DefinedExecutionError):
    """
    An experiment is already open. Please (save and) close the current experiment before creating a new one.
    """


class NoActiveReadError(sila.DefinedExecutionError):
    """
    This action can not be performed while there is no active read.
    """


class DBError(sila.DefinedExecutionError):
    """
    This feature is not implemented.
    """


class PlateNotFoundError(sila.DefinedExecutionError):
    """
    The plate specified does not exist. Please check the name and try again.
    """


class ReadStartError(sila.DefinedExecutionError):
    """
    Unexpected error while starting the measurement.
    Please first check the connection to the device.
    """


class MethodNotSupportedError(sila.DefinedExecutionError):
    """
    The method is not supported by the connected reader.
    """


class Gen5ServiceBase(sila.Feature, metaclass=abc.ABCMeta):  # pylint: disable=too-many-public-methods
    """A Gen5-specific feature providing access to all low-level commands of the Gen5 OLE API."""

    def __init__(self):
        super().__init__(originator="io.unitelabs", category="gen5", version="1.0", maturity_level="draft")

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_version(self) -> str:
        """Get the version of the installed Gen5 software."""

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_device_connected(self) -> bool:
        """Test the connection to the connected reader device. Returns false if in simulation mode."""

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_plate_types(self) -> list[str]:
        """Return a list of all available plate names."""

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_device_info(self) -> str:
        """
        Return a JSON string with information about the connected device:
            {
                "eAbsorbanceReadSupported": bool,
                "eAbsorbanceWavelengthMin": int,
                "eAbsorbanceWavelengthMax": int,
                "eAbsorbanceReadModeCount": int,
                "eAbsorbanceReadModeName": dict,
                "eTemperatureControlOption": [str],
                "eTemperatureMin": int,
                "eTemperatureMax": int,
                "eTemperatureGradientMax": int,
                "eShakeSupported": bool,
                "eSerialNumber": str,
                "eInstrumentName": str,
                "eFilterFluorescenceSupported": bool,
                "eMonoFluorescenceSupported": bool,
                "eReaderArchitectureLevel": int
            }
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_reader_status(self) -> str:
        """
        Return the status of the reader.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[PathNotFoundError, DBError])
    async def get_available_protocols(self) -> list[str]:
        """Return a list of available protocols."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[ExperimentAlreadyOpenError])
    async def new_experiment(self, protocol: str) -> None:
        """
        Create a new experiment.

        .. parameter:: The name of the protocol (must be available in the list of available protocols).
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_experiment_open(self) -> bool:
        """Return True if an experiment is currently open."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoExperimentError])
    @sila.Response("Confirmation")
    async def save_experiment(self, path: str, name: str) -> str:
        """
        Save the current experiment to the given path.

        .. parameter:: The path to save the experiment to.
        .. parameter:: The file name of the experiment.

        .. return:: A confirmation message.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoExperimentError])
    async def close_experiment(self) -> str:
        """
        Close the current experiment without saving.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError, NoExperimentError])
    async def get_plate_layout(self) -> str:
        """
        Returns the layout of the plate in a  BTIPlateLayout XML format.

        Only supports not paneled experiments
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, NoExperimentError])
    async def set_plate_layout(self, layout: str) -> None:
        """
        Set the layout of the plate.

        .. parameter:: The layout of the plate in a BTIPlateLayout XML format.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_protocol_path(self) -> str:
        """Return the path of the protocol folder."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[PathNotFoundError])
    async def set_protocol_path(self, path: str) -> None:
        """
        Sets the path to the protocol folder. Doesn't remember if connector is restarted.

        .. parameter:: The absolute path where the .prt files are located.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoExperimentError])
    async def get_plate_list(self) -> list[str]:
        """A list of names of available plates."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoExperimentError, PlateNotFoundError])
    async def activate_plate(self, plate_name: str) -> None:
        """
        Activate a plate for the current experiment.

        .. parameter:: The name of the plate to activate (must be in the list of available plates).
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def deactivate_plate(self) -> None:
        """Deactivate the currently active plate."""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_active_plate(self) -> str:
        """Return the name of the currently active plate."""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def delete_active_plate(self) -> None:
        """Delete the currently active plate. (Not deactivating, deletes plate and all data!)"""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_procedure(self) -> str:
        """Return the current procedure."""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_modifiable_procedure(self) -> str:
        """Return the part of the current procedure, which can be modified."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, ReadInProgressError])
    async def set_procedure(self, procedure: str) -> None:
        """
        Set the procedure for the current experiment.

        .. parameter:: The procedure to set.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, ReadInProgressError])
    async def set_modifiable_procedure(self, procedure: str) -> None:
        """
        Set the modifiable part of the procedure.

        .. parameter:: The modifiable part of the procedure to set.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, ReadInProgressError, MethodNotSupportedError])
    @sila.Response("Validation Status")
    @sila.Response("Validation Message")
    async def validate_procedure(self, flip: bool) -> tuple[int, str]:
        """
        Validate the current procedure.

        .. parameter:: Whether to flip the plate for validation.

        .. return:: A validation status (1: OK, any other number: Error Code).
        .. return:: A validation message.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, ReadInProgressError, ReadStartError])
    async def start_read(self) -> None:
        """
        Start reading the active plate.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, NoActiveReadError])
    async def resume_read(self) -> None:
        """
        Resume the current read.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError, NoActiveReadError])
    @sila.Response("Confirmation")
    async def abort_read(self) -> str:
        """
        Abort the current read.

        .. return:: A confirmation message that the read was aborted.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_read_status(self) -> int:
        """
        Return the status of the current read.

        0: Not started
        1: In progress
        2: Aborted
        3: Paused
        4: Error
        5: Completed
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_plate_calibration_type(self) -> str:
        """
        Return the calibration type of the active plate.
        Can be either Standard Plate (0) or Calibration Plate (1)
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_sample_count(self) -> int:
        """
        Return the number of samples assigned to the current plate. This property only applies to experiments based
        on Custom or Open Protocols.

        Note: This property is not applicable to panels that have unique samples for each protocol.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_row_count(self) -> int:
        """Return the number of rows in the active plate."""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_column_count(self) -> int:
        """Return the number of columns in the active plate."""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_plate_is_labware(self) -> bool:
        """Return True if the active plate is labware."""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_vessel_count(self) -> int:
        """
        Returns the number of vessels for the current plate type.
        If the plate is not labware the vessel count = 1.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_data_set_names(self) -> list[str]:
        """Return a list of available data set names."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[NoActivePlateError])
    @sila.Response("Data")
    async def get_plate_data(self) -> str:
        """
        Return the topmost entry in the data stack. Must be called more than once to retrieve all data.

        .. return:: A json (string) of the data:
            {
                "str dataset_name (f.ex. wavelength)": {
                    "row": [[int]]; An array of longs (int) containing the row (0-based) of the current read,
                    "column": [[int]]; An array of longs (int) containing the column (0-based) of the current read,
                    "value": [[float]]; An array of doubles (float) containing the value of the current read,
                    "kineticIndex": [[int]]; An array of longs (int) containing the kinetic index (0-based) of the
                        current read,
                    "wavelengthIndex": [[int]]; An array of longs (int) containing the spectrum wavelength index
                        (0-based) of the current read,
                    "horizontalIndex": [[int]]; An array of longs (int) containing the horizontal index (0-based) of
                        the current read,
                    "verticalIndex": [[int]]; An array of longs (int) containing the vertical index (0-based) of the
                        current read,
                    "primaryStatus": [[int]]; An array of longs (int) containing the primary status of the current read,
                        (
                            0: The well was successfully read,
                            1: The well data was outside the reader's range,
                            2: The reader was not able to capture the well data,
                            3: The well was masked (read from file only),
                            4: An error was encountered reading the well,
                            5: The well was not read
                        )
                    "secondaryStatus": [[int]]; An array of longs (int) containing the secondary status of the current
                        read,
                        (
                            0: There are no secondary status conditions,
                            1: The well was being dispensed with injector 1 during the read,
                            2: The well was being dispensed with injector 2 during the read,
                            3: The well was being dispensed with injector 3 during the read,
                            4: The well was being dispensed with injector 4 during the read
                        )
                },
                # for example:
                "600": {
                    "row": [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
                    "column": [[0, 1, 2], [0, 1, 2], [0, 1, 2]],
                    "value": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
                    ...
                }
                # in addition:
                "current_data_status": int (0: No raw data is currently available, 1: Raw data was found. More data is
                    available., 2: Raw data was found. No additional data is currently available.),
            }
        """

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_sample_description(self) -> str:
        """Return a dictionary with the sample description."""

    @abc.abstractmethod
    @sila.UnobservableProperty(errors=[NoActivePlateError])
    async def get_image_folder_path(self) -> list[str]:
        """Returns the count and the list of image folders that apply to the current plate."""

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def get_read_in_progress(self) -> bool:
        """Return True if a read is currently in progress."""
