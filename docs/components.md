# Components

This page describes the SiLA servers and supporting services that make up the VU lab automation stack.

## Robot Arm

**Hardware:** [UFactory 850](https://www.ufactory.us/product/850)

**SiLA server source:** [genericroboticarm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm) — a generic SiLA2 robotic arm driver that communicates with the xArm SDK.

**Docker service:** `robot_arm` (port 50054)

The robot arm container is built from `src/openlab_vu/robot_arm/`. It installs the `genericroboticarm` package along with the VU-lab-specific customization (see [Orchestrator — Robot arm customization](orchestrator.md#robot-arm-customization)).

**Configuration:**

| Environment variable | Default | Description |
|---|---|---|
| `PORT` | `50054` | SiLA2 server port |
| `HOST` | `0.0.0.0` | Bind address |
| `ROBOT_IP` | *(unset)* | IP address of the physical arm. If unset, the server runs in simulation mode. |
| `ADDITIONAL_PARAMS` | *(empty)* | Extra flags passed to the server entrypoint |

To connect to real hardware, set `ROBOT_IP` to the arm's IP address in your `.env` file:

```env
ROBOT_IP=192.168.1.xxx
```

The position graph file (`position_graph_VULabArm.gml`) is copied into the container at build time — see [Lab Configuration — Position graph](lab-configuration.md#position-graph) for details.

A web interface for the arm is available at [http://localhost:8055](http://localhost:8055) when the service is running.

## Plate Reader

**Hardware:** [Agilent BioTek Synergy HTX Multimode Reader](https://www.agilent.com/en/product/microplate-instrumentation/microplate-readers/multimode-microplate-readers/biotek-synergy-htx-multimode-reader-1623207)

**SiLA server source:** Gen5 private connector (not publicly available)

**Docker service:** `gen5` (port 50053)

The Gen5 connector requires environment configuration before use. Copy `gen5/.env.example` to `gen5/.env` and fill in the values specific to your plate reader setup.

## Magnetic Shaker

**Hardware:** [Thermo Fisher Teleshake](https://www.thermofisher.com/order/catalog/product/50094320)

**SiLA server source:** [teleshake](https://gitlab.com/sila-driver-group/teleshake) — a community SiLA2 driver for the Thermo Scientific Teleshake 1536.

**Docker service:** `teleshake` (port 50050)

The teleshake container clones the upstream driver and runs SiLA2 code generation at build time via `src/openlab_vu/teleshake/codegen.sh`.

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
