import asyncio
from synergy import SynergyHTXBackend
from pylabrobot.resources import Cor_96_wellplate_360ul_Fb
from pylabrobot.plate_reading import PlateReader
import time

from pprint import pp
import usb

from pylabrobot.io.ftdi import FTDI
from pylabrobot.io import ftdi

async def main():

    try:
        backend = SynergyHTXBackend()
        await backend.setup()

        fw = await backend.get_firmware_version()
        dev = backend.io
        print(f"Device:")
        pp(dev.serialize())
        print(f"Firmware version: {fw}")

        await backend.open()

        time.sleep(3)
        await backend.close()

        # print(f"Temperature: {await backend.get_current_temperature():.1f}°C")
    except Exception as e:
        print(f"{type(e)}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
