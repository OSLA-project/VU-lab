import logging
import typing
from typing import Union
import xml.etree.ElementTree as ET

import asyncio
from pathlib import Path
import os

from unitelabs.cdk import sila, create_logger
from .gen5_simulated_OLE_interface import (
    SimulatedGen5,
    SimulatedExperiment,
    SimulatedPlates,
    SimulatedPlate,
    SimulatedPlateReadMonitor,
    Simulatedwin32com,
    Simulatedpythoncom,
    Simulatedpywintypes,
)

if os.name == "nt":
    import win32com  # pylint: disable=import-error
    import win32com.client  # pylint: disable=import-error
    import pythoncom  # pylint: disable=import-error
    import pywintypes  # pylint: disable=import-error
else:
    win32com = Simulatedwin32com
    pythoncom = Simulatedpythoncom
    pywintypes = Simulatedpywintypes


class UnsupportedPlatformError(Exception):
    """
    This action is not supported on this platform.
    """


# Decorators
def error_on_read_in_progress(func):
    """
    Decorator to raise an error if a read is in progress.
    """

    def wrapper(self, *args, **kwargs):
        try:
            status = self.get_read_status()
        except TypeError:
            status = 0
        if status in (1, 3):
            raise RuntimeError("This action cannot be performed while a read is in progress.")
        return func(self, *args, **kwargs)

    return wrapper


def error_on_missing_active_plate(func):
    """
    Decorator to raise an error if no plate is active.
    """

    def wrapper(self, *args, **kwargs):
        if not self.active_plate:
            if not self.experiment:
                raise TypeError(
                    "None is not a valid active plate. Please make a new experiment and activate a plate before using "
                    "this method."
                )
            raise TypeError("None is not a valid active plate. Please activate a plate before using this method.")
        return func(self, *args, **kwargs)

    return wrapper


def error_on_missing_experiment(func):
    """
    Decorator to raise an error if no experiment is active.
    """

    def wrapper(self, *args, **kwargs):
        if not self.experiment:
            raise TypeError("None is not a valid experiment. Please create a new experiment before continuing.")
        return func(self, *args, **kwargs)

    return wrapper


def error_on_unsupported_temperature_control(func):
    """
    Decorator to raise an error if the temperature control is not supported.
    """

    def wrapper(self, *args, **kwargs):
        if not self.get_reader_characteristic(5):
            raise RuntimeError("Temperature control is not supported for this reader.")
        return func(self, *args, **kwargs)

    return wrapper


