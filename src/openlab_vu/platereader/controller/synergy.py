from pathlib import Path
from loguru import logger
from pylabrobot.resources import (
    Plate,
    Well,
    create_ordered_items_2d,
    thermo_AB_96_wellplate_300ul_Vb_MicroAmp,
)
import asyncio as aio
from datetime import datetime
from zoneinfo import ZoneInfo
import openlab_vu.platereader.controller.types as T
from pylabrobot.plate_reading.agilent.biotek_synergy_ht_backend import SynergyHTBackend
from openlab_vu import utils

logger.configure()


class SynergyHTXController(SynergyHTBackend):

    def __init__(
        self,
        timeout: int = 20,
        device_id: int = None,
        save_dir: str | Path | None = None,
        timestamp: str | None = None,
        tz: str = "Europe/Amsterdam",
    ):
        super().__init__(timeout, device_id)

        self.tray_state = T.TrayState.Unknown
        self.wells: list[Well] = []
        self.save_dir = (
            utils.ensure_dir(Path(save_dir)) if save_dir is not None else None
        )
        self.timestamp = timestamp if timestamp is not None else utils.iso_timestamp()
        self.tz = tz

    @property
    def plate(self) -> Plate | None:
        """
        A proxy for the _plate attribute in the base class.

        Returns:
            The stored plate (or None if there is no plate)
        """

        return self._plate

    async def get_plate_id(self) -> int | None:
        """
        Get the plate ID from the plate name.

        Returns:
            The plate ID as an integer or None if there is no plate.
        """

        if not isinstance(self.plate, Plate):
            return -1
        return int(self.plate.name)

    async def open_tray(self) -> T.TrayState:
        """
        Open the device tray.

        Returns:
            A TrayState instance.
        """

        try:
            logger.debug(f"Opening tray...")
            await super().open_tray()
            self.tray_state = T.TrayState.Open
        except Exception as e:
            self.tray_state = T.TrayState.Unknown
        finally:
            return self.tray_state

    async def close_tray(self) -> T.TrayState:
        """
        Close the device tray.

        Returns:
            A TrayState instance.
        """

        try:
            logger.debug(f"Closing tray...")
            await super().close_tray()
            self.tray_state = T.TrayState.Closed
        except Exception as e:
            self.tray_state = T.TrayState.Unknown
        finally:
            return self.tray_state

    async def remove_plate(self) -> str | None:
        """
        Remove the plate from the device.

        Returns:
            The plate ID.
        """

        if self.plate is None:
            return

        # TODO: Remove the plate from the tray by using a robotic arm.
        plate_name = self.plate.name
        self._plate = None
        self.wells.clear()

        return plate_name

    async def read_temperature(self) -> float:
        """
        Read the device temperature.

        Returns:
            The temperature as a float.
        """

        logger.debug(f"Reading temperature...")
        return await super().get_current_temperature()

    async def read_absorbance(
        self,
        wavelength: int,
    ) -> dict:
        """
        Read the absorbance of the wells in the currently loaded plate.

        Args:
            wavelength: Wavelength used for reading the absorbance.

        Returns:
            A ReadAbsorbance_Responses instance.
        """

        logger.debug(f"Reading absorbance...")
        result = await super().read_absorbance(self.plate, self.wells, wavelength)

        # TODO Store the data by using the user-supplied
        # destination directory (self.save_dir).
        # data = result.get('data', None)

        return result

    async def read_fluorescence(
        self,
        excitation_wavelength: int,
        emission_wavelength: int,
        focal_height: float,
    ) -> dict:
        """
        Read the fluorescence of the wells in the currently loaded plate.

        Args:
            excitation_wavelength: The excitation wavelength.
            emission_wavelength: The emission wavelength.
            focal_height: The focal height of the plate.

        Returns:
            A ReadFluorescence_Responses instance.
        """

        logger.debug(f"Reading fluorescence...")
        result = await super().read_fluorescence(
            self.plate,
            self.wells,
            excitation_wavelength,
            emission_wavelength,
            focal_height,
        )

        # TODO Store the data by using the user-supplied
        # destination directory (self.save_dir).
        # data = result.get('data', None)

        return result

    async def read_luminescence(
        self,
        focal_height: float,
        integration_time: float,
    ) -> dict:
        """
        Read the luminescence of the wells in the currently loaded plate.

        Args:
            focal_height: The focal height of the plate.
            integration_time: Integration time.
            metadata: Metadata provided by the client.

        Returns:
            A ReadLuminescence_Responses instance.
        """

        logger.debug(f"Reading luminescence...")
        result = await super().read_luminescence(
            focal_height,
            integration_time,
        )

        # TODO Store the data by using the user-supplied
        # destination directory (self.save_dir).
        # data = result.get('data', None)
        return result
