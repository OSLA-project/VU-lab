# pylint: disable=invalid-name
import logging
import time
import asyncio

from unitelabs.cdk import create_logger


class SimulatedPlateReadMonitor:
    "Simulated PlateReadMonitor object for testing purposes. Replaces the PlateReadMonitor interface."

    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""
        return create_logger("gen5")

    ReadInProgress = True
    ErrorsCount = 3
    Errors = ["Error1", "Error2", "Error3"]

    def __init__(self):
        self.logger.info(
            """
            SIMULATION: SimulatedPlateReadMonitor created.
            With following preset attributes: ReadInProgress = %s, ErrorsCount = %s, Errors = %s.
            """,
            self.ReadInProgress,
            self.ErrorsCount,
            self.Errors,
        )

    def GetReaderError(self, index):
        """
        Simulated GetReaderError method for testing purposes. Replaces the GetReaderError method from the
        Gen5.PlateReadMonitor object. Returns a mock error message.
        """
        self.logger.info(
            "SIMULATION: GetReaderError(%s) called on SimulatedPlateReadMonitor. Returning mock error message.", index
        )
        return self.Errors[index]


class Simulatedwin32com:
    "Simulated win32com object for testing purposes. Replaces the minimal needed calls from the win32com package."

    def __init__(self):
        pass

    class client:
        """
        Simulated win32com.client object for testing purposes. Replaces the minimal needed calls from the
        win32com.client package usage within this connector.
        """

        def __init__(self):
            pass

        CDispatch = object

        class VARIANT:
            "Simulated win32com.client.VARIANT object for testing purposes."
            value = None

            def __init__(self, value_type, value):
                self.value: value_type = value

        def Dispatch(self, *_, **__):
            "Simulated win32com.client.Dispatch object for testing purposes."
            return SimulatedGen5()


class SimulatedBYREF:
    def __or__(self, other):  # using the bitwise or operator with the BYREF object doesn't throw an error
        return other


class Simulatedpythoncom:
    """
    Simulated pythoncom object for testing purposes.
    Replaces the minimal needed calls from the pythoncom package usage within this connector.
    """

    VT_I4 = int
    VT_BSTR = str
    VT_VARIANT = Simulatedwin32com.client.VARIANT
    VT_BYREF = SimulatedBYREF()


class Simulatedpywintypes:
    """
    Simulated pywintypes object for testing purposes.
    Replaced the minimal needed calls from the pywintypes package usage within this connector.
    """

    com_error = ValueError


