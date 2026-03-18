from typing import Optional
import asyncio
from pylabrobot.resources import Plate
from pylabrobot.plate_reading import BioTekPlateReaderBackend
from pylabrobot.plate_reading import SynergyH1Backend

class SynergyHTBackend(BioTekPlateReaderBackend):
# class SynergyHTBackend(SynergyH1Backend):
    async def open(self, slow: bool = False) -> None:
        """Open the plate reader door / eject plate.

        Note: slow parameter is ignored on Synergy HT (not supported).
        """
        # Synergy HT doesn't support slow mode command (&), so skip it
        return await self.send_command("J")


    async def close(self, plate: Optional[Plate] = None, slow: bool = False) -> None:
        """Close the plate reader door / load plate.

        Note: slow parameter is ignored on Synergy HT (not supported).
        """
        # Synergy HT doesn't support slow mode command (&), so skip it
        self._plate = None
        if plate is not None:
            await self.set_plate(plate)
        return await self.send_command("A")