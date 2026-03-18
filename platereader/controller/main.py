import asyncio
from synergy import SynergyHTBackend
from pylabrobot.resources import Cor_96_wellplate_360ul_Fb
from pylabrobot.plate_reading import PlateReader

import usb

from pylabrobot.io.ftdi import FTDI
from pylabrobot.io import ftdi

async def main():

    for dev in ftdi.usb.core.find(find_all=True):
        dev_id = f"{dev.idVendor:04x}:{dev.idProduct:04x}"
        print(f"Found device {dev_id}...")

    try:
        backend = SynergyHTBackend()
        await backend.setup()
        print(f"Firmware: {backend}")
        print(f"Temperature: {await backend.get_current_temperature():.1f}°C")
    except Exception as e:
        print(f"{type(e)}: {e}")

if __name__ == "__main__":
    asyncio.run(main())