class SimulatedGen5:
    "Simulated Gen5 Interface for testing purposes. Replaces the Gen5.Application object."

    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""
        return create_logger("gen5")

    Gen5VersionString = "3.14.03"
    TestReaderCommunication = 1
    DatabaseFileStorage = False

    def __init__(self):
        self.logger.info(
            """
            SIMULATION: SimulatedGen5 created with following preset attributes:
            Gen5VersionString = %s, TestReaderCommunication = %s, DatabaseFileStorage = %s.
            """,
            self.Gen5VersionString,
            self.TestReaderCommunication,
            self.DatabaseFileStorage,
        )
        self.incubator_state = False
        self.temperature_set_point = 37
        self.current_temperature = 25
        self.gradient = 0
        self._simulate_incubation()

    def ConfigureUSBReader(self, _, __):
        """
        Simulated ConfigureUSBReader method for testing purposes. Replaces the ConfigureUSBReader method from the
        Gen5.Application object. Does not perform any action.
        """
        self.logger.info("SIMULATION: ConfigureUSBReader() called on SimulatedGen5. No action performed.")

    def ConfigureSerialReader(self, _, __, ___):
        """
        Simulated ConfigureSerialReader method for testing purposes. Replaces the ConfigureSerialReader method from the
        Gen5.Application object. Does not perform any action.
        """
        self.logger.info("SIMULATION: ConfigureSerialReader() called on SimulatedGen5. No action performed.")

    def GetReaderStatus(self):
        """
        Simulated GetReaderStatus method for testing purposes. Replaces the GetReaderStatus method from the
        Gen5.Application object.
        0: reader is ready and has no current error status
        """
        self.logger.info("SIMULATION: GetReaderStatus() called on SimulatedGen5. Returning 0.")
        return 0

    def GetPlateTypeNames(self, _: int, names: Simulatedwin32com.client.VARIANT):
        """
        Simulated GetPlateTypeNames method for testing purposes. Replaces the GetPlateTypeNames method from the
        Gen5.Application object.
        """
        names.value = ["Standard Plate", "Flat Bottom Plate", "Deep Well Plate"]
        self.logger.info(
            """
            SIMULATION: GetPlateTypeNames() called on SimulatedGen5. names now hold the following list. Not considering
            selection_flag: %s
            """,
            names.value,
        )

    def GetReaderCharacteristics(
        self,
        reader_characteristics_id: Simulatedwin32com.client.VARIANT,
        _: Simulatedwin32com.client.VARIANT,
        values: Simulatedwin32com.client.VARIANT,
    ):
        """
        Simulated GetReaderCharacteristics method for testing purposes. Replaces the GetReaderCharacteristics from the
        Gen5.Application object.
        the variant value to the corresponding value of the characteristics_id.
            0: "eAbsorbanceReadSupported": True,
            1: "eAbsorbanceWavelengthMin": 230,
            2: "eAbsorbanceWavelengthMax": 999,
            3: "eAbsorbanceReadModeCount": 2,
            4: "eAbsorbanceReadModeName": [],
            5: "eTemperatureControlOption": True,
            6: "eTemperatureMin": 18,
            7: "eTemperatureMax": 70,
            8: "eTemperatureGradientMax": 1,
            9: "eShakeSupported": True,
            10: "eSerialNumber": "23112122",
            11: "eInstrumentName": "Synergy H1",
            12: "eFilterFluorescenceSupported": True,
            13: "eMonoFluorescenceSupported": True,
            14: "eReaderArchitectureLevel": 4
        """
        value_dict = {
            0: True,
            1: 230,
            2: 999,
            3: 2,
            4: [],
            5: True,
            6: 18,
            7: 70,
            8: 1,
            9: True,
            10: "23112122",
            11: "Synergy H1",
            12: True,
            13: True,
            14: 4,
        }
        self.logger.info(
            """
                         SIMULATION: GetReaderCharacteristics() called on SimulatedGen5. Setting the variant value to
                         the corresponding value of the characteristics_id.
                         all_returns = {
                            "eAbsorbanceReadSupported": True,
                            "eAbsorbanceWavelengthMin": 230,
                            "eAbsorbanceWavelengthMax": 999,
                            "eAbsorbanceReadModeCount": 2,
                            "eAbsorbanceReadModeName": [],
                            "eTemperatureControlOption": True,
                            "eTemperatureMin": 18,
                            "eTemperatureMax": 70,
                            "eTemperatureGradientMax": 1,
                            "eShakeSupported": True,
                            "eSerialNumber": "23112122",
                            "eInstrumentName": "Synergy H1",
                            "eFilterFluorescenceSupported": True,
                            "eMonoFluorescenceSupported": True,
                            "eReaderArchitectureLevel": 4
                        }
                         """
        )
        values.value = value_dict[reader_characteristics_id.value]

    def NewExperiment(self, protocol: str):
        """
        Simulated NewExperiment method for testing purposes. Replaces the NewExperiment method from the
        Gen5.Application object.
        """
        self.logger.info(
            """
            SIMULATION: NewExperiment(%s) called on SimulatedGen5. Simulated experiment created without considering the
            protocol passed.
            """,
            protocol,
        )
        return SimulatedExperiment(protocol)

    def CarrierIn(self):
        """
        Simulated CarrierIn method for testing purposes. Replaces the CarrierIn method from the
        Gen5.Application object. Does not perform any action.
        """
        self.logger.info("SIMULATION: CarrierIn() called on SimulatedGen5. No action performed.")

    def CarrierOut(self):
        """
        Simulated CarrierOut method for testing purposes. Replaces the CarrierOut method from the
        Gen5.Application object. Does not perform any action.
        """
        self.logger.info("SIMULATION: CarrierOut() called on SimulatedGen5. No action performed.")

    def GetCurrentTemperatureFP(
        self, temperature_value: Simulatedwin32com.client.VARIANT, temperature_status: Simulatedwin32com.client.VARIANT
    ):
        """
        Simulated GetCurrentTemperatureFP method for testing purposes. Replaces the GetCurrentTemperatureFP method from
        the Gen5.Application object. Returns the simulated current temperature and temperature_status.
        """
        temperature_value.value = self.current_temperature
        temperature_status.value = 1

    def GetTemperatureSetPoint(
        self, temperature_set_point: Simulatedwin32com.client.VARIANT, gradient: Simulatedwin32com.client.VARIANT
    ):
        """
        Simulated GetTemperatureSetPoint method for testing purposes. Replaces the GetTemperatureSetPoint method from
        the Gen5.Application object. Returns the temperature set point and gradient.
        """
        temperature_set_point.value = self.temperature_set_point
        gradient.value = self.gradient

    def SetTemperatureSetPoint(self, incubator_state: bool, temperature_set_point: int, gradient: int):
        """
        Simulated SetTemperatureSetPoint method for testing purposes. Replaces the SetTemperatureSetPoint method from
        the Gen5.Application object. Sets the temperature set point as well as starts incubation if incubator_state
        True.
        """
        self.incubator_state = incubator_state
        self.temperature_set_point = temperature_set_point
        self.gradient = gradient

    async def _simulate_incubation(self):
        """
        Used to simulate incubation for simulation purposes.
        """
        while True:
            asyncio.sleep(2)
            if self.incubator_state:
                if self.current_temperature < self.temperature_set_point:
                    self.logger.inf("SIMULATION: Heating up. Increasing simulated temperature")
                    self.current_temperature += 0.2
                else:
                    self.logger.inf("SIMULATION: Cooling down. Reducing simulated temperature")
                    self.current_temperature -= 0.2
            else:
                if self.current_temperature > 25:
                    self.logger.inf("SIMULATION: Passive cooling down. Reducing simulated temperature")
                    self.current_temperature -= 0.1