class Gen5OleCommandProtocol:
    """
    The Gen5 OLE Command Protocol is the interface command set for the Gen5 software from Agilent Biotek written by
    UniteLabs.

    Attributes:
        api: The client for the Gen5 OLE server.
        path: A string containing the path to location in which the Gen5 protocol are stored.
        reader_type: An integer representing the reader type.
        experiment: An OLE automation interface of the active experiment.
        plates: An OLE automation interface representing the plates registered in the active experiment.
        active_plate: An OLE automation interface of the currently active plate.
        active_plate_monitor: An OLE automation interface containing a monitoring object for an active read.
        data_buffer: A dictionary containing the result data received for a plate measurement.
        door_open: a boolean indicating whether the door of the reader is open (True) or closed (False)
    """

    door_open: bool = None
    door_open_change_event: asyncio.Event = asyncio.Event()

    current_temperature: float = None
    current_temperature_event = asyncio.Event()
    active_temperature_subscription: typing.Optional[asyncio.Task] = None
    active_temperature_subscription_counter: int = 0

    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""
        return create_logger("gen5")

    def __init__(self, path: str = "C:\\Protocols", simulation: bool = False):
        if not os.name == "nt" and not simulation:
            raise UnsupportedPlatformError(
                "Simulation mode is the only option available on platforms other than Windows. You can enable "
                "simulation mode by setting the simulation parameter in the .env file."
            )

        if os.name == "nt" and not simulation:
            self.api = win32com.client.Dispatch("Gen5.Application")
            self.api.DataExportEnabled = True
            self.experiment: Union[win32com.client.CDispatch, None] = None
            self.plates: Union[win32com.client.CDispatch, None] = None
            self.active_plate: Union[win32com.client.CDispatch, None] = None
            self.active_plate_monitor: Union[win32com.client.CDispatch, None] = None
        else:
            self.api = SimulatedGen5()
            self.experiment: Union[SimulatedExperiment, None] = None
            self.plates: Union[SimulatedPlates, None] = None
            self.active_plate: Union[SimulatedPlate, None] = None
            self.active_plate_monitor: Union[SimulatedPlateReadMonitor, None] = None
        self.path: str = path
        self.reader_number: int = 0
        self.data_buffer: dict = {}
        self.simulation: bool = simulation
        # config
        self.reader_type, self.con_type, self.com_port, self.reader_serial_number = None, None, None, None

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # 0. Initialization & Configuration

    def get_version(self) -> str:
        """
        Returns the Version of the Gen5 software as a string.
        """

        return self.api.Gen5VersionString

    def reinitialize(self):
        """
        Used to reinitialize the api of the Gen5 OLE Command Protocol.
        """
        if not os.name == "nt" and not self.simulation:
            raise UnsupportedPlatformError(
                """
                Simulation mode is the only option available on platforms other than Windows.
                You can enable simulation mode by setting the simulation parameter in the .env file.
                """
            )

        del self.api
        del self.experiment
        del self.plates
        del self.active_plate
        del self.active_plate_monitor

        if win32com and not self.simulation:
            self.api = win32com.client.Dispatch("Gen5.Application")
            self.api.DataExportEnabled = True
            self.experiment: Union[win32com.client.CDispatch, None] = None
            self.plates: Union[win32com.client.CDispatch, None] = None
            self.active_plate: Union[win32com.client.CDispatch, None] = None
            self.active_plate_monitor: Union[win32com.client.CDispatch, None] = None
        else:
            self.api = SimulatedGen5()
            self.experiment: Union[SimulatedExperiment, None] = None
            self.plates: Union[SimulatedPlates, None] = None
            self.active_plate: Union[SimulatedPlate, None] = None
            self.active_plate_monitor: Union[SimulatedPlateReadMonitor, None] = None

        self.configure(self.reader_type, self.con_type, self.com_port, self.reader_serial_number)
        self.calibrate_door()

    async def configure(
        self, reader_type: Union[str, int], con_type: str, com_port: int = 0, reader_serial_number: str = ""
    ):
        """
        Initialize and test the connection to the device.

        Args:
          reader_type: A string or integer representing the reader type. All the supported readers can be found in the
          table below.
          con_type: A string defining the connection type (serial or usb).
          com_port: An integer defining the COM port number for serial connection (1-99 are valid, 0 for auto-detect, if
            only one reader is connected). The com_port is optional if the device is connected by USB.
          reader_serial_number: A string containing the serial number of the reader for usb connection ("" to
            auto-detect if only one reader is connected). The reader_serial_number is optional if the device is
            connected by serial.
          reader_number: An integer representing the number of the reader to use, see Gen5 Automation Programmer Guide
            for details.
            | number | name          |
            | ------ | ------------- |
            | 2      | ELx800        |
            | 3      | ELx808        |
            | 6      | Synergy HT    |
            | 7      | FLx800        |
            | 8      | Powerwave     |
            | 9      | Clarity       |
            | 10     | Synergy2      |
            | 11     | PowerWaveXS 2 |
            | 13     | Synergy Mx    |
            | 14     | Epoch         |
            | 15     | Synergy H4    |
            | 16     | Synergy H1    |
            | 17     | Eon           |
            | 18     | Synergy Neo   |
            | 19     | Cytation3     |
            | 20     | Synergy HTX   |
            | 21     | Cytation5     |
            | 22     | Epoch 2       |
            | 23     | Synergy Neo2  |
            | 24     | Lionheart FX  |
            | 25     | 800TS         |
            | 26     | Cytation1     |
            | 27     | Synergy LX    |
            | 28     | Lionheart LX  |
            | 29     | Cytation7     |
            | 30     | LogPhase 600  |
            | 31     | Cytation C10  |
        """
        reader_number_dict = {
            "ELx800": 2,
            "ELx808": 3,
            "Synergy HT": 6,
            "FLx800": 7,
            "Powerwave": 8,
            "Clarity": 9,
            "Synergy2": 10,
            "PowerWaveXS 2": 11,
            "Synergy Mx": 13,
            "Epoch": 14,
            "Synergy H4": 15,
            "Synergy H1": 16,
            "Eon": 17,
            "Synergy Neo": 18,
            "Cytation3": 19,
            "Synergy HTX": 20,
            "Cytation5": 21,
            "Epoch 2": 22,
            "Synergy Neo2": 23,
            "Lionheart FX": 24,
            "800TS": 25,
            "Cytation1": 26,
            "Synergy LX": 27,
            "Lionheart LX": 28,
            "Cytation7": 29,
            "LogPhase 600": 30,
            "Cytation C10": 31,
        }
        self.reader_type, self.con_type, self.com_port, self.reader_serial_number = (
            reader_type,
            con_type,
            com_port,
            reader_serial_number,
        )
        try:
            self.reader_number = int(reader_type)
            reader_type = list(reader_number_dict.keys())[list(reader_number_dict.values()).index(self.reader_number)]
        except ValueError:
            try:
                self.reader_number = reader_number_dict[reader_type]
            except KeyError:
                raise ValueError(  # pylint: disable=raise-missing-from
                    f"Reader type {reader_type} not found. Please check the reader type and try again."
                )

        self.logger.info("Configured %s reader. Testing connection ...", reader_type)
        if self.simulation and self.api.TestReaderCommunication == 1:
            self.logger.info("Simulated reader configures")
            return

        if con_type.lower() == "serial":
            if com_port == 0:
                self.logger.info("No COM port for serial connection provided. Trying to auto-detect serial port.")
                for i in range(1, 100):
                    self.logger.debug("Trying COM port %s.", i)
                    self.api.ConfigureSerialReader(self.reader_number, i, 9600)
                    if self.api.TestReaderCommunication == 1:
                        self.logger.info("Found reader on COM port %s.", i)
                        self.logger.info("Successfully connected to reader on COM port %s.", i)
                        break
                self.logger.error("No reader found on any COM port!")
            else:
                self.api.ConfigureSerialReader(self.reader_number, com_port, 9600)
                if self.api.TestReaderCommunication != 1:
                    self.logger.error("No reader found on COM port %s.", com_port)
                else:
                    self.logger.info("Successfully connected to reader on COM port %s.", com_port)
        elif con_type.lower() == "usb":
            try:
                self.api.ConfigureUSBReader(self.reader_number, reader_serial_number)
            except pywintypes.com_error:  # pylint: disable=broad-except
                self.logger.error("Failed to connect to USB. Please check the serial number and try again.")
                return
            if self.api.TestReaderCommunication != 1:
                self.logger.error("No reader found connected to USB. Please check the serial number and try again.")
            else:
                self.logger.info("Connected to reader via USB.")

    def calibrate_door(self):
        """
        Calibrates the door at startup by simulating a full open-close cycle.
        This method sequentially executes the opening and closing of the door to ensure the door state is accurately
        reflected and tracked by the connector.
        """
        try:
            self.carrier_out()
            self.carrier_in()
        except Exception as error:  # pylint: disable=broad-except
            self.logger.error("Error calibrating door: %s", error)
        self.door_open = False

    def test_connection(self) -> int:
        """
        Returns 1 if the connection to the device is working, an error code otherwise.

        Error codes see "3. Gen5 Function Call Errors" in the Gen5 Automation Programmer Guide.
        """

        return self.api.TestReaderCommunication

    def get_reader_characteristic(
        self, reader_characteristics_id: int, reader_characteristics_index: int = 0
    ) -> tuple[int, int, Union[str, int, bool]]:
        """
        Returns the reader characteristic from the id and index:

        Args:
            reader_characteristics_id: An integer representing the reader characteristic id:
                0: eAbsorbanceReadSupported; return value: bool; true if reader supports absorbance reads, else false
                1: eAbsorbanceWavelengthMin; return value: int; minimum absorbance wavelength (nm) supported
                2: eAbsorbanceWavelengthMax; return value: int; maximum absorbance wavelength (nm) supported
                3: eAbsorbanceReadModeCount; return value: int; number of absorbance read modes supported
                4: eAbsorbanceReadModeName (index required); return value: str; one of the following:
                    Normal, Rapid, Sweep
                5: eTemperatureControlOption; return value: bool; true if reader supports incubation, else false
                6: eTemperatureMin; return value: int; minimum incubation temperature supported
                7: eTemperatureMax; return value: int; maximum incubation temperature supported
                8: eTemperatureGradientMax; return value: int; maximum gradient value supported.
                    A value of 0 indicates no support.
                9: eShakeSupported; return value: bool; true if reader supports shaking, else false
                10: eSerialNumber; return value: str; serial number of reader
                11: eInstrumentName; return value: str; reader (or imager) name
                12: eFilterFluorescenceSupported; return value: bool; true if reader supports filtered fluorescence
                    else false
                13: eMonoFluorescenceSupported; return value: bool; true if reader supports mono fluorescence else false
                14: eReaderArchitectureLevel; return value: book; architecture level of current reader

            reader_characteristics_index: An integer representing the index of the reader characteristic.
                Only required for eAbsorbanceReadModeName. Number is equal to number of absorbance read modes supported

            return: A tuple containing the reader_characteristics_id, reader_characteristics_index, and the value of the
                reader characteristic as described above.
        """
        reader_characteristics_id_variant = win32com.client.VARIANT(pythoncom.VT_I4, reader_characteristics_id)
        reader_characteristics_index_variant = win32com.client.VARIANT(pythoncom.VT_I4, reader_characteristics_index)
        value_variant = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )
        self.api.GetReaderCharacteristics(
            reader_characteristics_id_variant, reader_characteristics_index_variant, value_variant
        )
        return [reader_characteristics_id, reader_characteristics_index, value_variant.value]

    def get_all_reader_characteristics(self) -> dict:
        """
        Loops through all available reader characteristics.

        return: A dictionary containing all reader characteristics.
            {
                "eAbsorbanceReadSupported": bool,
                "eAbsorbanceWavelengthMin": int,
                "eAbsorbanceWavelengthMax": int,
                "eAbsorbanceReadModeCount": int,
                "eAbsorbanceReadModeName": [str],
                "eTemperatureControlOption": str,
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
        results = {}
        id_names = {
            0: "eAbsorbanceReadSupported",
            1: "eAbsorbanceWavelengthMin",
            2: "eAbsorbanceWavelengthMax",
            3: "eAbsorbanceReadModeCount",
            4: "eAbsorbanceReadModeName",
            5: "eTemperatureControlOption",
            6: "eTemperatureMin",
            7: "eTemperatureMax",
            8: "eTemperatureGradientMax",
            9: "eShakeSupported",
            10: "eSerialNumber",
            11: "eInstrumentName",
            12: "eFilterFluorescenceSupported",
            13: "eMonoFluorescenceSupported",
            14: "eReaderArchitectureLevel",
        }

        for reader_characteristics_id in range(15):
            if reader_characteristics_id in [4]:
                results[id_names[reader_characteristics_id]] = []
                index = 0
                while True:
                    index += 1
                    try:
                        result = self.get_reader_characteristic(reader_characteristics_id, index)
                        results[reader_characteristics_id].append = result[2]
                    except KeyError:
                        break
            else:
                result = self.get_reader_characteristic(reader_characteristics_id)
                results[id_names[reader_characteristics_id]] = result[2]

        return results

    def get_reader_status(self) -> int:
        """
        Returns the status of the reader.

        0:  reader is ready and has no current error status
        -1: reader is busy
        -2: reader not communicating
        -3: reader has not been configured
        >0: reader has an error status. Reboot or system test is required. The returned value should be interpreted as
            an unsigned 16-bit hex code. See the reader manual for details regarding error statuses
        """

        return self.api.GetReaderStatus

    def get_plate_names(self, selection_flag) -> list[str]:
        """
        The GetPlateTypeNames method returns the list of plate type names supported by Gen5.

        Args:
            selection_flag:
                1 Returned plate types are favorite plates
                2 Default Plate Types are included,
                4 Custom Plate Types are included,
                6 All Plate Types are included,
                8 Returned plate types have a lid defined
        """
        names = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )
        self.api.GetPlateTypeNames(selection_flag, names)
        return names.value

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # 1. Experiment Service

    def get_available_protocols(self, path: str) -> list:
        """
        Returns a list of available protocols in the provided path.

        Args:
            path: A string containing the path at which the Gen5 reader protocols are stored.
        """

        if not self.api.DatabaseFileStorage:
            if not os.path.exists(path):
                raise ValueError(
                    f"The protocol path {path} does not exist. Try setting a new path using 'set_protocol_path()'."
                )
            protocols = []
            for protocol in os.listdir(path):
                if protocol.endswith(".prt"):
                    protocols.append(protocol)
        else:
            self.logger.debug("DatabaseFileStorage: %s", self.api.DatabaseFileStorage)
            self.logger.warning(
                "DatabaseFileStorage is not supported. Please change your Gen5 settings to use Windows File System."
            )
            raise NotImplementedError()
        return protocols

    def new_experiment(self, protocol: str, path: str):
        """
        Creates a new experiment with the given protocol.

        Args:
            protocol: A string representing the name of the protocol file name.
            path: A string defining the path at which the new experiment is stored.
        """
        if self.experiment:
            raise ValueError(
                "An experiment is already open. Please close the current experiment before creating a new one."
            )
        if os.path.isabs(protocol):
            self.experiment = self.api.NewExperiment(protocol)
        else:
            self.experiment = self.api.NewExperiment(os.path.join(path, protocol))
        self.plates = self.experiment.Plates

    @error_on_missing_experiment
    def save_experiment(self, path: str, name: str) -> str:
        """
        Saves the current experiment to the given path. Appends a number to the name if the file already exists.
        Returns the path of the saved file.

        Args:
            path: A string containing the path at which the current experiment is to be saved.
            name: A string defining the file name of the saved experiment.
        """

        i = 1
        tmpname = name
        path = Path(path)
        while (path / f"{tmpname}.xpt").exists():
            tmpname = f"{name}_{i}"
            i += 1

        self.experiment.SaveAs(os.path.join(path, name + ".xpt"))
        return str(path)

    @error_on_missing_experiment
    def close_experiment(self):
        """
        Closes the currently open experiment without saving. Call .save_experiment() before closing to save the
        experiment.
        """
        self.experiment.Close()
        self.experiment = None
        self.plates = None

    @error_on_missing_active_plate
    @error_on_missing_experiment
    def get_plate_layout(self) -> ET.Element:
        """
        Returns the layout of the plate in a  BTIPlateLayout XML format.

        Currently only supports not paneled experiments
        """
        layout_str = self.experiment.GetPlateLayout("")
        root = ET.fromstring(layout_str)
        return root

    @error_on_missing_active_plate
    @error_on_missing_experiment
    def set_plate_layout(self, layout: str):
        """
        Sets the layout of the plate. Layout must be in  BTIPlateLayout XML format.
        Returns a message indicating the layout was set successfully.

        Args:
            layout: A string specifying the layout of the plate.
        """

        self.experiment.SetPlateLayout(layout)

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # 2. Plates Service

    def get_plate_list(self) -> list[str]:
        """Returns a list of available plates."""
        if not self.plates:
            raise ValueError("No plates found. Maybe no new experiment was created yet?")
        plates = []
        i = 1
        while True:
            try:
                plates.append(self.plates.GetPlate(i).Name)
                i += 1
            except Exception:  # pylint: disable=broad-except
                break
        return plates

    @error_on_missing_experiment
    def activate_plate(self, name: str):
        """
        Args:
            name: A string specifying the name of the plate to activate.
        """

        i = 1
        while True:
            try:
                plate = self.plates.GetPlate(i)
                if plate.Name == name:
                    self.active_plate = plate
                    break
                i += 1
            except Exception as error:  # pylint: disable=broad-except
                raise ValueError(f"No Plate with the name {name} found") from error

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # 3. Plate Service

    @error_on_missing_active_plate
    def delete_active_plate(self):
        """Deletes the active plate."""

        self.active_plate.Delete()
        self.active_plate = None

    @error_on_missing_active_plate
    def get_plate_calibration_type(self) -> str:
        """Returns the calibration type of the plate: standard or calibration."""
        plate_type_dict = {0: "Standard Plate", 1: "Calibration Plate"}
        return plate_type_dict[self.active_plate.PlateType]

    @error_on_missing_active_plate
    def get_sample_count(self) -> int:
        """
        The number of samples assigned to the current plate.
        This property only applies to experiments based on Custom or Open Protocols.
        """

        return self.active_plate.SampleCount

    @error_on_missing_active_plate
    def get_row_count(self) -> int:
        """Returns the number of rows of the plate."""

        return self.active_plate.MaxRows

    @error_on_missing_active_plate
    def get_column_count(self) -> int:
        """Returns the number of columns of the plate."""

        return self.active_plate.MaxColumns

    @error_on_missing_active_plate
    def get_plate_is_labware(self) -> bool:
        """Returns whether the plate type is labware or not."""
        return self.active_plate.Labware

    @error_on_missing_active_plate
    def get_vessel_count(self) -> int:
        """
        Returns the number of vessels for the current plate type.
        If the plate is not labware the vessel count = 1.
        """
        return self.active_plate.MaxVessels

    @error_on_missing_active_plate
    def get_procedure(self) -> ET.Element:
        """Returns the procedure of the plate in a BTIProcedure XML format."""
        procedure_str = self.active_plate.GetProcedure
        root = ET.fromstring(procedure_str)
        return root

    @error_on_missing_active_plate
    def get_modifiable_procedure(self) -> ET.Element:
        """Returns the modifiable procedure of the plate in a BTIProcedure XML format."""
        procedure_str = self.active_plate.GetModifiableProcedure
        root = ET.fromstring(procedure_str)
        return root

    @error_on_missing_active_plate
    @error_on_read_in_progress
    def set_procedure(self, procedure: str):
        """
        Sets the procedure of the plate. Procedure must be in BTIProcedure XML format.

        Notes from Gen5 Automation Programmer Guide:
        The supported procedure metadata is limited to the following features:
            End-Point / Kinetic Absorbance read step
            Kinetic step (Append to kinetic data and discontinuous kinetics not supported)
            Temperature step
            Shake step

        Args:
            procedure: A string specifying the procedure to execute for the measurement.
        """

        self.active_plate.SetProcedure(procedure)

    @error_on_missing_active_plate
    @error_on_read_in_progress
    def set_modifiable_procedure(self, procedure: str) -> str:
        """
        Sets the modifiable procedure of the plate. Procedure must be in BTIProcedure XML format.

        Notes from Gen5 Automation Programmer Guide:
        The supported procedure metadata is limited to the following features:
            End-Point / Kinetic Absorbance read step
            Kinetic step (Append to kinetic data and discontinuous kinetics not supported)
            Temperature step
            Shake step

        Args:
            procedure: A string specifying the procedure to execute for the measurement.
        """

        self.active_plate.SetModifiableProcedure(procedure)
        return "Procedure set."

    @error_on_missing_active_plate
    @error_on_read_in_progress
    def validate_procedure(self, flip: bool) -> tuple[int, str]:
        """
        Validates the given procedure.

        Args:
          flip: False: normal read position & True: flip A1/H12 locations on the carrier

        Return:
            1 if the procedure is valid, an error code otherwise.
            A message describing the validation status if there is an error.
        """
        if self.reader_number < 10:
            raise RuntimeError("Procedure validation is not supported for this reader.")
        pb_str_rejection_cause = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
        resp = self.active_plate.ValidateProcedure(flip, pb_str_rejection_cause)
        return resp, pb_str_rejection_cause.value

    @error_on_missing_active_plate
    @error_on_read_in_progress
    def start_read(self) -> str:
        """Starts the measurement."""
        # Reset the data buffer
        self.data_buffer = {}
        try:
            self.active_plate_monitor = self.active_plate.StartRead()
        except Exception:  # pylint: disable=broad-except
            pass
        if not self.active_plate_monitor:
            if self.get_read_status() in [1, 3]:
                self._track_door_during_read()
            else:
                raise RuntimeError("Error starting measurement.")

    @error_on_missing_active_plate
    @error_on_read_in_progress
    def start_simulated_read(self):
        """Starts a simulated measurement."""
        # Reset the data buffer
        self.data_buffer = {}
        self.active_plate_monitor = self.active_plate.StartSimulatedRead()
        if not self.active_plate_monitor:
            raise RuntimeError("Error starting simulated measurement.")

    @error_on_missing_active_plate
    @error_on_read_in_progress
    def resume_read(self) -> str:
        """Resumes the measurement."""

        self.active_plate_monitor = self.active_plate.ResumeRead()
        if not self.active_plate_monitor:
            return "Error resuming measurement."
        return "Measurement resumed."

    @error_on_missing_active_plate
    def abort_read(self) -> None:
        """
        Sends an abort command to the reader.
        """
        status = self.get_read_status()
        if status not in [1, 3]:
            raise ValueError("No read in progress to abort.")
        self.active_plate.AbortRead()

    @error_on_missing_active_plate
    def get_read_status(self) -> int:
        """
        Returns the status of the reader.

        0: Not started
        1: In progress
        2: Aborted
        3: Paused
        4: Error
        5: Completed
        """

        return self.active_plate.ReadStatus

    @error_on_missing_active_plate
    def get_data_set_names(self) -> list[str]:
        """Returns the names of the data sets."""
        vt_data_set_names = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )
        self.active_plate.GetDataSetNames(
            "SINGLE", vt_data_set_names
        )  # ProtocolID="SINGLE" does only work for non paneled protocols

        return vt_data_set_names.value

    @error_on_missing_active_plate
    def get_raw_data(self) -> dict:
        """Returns a dictionary with all the information in the given set."""

        set_name = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")

        (
            row,
            column,
            kinetic_index,
            wavelength_index,
            horizontal_index,
            vertical_index,
            value,
            primary_status,
            secondary_status,
        ) = (
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
            win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
            ),
        )
        data_status = self.active_plate.GetRawData(
            set_name,
            row,
            column,
            kinetic_index,
            wavelength_index,
            horizontal_index,
            vertical_index,
            value,
            primary_status,
            secondary_status,
        )
        if set_name.value and data_status != 0:
            self._update_data_buffer(
                set_name,
                row,
                column,
                kinetic_index,
                wavelength_index,
                horizontal_index,
                vertical_index,
                value,
                primary_status,
                secondary_status,
            )
        self.data_buffer["current_data_status"] = data_status
        return self.data_buffer

    def _update_data_buffer(
        self,
        set_name,
        row,
        column,
        kinetic_index,
        wavelength_index,
        horizontal_index,
        vertical_index,
        value,
        primary_status,
        secondary_status,
    ) -> None:
        """
        Updates the measurement data in the data buffer.

        Args:
            set_name: str; A string specifying the name of the data set.
            row: array[int]; An array of longs (int) containing the row (0-based) of the current read.
            column: array[int]; An array of longs (int) containing the column (0-based) of the current read.
            kinetic_index: array[int]; An array of longs (int) containing the kinetic index (0-based) of the current
                read.
            wavelength_index: array[int]; An array of longs (int) containing the spectrum wavelength index (0-based) of
                the current read.
            horizontal_index: array[int]; An array of longs (int) containing the horizontal index (0-based) of the
                current read.
            vertical_index: array[int]; An array of longs (int) containing the vertical index (0-based) of the current
                read.
            value: array[float]; An array of doubles (float) containing the value of the current read.
            primary_status: array[int]; An array of longs (int) containing the primary status of the current read.
                (
                0: The well was successfully read,
                1: The well data was outside the reader's range,
                2: The reader was not able to capture the well data,
                3: The well was masked (read from file only),
                4: An error was encountered reading the well,
                5: The well was not read
                )
            secondary_status: array[int]; An array of longs (int) containing the secondary status of the current read.
                (
                0: There are no secondary status conditions,
                1: The well was being dispensed with injector 1 during the read,
                2: The well was being dispensed with injector 2 during the read,
                3: The well was being dispensed with injector 3 during the read,
                4: The well was being dispensed with injector 4 during the read
                )
        """

        dataset_name = set_name.value

        def _modify_dataset_name(name):
            # Check if name ends with a number
            if name[-1].isdigit():
                # Increment the number at the end
                parts = name.rsplit("_", 1)
                base = parts[0]
                num = int(parts[1]) + 1
                return f"{base}_{num}"
            # Append _1 if no number is present
            return f"{name}_1"

        while dataset_name in self.data_buffer and any(
            list(row.value) == existing_row for existing_row in self.data_buffer[dataset_name]["row"]
        ):
            dataset_name = _modify_dataset_name(dataset_name)

        if dataset_name not in self.data_buffer:
            self.data_buffer[dataset_name] = {
                "status": [],
                "row": [],
                "column": [],
                "kineticIndex": [],
                "wavelengthIndex": [],
                "horizontalIndex": [],
                "verticalIndex": [],
                "value": [],
                "primaryStatus": [],
                "secondaryStatus": [],
            }

        self.data_buffer[dataset_name]["row"].append(list(row.value))
        self.data_buffer[dataset_name]["column"].append(list(column.value))
        self.data_buffer[dataset_name]["kineticIndex"].append(list(kinetic_index.value))
        self.data_buffer[dataset_name]["wavelengthIndex"].append(list(wavelength_index.value))
        self.data_buffer[dataset_name]["horizontalIndex"].append(list(horizontal_index.value))
        self.data_buffer[dataset_name]["verticalIndex"].append(list(vertical_index.value))
        self.data_buffer[dataset_name]["value"].append(list(value.value))
        self.data_buffer[dataset_name]["primaryStatus"].append(list(primary_status.value))
        self.data_buffer[dataset_name]["secondaryStatus"].append(list(secondary_status.value))

    @error_on_missing_active_plate
    def get_sample_description(self) -> str:
        """
        Returns the sample description in the BTISampleIDescription XML format of the plate.

        For example:
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?> <BTISampleDescription Version="1"> <Protocols>
        <Protocol ID="ALL"> <SampleData /> </Protocol> </Protocols> </BTISampleDescription>
        """
        return self.active_plate.GetSampleDescription()

    @error_on_missing_active_plate
    def set_sample_description(self, sample_description: str):
        """
        Sets the sample description of the plate. Sample description must be in BTISampleIDescription XML format.

        Args:
            sample_description: A string containing the sample description in BTISampleIDescription XML format.
        """

        self.active_plate.SetSampleDescription(sample_description)

    @error_on_missing_active_plate
    def get_image_folder_path(self) -> list[str]:
        """Returns the list of image folders that apply to the current plate."""
        paths_variant = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )
        _ = self.active_plate.GetImageFolderPaths(paths_variant)
        return list(paths_variant.value)

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # 4. PlateReadMonitor Service

    def get_read_in_progress(self) -> bool:
        """
        Returns weather the current read is in progress.

        Notes from Gen5 Automation Programmer Guide:
        Querying the status of the ReadInProgress property may not return immediately. In some situations when you query
        the ReadInProgress property, Gen5 must wait for the reader to respond, and it may take several seconds depending
        on the operation that the reader is performing.
        """
        if not self.active_plate_monitor:
            if not self.active_plate:
                return False
            status = self.get_read_status()
            if status == 1:
                return True
            return False
        return self.active_plate_monitor.ReadInProgress

    def get_errors(self) -> list[str]:
        """Returns the error of the current read."""

        if not self.active_plate_monitor:
            return ["No active read found."]
        number_of_errors = self.active_plate_monitor.ErrorsCount
        errors = []

        for i in range(number_of_errors):  # check if index starts at 0 or 1
            error_code = self.active_plate_monitor.GetErrorCode(i)
            if error_code == -601:
                reader_error_index = self.active_plate_monitor.GetReaderError(i)
                errors.append("Reader failed with error code " + str(reader_error_index))
            else:
                errors.append(self.active_plate_monitor.GetErrorMessage(i))

        return errors

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # 5. Carrier Commands

    @error_on_read_in_progress
    def carrier_in(self):
        """Retracts the carrier and closes the door."""

        self.api.CarrierIn()
        self.door_open = False
        self.door_open_change_event.set()

    @error_on_read_in_progress
    def carrier_out(self):
        """Opens the door and moves the carrier out."""

        self.api.CarrierOut()
        self.door_open = True
        self.door_open_change_event.set()

    async def _track_door_during_read(self):
        """Tracks the carrier state during read"""
        if self.door_open:
            self.door_open = False
            self.door_open_change_event.set()
        while True:
            await asyncio.sleep(2)
            if self.get_read_status() in [0, 2, 5]:
                break

        root = self.get_procedure()
        eject_plate_on_completion = root.find(".//EjectPlateOnCompletion")
        if eject_plate_on_completion is not None:
            eject = eject_plate_on_completion.text.lower() == "true"
        if eject:
            self.door_open = True
            self.door_open_change_event.set()

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # 6. Temperature Control

    @error_on_unsupported_temperature_control
    def get_current_temperature(self) -> tuple[float, int]:
        """Returns the current temperature of the reader."""
        temperature_value = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )
        temperature_status = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )

        self.api.GetCurrentTemperatureFP(temperature_value, temperature_status)
        return float(temperature_value.value), temperature_status

    def subscribe_current_temperature(self) -> None:
        """
        Subscribes to the current temperature of the reader.
        """
        if self.active_temperature_subscription_counter == 0:
            self.active_temperature_subscription = sila.utils.set_interval(self.publish_temperature_reads, delay=1)
        self.active_temperature_subscription_counter += 1

    def unsubscribe_current_temperature(self) -> int:
        """
        Unsubscribes from the current temperature of the reader.
        """
        self.active_temperature_subscription_counter -= 1
        if self.active_temperature_subscription_counter == 0:
            self.active_temperature_subscription.cancel()

    def publish_temperature_reads(self):
        """
        Publishes the current temperature of the reader.
        """
        new_temperature, _ = self.get_current_temperature()
        if new_temperature != self.current_temperature:
            self.current_temperature = round(new_temperature, 3)
            self.current_temperature_event.set()
            self.current_temperature_event.clear()

    def get_temperature_set_point(self) -> tuple[int, int]:
        """
        Returns the temperature set point and gradient currently set on the reader.
        """
        if self.reader_number < 10:
            raise RuntimeError('"get temperature set point" is not supported for this reader.')
        temperature_set_point = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )
        gradient = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, win32com.client.VARIANT(pythoncom.VT_BSTR, "")
        )
        self.api.GetTemperatureSetPoint(temperature_set_point, gradient)
        return temperature_set_point.value, gradient.value

    def set_temperature_set_point(self, incubator_state: bool, temperature_set_point: int, gradient: int):
        """
        Sets the temperature set point of the reader.

        Args:
            incubator_state: A boolean defining the state of the incubator. True: Incubator is turned ON, False:
                Incubator is turned OFF.
            temperature_set_point: The value of the temperature setpoint. This parameter is ignored when the incubator
                is turned OFF
            gradient: The value of the temperature gradient between the bottom and the top of the plate. Pass 0 for no
                gradient. This parameter is ignored when the incubator is turned OFF
        """
        self.api.SetTemperatureSetPoint(incubator_state, temperature_set_point, gradient)


class SerialConnectionError(sila.DefinedExecutionError):
    """
    Serial connection is not available. Make sure the serial cable is connected and the right serial port is specified.
    """


class USBConnectionError(sila.DefinedExecutionError):
    """
    USB connection is not available. Make sure the USB cable is connected and the right reader serial number is
    specified.
    """
