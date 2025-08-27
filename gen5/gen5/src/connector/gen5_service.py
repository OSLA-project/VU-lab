# pylint: disable=missing-class-docstring

import logging
import json
import os
import asyncio
import xml.etree.ElementTree as ET

from unitelabs.cdk import create_logger

from .features.gen5_service import (
    Gen5ServiceBase,
    ReadInProgressError,
    PathNotFoundError,
    NoActivePlateError,
    NoExperimentError,
    ExperimentAlreadyOpenError,
    NoActiveReadError,
    DBError,
    PlateNotFoundError,
    ReadStartError,
    MethodNotSupportedError,
)
from .io import Gen5OleCommandProtocol


def error_handler(func):
    """
    Decorator to handle all the errors thrown by the io layer.
    """

    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except NotImplementedError as error:
            raise DBError(
                """
                DatabaseFileStorage compatibility is not implemented. Please change your Gen5 settings to use Windows
                File System.
                    1. Open Gen5
                    2. Go to System -> Preferences -> File Storage
                    3. Select "Windows File System" and click "Apply"
                """
            ) from error
        except RuntimeError as error:
            if "This action cannot be performed while a read is in progress." in str(error):
                raise ReadInProgressError(description=str(error)) from error
            if "Error starting measurement." in str(error):
                raise ReadStartError from error
            if "Error starting simulated measurement." in str(error):
                raise ReadStartError from error
            if "not supported for this reader." in str(error):
                raise MethodNotSupportedError(description=str(error)) from error
            raise error
        except TypeError as error:
            if "None is not a valid active plate" in str(error):
                raise NoActivePlateError(description=str(error)) from error
            if "None is not a valid experiment" in str(error):
                raise NoExperimentError(description=str(error)) from error
            raise error
        except ValueError as error:
            if "The protocol path" in str(error):
                raise PathNotFoundError(description=str(error)) from error
            if "An experiment is already open" in str(error):
                raise ExperimentAlreadyOpenError(description=str(error)) from error
            if "No plates found" in str(error):
                raise NoExperimentError(description=str(error)) from error
            if "No read in progress to abort" in str(error):
                raise NoActiveReadError(description=str(error)) from error
            if "Plate not found" in str(error):
                raise PlateNotFoundError(description=str(error)) from error
            raise error

    return wrapper