class SimulatedExperiment:
    "Simulated Experiment object for testing purposes. Replaces the Experiment interface."

    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""
        return create_logger("gen5")

    def __init__(self, _):
        self.Plates = SimulatedPlates()
        self.logger.info("SIMULATION: SimulatedExperiment created with a Plates = SimulatedPlates object.")

    def SaveAs(self, path: str):
        """
        Simulated SaveAs method for testing purposes. Replaces the SaveAs method from the
        Gen5.Experiment object.
        Creates a mock file at the given path.
        """
        path = path.replace(".xpt", ".txt")
        with open(path, "w", encoding="utf-8") as file:
            file.write("Mock file content")
        self.logger.info("SIMULATION: SaveAs() called on SimulatedExperiment. Mock .txt file created at path: %s", path)

    def Close(self):
        """
        Simulated Close method for testing purposes. Replaces the Close method from the
        Gen5.Experiment object. Does not perform any action.
        """
        self.logger.info("SIMULATION: Close() called on SimulatedExperiment. No action performed.")


class SimulatedPlates:
    """
    Simulated Plates object for testing purposes. Replaces the Plates interface.

    Initiates with two SimulatedPlate objects named "Plate 1" and "Plate 2".
    """

    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""
        return create_logger("gen5")

    def __init__(self):
        self.plates: list[SimulatedPlate] = [SimulatedPlate("Plate 1"), SimulatedPlate("Plate 2")]
        self.logger.info(
            """
            SIMULATION: SimulatedPlates created with two SimulatedPlate objects named 'Plate1' and 'Plate2'
            and the following preset attributes.
            """
        )

    def GetPlate(self, index: int):
        """
        Simulated GetPlate method for testing purposes. Replaces the GetPlate method from the
        Gen5.Plates object.
        """
        self.logger.info("SIMULATION: GetPlate(%s) called on SimulatedPlates. Returning SimulatedPlate object.", index)
        return self.plates[index - 1]  # -1 because plate indexing within Gen5 starts at 1


