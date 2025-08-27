import asyncio
import logging
import os
from typing import Union

from unitelabs.cdk import Connector, Config, create_logger

from .io import Gen5OleCommandProtocol

from .gen5_service import Gen5Service
from .door_controller import DoorController
from .simulation_controller import SimulationController
from .temperature_controller import TemperatureController
from .shake_controller import ShakeController
from .protocol_controller import ProtocolController

if os.name == "nt":
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=".env")


class Gen5Config(Config):
    """Contains the configuration parameters of the device serial interface"""

    reader_type: Union[str, int]
    con_type: str
    com_port: int = 0
    reader_serial_number: str = ""
    protocol_path: str = "C:\\Protocols"
    simulation: bool = False


async def create_app():
    """Creates the connector application"""
    logger = create_logger("gen5", logging.INFO)

    app = Connector(
        {
            "sila_server": {
                "name": "Gen5 Software",
                "type": "Reader",
                "description": "A connector to control the software to control multiple readers by Agilent",
                "version": "1.1.0",
                "vendor_url": "https://unitelabs.io/",
            }
        }
    )

    config = Gen5Config()
    protocol = Gen5OleCommandProtocol(path=config.protocol_path, simulation=config.simulation)
    logger.info("Gen5 version: %s", protocol.get_version())
    logger.info("Configuring Gen5 connection ...")
    await protocol.configure(config.reader_type, config.con_type, config.com_port, config.reader_serial_number)
    protocol.calibrate_door()

    app.register(Gen5Service(protocol=protocol))
    app.register(DoorController(protocol=protocol))
    app.register(SimulationController(protocol=protocol))
    app.register(TemperatureController(protocol=protocol))
    app.register(ShakeController(protocol=protocol))
    app.register(ProtocolController(protocol=protocol))

    yield app

    logger.info("Quitting Gen5 ...")
    protocol.carrier_in()
    del protocol
    logger.info("Gen5 has been quit")