class Gen5Service(Gen5ServiceBase):
    # pylint: disable=missing-class-docstring
    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""
        return create_logger("gen5")

    def __init__(self, protocol: Gen5OleCommandProtocol):
        super().__init__()
        self.protocol = protocol

    @error_handler
    async def get_version(self):
        return self.protocol.get_version()

    @error_handler
    async def get_device_connected(self):
        connection_info = self.protocol.test_connection()
        if connection_info == 1:
            return True
        self.logger.error("Connection to reader failed with error code %s", connection_info)
        return False

    @error_handler
    async def get_plate_types(self):
        return self.protocol.get_plate_names(6)

    @error_handler
    async def get_device_info(self):
        return json.dumps(self.protocol.get_all_reader_characteristics())

    @error_handler
    async def get_reader_status(self):
        status_dict = {
            0: "Reader is ready and has no current error status.",
            -1: "Reader is busy.",
            -2: "Reader not communicating.",
            -3: "Reader has not been configured.",
        }
        status_number = self.protocol.get_reader_status()
        if status_number > 0:
            return f"Reader has an error status: {status_number}. Reboot or system test is required."
        return status_dict[status_number]

    @error_handler
    async def get_available_protocols(self):
        return self.protocol.get_available_protocols(path=self.protocol.path)

    @error_handler
    async def new_experiment(self, protocol):
        self.protocol.new_experiment(protocol, path=self.protocol.path)

    async def get_experiment_open(self):
        if self.protocol.experiment:
            return True
        return False

    @error_handler
    async def save_experiment(self, path, name):
        save = self.protocol.save_experiment(path, name)
        return f"Experiment saved to {save}"

    @error_handler
    async def close_experiment(self):
        try:
            self.protocol.close_experiment()
        except ValueError as error:
            raise NoExperimentError("No experiment is open.") from error

    @error_handler
    async def get_plate_layout(self):
        root = self.protocol.get_plate_layout()
        xml_bytes = ET.tostring(root, encoding="utf-8")
        xml_string = xml_bytes.decode("utf-8")
        return xml_string

    @error_handler
    async def set_plate_layout(self, layout):
        self.protocol.set_plate_layout(layout)

    @error_handler
    async def get_protocol_path(self):
        return self.protocol.path

    @error_handler
    async def set_protocol_path(self, path):
        if not os.path.exists(path):
            raise PathNotFoundError(f"Path {path} does not exist.")
        self.protocol.path = path

    @error_handler
    async def get_plate_list(self):
        return self.protocol.get_plate_list()

    @error_handler
    async def activate_plate(self, plate_name):
        self.protocol.activate_plate(plate_name)

    @error_handler
    async def get_active_plate(self):
        if self.protocol.active_plate:
            return self.protocol.active_plate.Name
        raise NoActivePlateError

    @error_handler
    async def delete_active_plate(self):
        self.protocol.delete_active_plate()

    @error_handler
    async def get_procedure(self):
        root = self.protocol.get_procedure()
        xml_bytes = ET.tostring(root, encoding="utf-8")
        xml_string = xml_bytes.decode("utf-8")
        return xml_string

    @error_handler
    async def get_modifiable_procedure(self):
        root = self.protocol.get_modifiable_procedure()
        xml_bytes = ET.tostring(root, encoding="utf-8")
        xml_string = xml_bytes.decode("utf-8")
        return xml_string

    @error_handler
    async def set_procedure(self, procedure):
        self.protocol.set_procedure(procedure)

    @error_handler
    async def set_modifiable_procedure(self, procedure):
        self.protocol.set_modifiable_procedure(procedure)

    async def deactivate_plate(self):
        if not self.protocol.active_plate:
            raise NoActivePlateError
        self.protocol.active_plate = None

    @error_handler
    async def validate_procedure(self, flip):
        validation, message = self.protocol.validate_procedure(flip)
        if validation == -707:
            message = "No read parameters"
        return validation, message

    @error_handler
    async def start_read(self):
        self.protocol.start_read()

    @error_handler
    async def resume_read(self):
        self.protocol.resume_read()

    @error_handler
    async def abort_read(self):
        self.protocol.abort_read()
        while self.protocol.get_read_status() in (1, 3):
            await asyncio.sleep(0.5)
        final_status = self.protocol.get_read_status()
        return (
            "Measurement aborted with final read status "
            + str(final_status)
            + " (0: Not started, 1: In progress, 2: Aborted, 3: Paused, 4: Error, 5: Completed)."
        )

    @error_handler
    async def get_read_status(self):
        return self.protocol.get_read_status()

    @error_handler
    async def get_plate_calibration_type(self):
        return self.protocol.get_plate_calibration_type()

    @error_handler
    async def get_sample_count(self):
        return self.protocol.get_sample_count()

    @error_handler
    async def get_row_count(self):
        return self.protocol.get_row_count()

    @error_handler
    async def get_column_count(self):
        return self.protocol.get_column_count()

    @error_handler
    async def get_plate_is_labware(self):
        return self.protocol.get_plate_is_labware()

    @error_handler
    async def get_vessel_count(self):
        return self.protocol.get_vessel_count()

    @error_handler
    async def get_data_set_names(self):
        return self.protocol.get_data_set_names()

    @error_handler
    async def get_plate_data(self):
        return json.dumps(self.protocol.get_raw_data())

    @error_handler
    async def get_sample_description(self):
        return self.protocol.get_sample_description()

    @error_handler
    async def get_image_folder_path(self):
        return self.protocol.get_image_folder_path()

    @error_handler
    async def get_read_in_progress(self):
        return self.protocol.get_read_in_progress()
