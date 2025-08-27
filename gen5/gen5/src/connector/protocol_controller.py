import os
from xml.etree import ElementTree as ET

from .features.protocol_controller import (
    ProtocolControllerBase,
    ExperimentAlreadyOpenError,
    InvalidParameterError,
    NoActivePlateError,
    NoExperimentError,
)
from .io import Gen5OleCommandProtocol


def error_handler(func):
    """
    Decorator to handle all the errors thrown by the io layer.
    """

    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except TypeError as error:
            if "None is not a valid active plate" in str(error):
                raise NoActivePlateError(description=str(error)) from error
            if "None is not a valid experiment" in str(error):
                raise NoExperimentError(description=str(error)) from error
            raise error

    return wrapper


class ProtocolController(ProtocolControllerBase):
    # pylint: disable=missing-class-docstring
    def __init__(self, protocol: Gen5OleCommandProtocol):
        super().__init__()
        self.protocol = protocol

    async def initialize_empty_protocol(self):
        if self.protocol.experiment:
            raise ExperimentAlreadyOpenError(
                description="An experiment is already open. Please (save and) close the current experiment before "
                "creating a new one."
            )
        self.protocol.new_experiment(os.path.abspath(".\\src\\connector\\features\\empty.prt"), "")
        self.protocol.activate_plate(self.protocol.get_plate_list()[0])
        self.protocol.set_procedure(
            """
        <BTIProcedure Version="1.00">
            <Labware>
                <Type>Microplate</Type>
                <Name>96 WELL PLATE</Name>
                <UseLid>true</UseLid>
            </Labware>
            <StepList>
            </StepList>
        </BTIProcedure>
        """
        )

    @error_handler
    async def get_step_list(self):
        procedure = self.protocol.get_procedure()
        step_list_element = procedure.find("StepList")
        step_list = [str(step.tag) for step in step_list_element]
        return step_list

    @error_handler
    async def get_step(self, index):
        procedure = self.protocol.get_procedure()
        step_list_element = procedure.find("StepList")
        step = step_list_element[index]
        return str(ET.tostring(step).decode()).replace("\n    ", "\n")

    @error_handler
    async def delete_step(self, index):
        step_count = len(await self.get_step_list())
        if index > step_count - 1:
            raise InvalidParameterError(
                description=f"Index out of range. Only {step_count} currently in the procedure."
            )
        procedure = self.protocol.get_procedure()
        step_list_element = procedure.find("StepList")
        step_list_element.remove(step_list_element[index])
        procedure = self._remove_unsupported_tags(procedure)
        self.protocol.set_procedure(ET.tostring(procedure).decode())

    @error_handler
    async def add_absorbance_step(self, index, wavelengths, read_speed, wavelength_switching):
        step_count = len(await self.get_step_list())
        if index > step_count:
            raise InvalidParameterError(
                description=f"Index out of range. Only {step_count} currently in the procedure."
            )

        read_speeds = {0: "Normal", 1: "Sweep"}

        procedure = self.protocol.get_procedure()
        step_list_element = procedure.find("StepList")

        read_step = ET.Element("ReadStep")

        ET.SubElement(read_step, "Detection").text = "Absorbance"
        ET.SubElement(read_step, "ReadType").text = "EndPoint"
        ET.SubElement(read_step, "Wells").text = "Full Plate"
        ET.SubElement(read_step, "ReadSpeed").text = read_speeds[read_speed]
        # ET.SubElement(read_step, 'DelayAfterPlateMovementMSec').text = '100' test if needed
        # ET.SubElement(read_step, 'MeasurementsPerDataPoint').text = '8' test if needed
        if wavelength_switching:
            ET.SubElement(read_step, "WavelengthSwitching")

        measurements = ET.SubElement(read_step, "Measurements")
        wavelengths = [int(wavelength) for wavelength in wavelengths.split(",")]
        for i, wavelength in enumerate(wavelengths, start=1):
            measurement = ET.SubElement(measurements, "Measurement")
            measurement.set("Index", str(i))
            ET.SubElement(measurement, "Wavelength").text = str(wavelength)

        step_list_element.insert(index, read_step)

        procedure = self._remove_unsupported_tags(procedure)
        self.protocol.set_procedure(ET.tostring(procedure).decode())

    @error_handler
    async def add_shake_step(self, index, mode, duration_sec, displacement_mm, orbital_speed):
        modes = {
            0: "Linear",
            1: "Orbital",
            2: "DoubleOrbital",
        }
        orbital_speeds = {
            0: "Slow",
            1: "Fast",
        }
        procedure = self.protocol.get_procedure()
        step_list_element = procedure.find("StepList")

        shake_step = ET.Element("ShakeStep")
        ET.SubElement(shake_step, "Mode").text = modes[mode]
        ET.SubElement(shake_step, "DurationSec").text = str(duration_sec)
        ET.SubElement(shake_step, "DisplacementMM").text = str(displacement_mm)
        if mode in ["Orbital", "DoubleOrbital"]:
            ET.SubElement(shake_step, "OrbitalSpeed").text = orbital_speeds[orbital_speed]

        step_list_element.insert(index, shake_step)

        procedure = self._remove_unsupported_tags(procedure)
        self.protocol.set_procedure(ET.tostring(procedure).decode())

    def _remove_unsupported_tags(self, procedure_root):
        options = procedure_root.find("Options")
        if options is not None:
            procedure_root.remove(options)
        well_selection = procedure_root.find("WellSelection")
        if well_selection is not None:
            procedure_root.remove(well_selection)

        return procedure_root

    @error_handler
    async def get_plate_type(self):
        procedure = self.protocol.get_procedure()
        return (
            str(procedure.find("Labware").find("Name").text) + ", Lid: " + procedure.find("Labware").find("UseLid").text
        )

    async def get_supported_plate_types(self):
        return self.protocol.get_plate_names(6)

    @error_handler
    async def set_plate_type(self, plate_type, use_lid):
        procedure = self.protocol.get_procedure()

        labware = procedure.find("Labware")
        labware.find("Name").text = plate_type
        labware.find("UseLid").text = "true" if use_lid else "false"

        procedure = self._remove_unsupported_tags(procedure)
        self.protocol.set_procedure(ET.tostring(procedure).decode())