class SimulatedPlate:
    "Simulated Plate object for testing purposes. Replaces the Plate interface."

    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""
        return create_logger("gen5")

    Name = ""
    ReadStatus = 0
    PlateType = "Standard Plate"
    SampleCount = 96
    MaxRows = 8
    MaxColumns = 12
    Labware = False
    MaxVessels = 1
    GetProcedure = """
            <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <BTIProcedure Version="1.00">
                <Labware>
                    <Type>Microplate</Type>
                    <Name>96 WELL PLATE</Name>
                    <UseLid>true</UseLid>
                </Labware>
                <WellSelection>PerStep</WellSelection>
                <StepList>
                    <ReadStep>
                        <Detection>Absorbance</Detection>
                        <ReadType>EndPoint</ReadType>
                        <Wells>Full Plate</Wells>
                        <Measurements>
                            <Measurement Index="1">
                                <Wavelength>750</Wavelength>
                            </Measurement>
                        </Measurements>
                        <ReadSpeed>Normal</ReadSpeed>
                        <DelayAfterPlateMovementMSec>100</DelayAfterPlateMovementMSec>
                        <MeasurementsPerDataPoint>8</MeasurementsPerDataPoint>
                    </ReadStep>
                    <DelayStep>
                        <DurationSec>20.000</DurationSec>
                        <ReferenceTime>EndOfPreviousStep</ReferenceTime>
                    </DelayStep>
                </StepList>
                <Options>
                    <DiscontinuousKinetics Selected="false" />
                    <SkipLoadPlateDialog>false</SkipLoadPlateDialog>
                    <EjectPlateOnCompletion>true</EjectPlateOnCompletion>
                    <UseSlowerCarrierSpeed>false</UseSlowerCarrierSpeed>
                    <ReadPlateBarCode Selected="false" />
                </Options>
            </BTIProcedure>
        """
    GetModifiableProcedure = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <BTIModifiableProcedure Version="1.00">
                <Labware>
                    <Name Modifiable="Yes">96 WELL PLATE</Name>
                </Labware>
                <StepList>
                    <ReadStep Detection="Absorbance" />
                    <DelayStep />
                </StepList>
                <DiscontinuousKinetics Selected="No" />
            </BTIModifiableProcedure>
        """

    def __init__(self, name: str):
        self.Name = name
        self.monitor = None
        self.logger.info(
            "SIMULATION: SimulatedPlate created with the following preset attributes: Name = %s, ReadStatus = 0.",
            self.Name,
        )

    def StartRead(self):
        """
        Simulated StartRead method for testing purposes. Replaces the StartRead method from the
        Gen5.Plate object. Starts a simulated read that lasts 60 seconds.

        The simulated read changes the ReadStatus to 1 for 60 seconds.
        """
        self.monitor = SimulatedPlateReadMonitor()
        self.logger.info("SIMULATION: StartRead() called on SimulatedPlate. Starting simulated read.")
        self.ReadStatus = 1
        self.monitor.ReadInProgress = True
        self.logger.info("SIMULATION: Waiting 60 seconds for the read to finish.")
        time.sleep(60)
        self.ReadStatus = 0
        self.monitor.ReadInProgress = False
        self.logger.info("SIMULATION: ReadStatus set to 0. Simulated read finished.")

    def StartSimulatedRead(self):
        """
        Simulated StartSimulatedRead method for testing purposes. Replaces the StartSimulatedRead method from the
        Gen5.Plate object. Starts a simulated read that lasts 60 seconds.

        The simulated read changes the ReadStatus to 1 for 60 seconds.
        """
        self.monitor = SimulatedPlateReadMonitor()
        self.logger.info("SIMULATION: StartSimulatedRead() called on SimulatedPlate. Starting simulated read.")
        self.ReadStatus = 1
        self.monitor.ReadInProgress = True
        self.logger.info("SIMULATION: Waiting 60 seconds for the read to finish.")
        time.sleep(60)
        self.ReadStatus = 0
        self.monitor.ReadInProgress = False
        self.logger.info("SIMULATION: ReadStatus set to 0. Simulated read finished.")

    def ResumeRead(self):
        """
        Simulated ResumeRead method for testing purposes. Replaces the ResumeRead method from the
        Gen5.PlateReadMonitor object. Sets ReadInProgress to True.
        """
        self.ReadStatus = 1
        self.monitor.ReadInProgress = True
        self.logger.info("SIMULATION: ResumeRead() called on SimulatedPlateReadMonitor. Sets ReadInProgress to True.")

    def AbortRead(self):
        """
        Simulated AbortRead method for testing purposes. Replaces the AbortRead method from the
        Gen5.PlateReadMonitor object. Sets ReadInProgress to False after 2 seconds.
        """
        self.logger.info(
            "SIMULATION: AbortRead() called on SimulatedPlateReadMonitor. Sets ReadInProgress to False in 2 seconds."
        )
        time.sleep(2)
        self.ReadStatus = 0
        self.monitor.ReadInProgress = False

    def SetProcedure(self, _: str):
        """
        Simulated SetProcedure method for testing purposes. Replaces the SetProcedure method from the
        Gen5.Plate object. Does not perform any action.
        """
        self.logger.info("SIMULATION: SetProcedure() called on SimulatedPlate. No action performed.")

    def ValidateProcedure(self, _: bool):
        """
        Simulated ValidateProcedure method for testing purposes. Replaces the ValidateProcedure method from the
        Gen5.Plate object. Returns 1. Ignores the actual procedure from the protocol used to create the simulated
        experiment and the flip parameter.
        """
        self.logger.info(
            """
            SIMULATION: ValidateProcedure() called on SimulatedPlate. Returning 1. Ignoring the actual procedure
            from the protocol used to create the simulated experiment and the flip parameter.
            """
        )
        return 1

    def Delete(self):
        """
        Simulated Delete method for testing purposes. Replaces the Delete method from the
        Gen5.Plate object. Does not perform any action.
        """
        self.logger.info("SIMULATION: Delete() called on SimulatedPlate. No action performed.")

    def GetDataSetNames(self, _: str, data_set_names: Simulatedwin32com.client.VARIANT):
        """
        Simulated GetDataSetNames method for testing purposes. Replaces the GetDataSetNames method from the
        Gen5.Plate object. Fills the Variant object with a list of moc data set names.
        """
        data_set_names.value = ["MockDataSetName1", "700", "MockDataSetName3"]
        self.logger.info(
            "SIMULATION: GetDataSetNames() called on SimulatedPlate. data_set_names now hold the following list: %s",
            data_set_names.value,
        )

    def GetRawData(
        self,
        set_name: Simulatedwin32com.client.VARIANT,
        row: Simulatedwin32com.client.VARIANT,
        column: Simulatedwin32com.client.VARIANT,
        kinetic_index: Simulatedwin32com.client.VARIANT,
        wavelength_index: Simulatedwin32com.client.VARIANT,
        horizontal_index: Simulatedwin32com.client.VARIANT,
        vertical_index: Simulatedwin32com.client.VARIANT,
        value: Simulatedwin32com.client.VARIANT,
        primary_status: Simulatedwin32com.client.VARIANT,
        secondary_status: Simulatedwin32com.client.VARIANT,
    ):
        """
        Simulated GetRawData method for testing purposes. Replaces the GetRawData method from the
        Gen5.Plate object. Fills the Variant objects with mock data.
        """
        set_name.value = 600
        row.value = "1, 2, 3"
        column.value = "A, B, C"
        kinetic_index.value = "1, 2, 3"
        wavelength_index.value = "450, 500, 550"
        horizontal_index.value = "1, 2, 3"
        vertical_index.value = "1, 2, 3"
        value.value = "0.1, 0.2, 0.3"
        primary_status.value = "1, 2, 3"
        secondary_status.value = "1, 2, 3"
        self.logger.info(
            """
            SIMULATION: GetRawData() called on SimulatedPlate. Filling Variant objects with mock data:
            row = %s, column = %s, kinetic_index = %s, wavelength_index = %s, horizontal_index = %s,
            vertical_index = %s, value = %s, primary_status = %s, secondary_status = %s
            """,
            row.value,
            column.value,
            kinetic_index.value,
            wavelength_index.value,
            horizontal_index.value,
            vertical_index.value,
            value.value,
            primary_status.value,
            secondary_status.value,
        )

    def GetSampleDescription(self):
        """
        Simulated GetSampleDescription method for testing purposes. Replaces the GetSampleDescription method from the
        Gen5.Plate object. Returns a mock sample description in the BTISampleDescription XML without taking into
        account the actual sample description from the protocol used to create the simulated experiment.
        """
        self.logger.info(
            """
            SIMULATION: GetSampleDescription() called on SimulatedPlate. Returning mock sample description in the
            BTISampleDescription XML format ignoring the actual sample description from the protocol used to create the
            simulated experiment.
            """
        )
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?> <BTISampleDescription Version="1">
        <Protocols> <Protocol ID="ALL"> <SampleData /> </Protocol> </Protocols> </BTISampleDescription>"""

    def SetSampleDescription(self, _: str):
        """
        Simulated SetSampleDescription method for testing purposes. Replaces the SetSampleDescription method from the
        Gen5.Plate object. Does not perform any action.
        """
        self.logger.info("SIMULATION: SetSampleDescription() called on SimulatedPlate. No action performed.")

    def GetImageFolderPaths(
        self,
    ):
        """
        Simulated GetImageFolderPaths method for testing purposes. Replaces the GetImageFolderPaths method from the
        Gen5.Plate object. Returns a mock image folder path.
        """
        return "C:/Mock/Image/Folder"
