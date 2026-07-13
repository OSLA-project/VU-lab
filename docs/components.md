# Components

This page describes the SiLA servers and supporting services that make up the VU lab automation stack.

## Robot Arm

**Hardware:** [UFactory 850](https://www.ufactory.us/product/850)

**SiLA server source:** [genericroboticarm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm) (port 50054)

See [Robot Arm](components/robot_arm.md) for full setup and configuration.

## Plate Reader

**Hardware:** [Agilent BioTek Synergy HTX Multimode Reader](https://www.agilent.com/en/product/microplate-instrumentation/microplate-readers/multimode-microplate-readers/biotek-synergy-htx-multimode-reader-1623207)

**SiLA server source:** Gen5 private connector (not publicly available)

**Docker service:** `gen5` (port 50053)

The Gen5 connector requires environment configuration before use. Copy `gen5/.env.example` to `gen5/.env` and fill in the values specific to your plate reader setup.

## Magnetic Shaker

**Hardware:** VARIONMAG Teleshake 1536 (8 units)

**SiLA server source:** [Teleshake-1536](https://github.com/OSLA-project/Teleshake-1536)

**Running mode:** Native on Windows (not in Docker — RS-232 COM ports cannot be forwarded to Linux containers)

The teleshake runs outside Docker on the Windows host and connects to the lab PC's native RS-232 port (COM1). See [Teleshake 1536](components/teleshake.md) for full setup instructions and known issues.

## Plate Hotels

**Hardware:** [HighRes Bio Stationary Plate Hotel](https://highresbio.com/hardware/automated-sample-storage/stacking-and-storage)

The plate hotels are passive storage — they have no SiLA server of their own. The robot arm moves plates in and out; positions are defined in the position graph (see [Lab Configuration — Position graph](lab-configuration.md#position-graph)).

## Scanner

**Hardware:** [Epson Perfection V600 Flatbed Scanner](https://epson.com/For-Home/Scanners/Photo-Scanners/Epson-Perfection-V600-Photo-Scanner/p/B11B198011)

The scanner is used to take pictures of plates. The robot arm places a plate on the scanner via the photobooth position defined in the position graph (see [Lab Configuration — Position graph](lab-configuration.md#position-graph)).

## Platform Status Database

**Docker service:** `platform_status_db` (port 8000)

A PostgreSQL-backed service that tracks the status of containers (plates) on the platform — their current location, barcode, and processing history. The laborchestrator writes to it via `StatusDBImplementation` and it is exposed as a REST API.

**Credentials (development only):** `platform_status / platform_status`

The database uses a named Docker volume (`pgdata`) so data persists across container restarts.

A web interface is available at [http://localhost:8000](http://localhost:8000) when the service is running.
