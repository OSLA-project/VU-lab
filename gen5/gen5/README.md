# Gen5 Connector

This connector enables the control of all plate readers by Agilent that connect to the Gen5 software

## Requirements
Requires [python > 3.9](https://www.python.org/downloads/) and [poetry](https://python-poetry.org/docs/#installing-with-pipx)

Requires the [Gen5 software](https://www.agilent.com/en/product/cell-analysis/cell-imaging-microscopy/cell-imaging-microscopy-software/biotek-gen5-software-for-imaging-microscopy-1623226) with an active license.

Only works on windows because requires the Gen5 software (only available on windows) and the [pywin32](https://pypi.org/project/pywin32/) python package.

This connector however does have a simulation mode that works on other operating systems as well.

## Quickstart
This implementation is based on the [UniteLabs Connector Framework](https://gitlab.com/unitelabs/connector-framework) and uses the [UniteLabs SiLA Python](https://gitlab.com/unitelabs/integrations/sila2/sila-python) implementation.

To get started, clone this repository and run the poetry install command within the connector folder:

``` cmd
git clone https://gitlab.com/unitelabs/connectors/gen5.git
cd gen5
poetry install
```
To use the connector, environment variables need to be set. This can be done by adding a .env file in the root directory.
Here are some standard variables that can be used for local testing in the [UniteLabs SiLA Browser](https://gitlab.com/unitelabs/integrations/sila2/sila-browser):

``` .env
SILA_SERVER__NAME='Gen5'
CLOUD_SERVER_ENDPOINT__ENDPOINT = localhost:443 
CLOUD_SERVER_ENDPOINT__SECURE = True
SILA_SERVER__UUID = <Your generated uuid4>
SILA_SERVER__HOST = 0.0.0.0
SILA_SERVER__PORT = 50001
```
You can generate a uuid4 quickly with this online [generator](https://www.uuidgenerator.net/version4). If you're using 
the server-initiated cloud connectivity, enter the cloud endpoint of your client application.

To use the connector with an attached reader, specify these additional parameters in the .env file:

``` .env 
reader_type='Synergy H1'
CON_TYPE = 'USB'
COM_PORT = 0
READER_SERIAL_NUMBER = ''
PROTOCOL_PATH = 'C:\\Users\\Public\\Documents\\Protocols'
SIMULATION = False
```

Explanation of the additional env variables:
- reader_type: can be int or string from the reader type table found below
- con_type: serial or usb
- com_port: An integer defining the COM port number for serial connection (1-99 are valid, 0 for auto-detect, if only one reader is connected). The com_port is ignored if the device is connected by USB.
- reader_serial_number: A string containing the serial number of the reader for usb connection ("" to auto-detect if only one reader is connected). The reader_serial_number is ignored if the device is connected by serial.
- protocol_path: the default path where to look for protocols (can be changed by getters and setters within gen5_service but this change is not permanent and will reset if the connector is restarted)
- simulation: boolean to set in which state the connector should try to start in

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


Finally, running the start command will start the connector

``` cmd
poetry run connector start
```

## Register connector start on login

simply run ´register_login_item.bat´ (double click in folder, no other installation needed)

## Documentation
The usage documentation can be found on the official [UniteLabs docs](https://docs-unitelabs-web-815d69b03b66df4c3a4817af38d7e7b09a17f7c4b50b.gitlab.io/python-sdk/guides/device-guides/biotek-gen5) page.