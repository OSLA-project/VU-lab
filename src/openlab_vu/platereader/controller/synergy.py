from pathlib import Path
from loguru import logger
from pylabrobot.resources import Plate, Well
import openlab_vu.platereader.controller.types as T
from pylabrobot.plate_reading.agilent.biotek_synergy_ht_backend import SynergyHTBackend
from openlab_vu import utils
from pprint import pp

logger.configure()


class SynergyHTXController(SynergyHTBackend):

    def __init__(
        self,
        device_id: int = None,
        timeout: int = 20,
        save_dir: str | Path | None = None,
        timestamp: str | None = None,
        tz: str = "Europe/Amsterdam",
    ):
        """
        A SynergyHTX controller with some convenience functions

        Args:
            device_id: The device ID.
            timeout: Timeout in seconds.
            save_dir: Destination directory for acquired data.
            timestamp: Timestamp to use for the saved data file.
            tz: Timezone for constructing a default timestamp (TODO).
        """

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

    @plate.setter
    def plate(self, plate: Plate | None) -> None:
        self._plate = plate

    async def open_tray(self) -> T.TrayState:
        """
        Open the device tray.

        Returns:
            A TrayState instance.
        """

        try:
            logger.debug(f"Opening tray...")
            await super().open()
            self.tray_state = T.TrayState.Open
        except Exception as e:
            logger.error(e)
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
            await super().close()
            self.tray_state = T.TrayState.Closed
        except Exception as e:
            self.tray_state = T.TrayState.Unknown
        finally:
            return self.tray_state

    def get_plate_name(self) -> str:
        """
        Get the name of the currently loaded plate.

        Returns:
            The plate name or None if there is no plate in the tray.
        """

        return self.plate.name if isinstance(self.plate, Plate) else ""

    async def insert_plate(self, plate: Plate, wells: list[Well]) -> str | None:
        """
        Insert a plate into the tray and store the wells that need to be read.

        Returns:
            The plate name.
        """

        if self.plate is not None:
            logger.warning(f"Plate '{self.get_plate_name()}' is in the tray.")
            return ""

        await super().set_plate(plate)
        self.wells = wells

        logger.info(f"Plate '{plate}' set successfully.")
        return self.get_plate_name()

    async def remove_plate(self) -> str | None:
        """
        Remove the plate from the device.

        Returns:
            The plate name.
        """

        if self.plate is None:
            return ""

        plate_name = self.plate.name
        self.plate = None
        self.wells.clear()
        logger.info(f"Plate '{plate_name}' removed successfully.")

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
        pp(result)

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
        pp(result)

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
        pp(result)

        # TODO Store the data by using the user-supplied
        # destination directory (self.save_dir).
        # data = result.get('data', None)
        return result
