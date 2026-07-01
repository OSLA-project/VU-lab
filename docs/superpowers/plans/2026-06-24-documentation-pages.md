# VU-lab Documentation Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write three new MkDocs documentation pages (components, lab-configuration, orchestrator) and update mkdocs.yml nav to include them.

**Architecture:** Three standalone Markdown files added to `docs/`, each covering a distinct concern. No code changes — documentation only. The mkdocs.yml nav is updated last once all pages exist.

**Tech Stack:** MkDocs with Material theme, Markdown

## Global Constraints

- Working directory: `/home/dsmits/osla/VU-lab`
- Teleshake is intentionally excluded from all pages (in-progress on a separate branch)
- Audience: lab operators and researchers in the VU lab; some will make code changes
- People adapting to a different lab are referred to: https://osla-project.github.io/python-lab-automation-tutorial/
- Position graph documentation is overview-only — do not enumerate nodes
- No emoji, no trailing summaries

---

### Task 1: Write `docs/components.md`

**Files:**
- Create: `docs/components.md`

**Interfaces:**
- Consumes: nothing
- Produces: `docs/components.md` with sections for robot arm, plate reader, platform status DB

- [ ] **Step 1: Create the file**

Write `docs/components.md` with the following content:

```markdown
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

## Platform Status Database

**Docker service:** `platform_status_db` (port 8000)

A PostgreSQL-backed service that tracks the status of containers (plates) on the platform — their current location, barcode, and processing history. The laborchestrator writes to it via `StatusDBImplementation` and it is exposed as a REST API.

**Credentials (development only):** `platform_status / platform_status`

The database uses a named Docker volume (`pgdata`) so data persists across container restarts.

A web interface is available at [http://localhost:8000](http://localhost:8000) when the service is running.
```

- [ ] **Step 2: Verify the file renders locally (optional)**

```bash
cd /home/dsmits/osla/VU-lab && mkdocs serve
```

Open http://localhost:8000 and confirm the Components page appears without errors. Stop the server with Ctrl+C. Skip this step if mkdocs is not installed locally.

- [ ] **Step 3: Commit**

```bash
cd /home/dsmits/osla/VU-lab && git add docs/components.md && git commit -m "docs: add components page"
```

---

### Task 2: Write `docs/lab-configuration.md`

**Files:**
- Create: `docs/lab-configuration.md`
- Reference (read only): `src/openlab_vu/laborchestrator/platform_config.yaml`

**Interfaces:**
- Consumes: nothing
- Produces: `docs/lab-configuration.md` with sections for platform_config.yaml and position graph

- [ ] **Step 1: Create the file**

Write `docs/lab-configuration.md` with the following content:

```markdown
# Lab Configuration

## Platform Configuration (`platform_config.yaml`)

The file `src/openlab_vu/laborchestrator/platform_config.yaml` (mounted into the laborchestrator container as `/opt/vu_lab/platform_config.yaml`) defines the physical layout of the lab for the scheduler and orchestrator.

It has two sections:

### `sila_servers`

Declares the devices available on the platform, grouped by type, with their capacity (how many plates they can hold simultaneously):

```yaml
sila_servers:
  storage:
    hotel_1_d_pos_:
      capacity: 8
  movers:
    robot_arm:
      capacity: 1
  shakers:
    shaker_1_d_pos_1:
      capacity: 1
    # ... shaker_2 through shaker_10
```

The device names here (e.g. `hotel_1_d_pos_`, `robot_arm`, `shaker_1_d_pos_1`) must match:
- The node labels in the position graph (see [Position graph](#position-graph))
- The resource names used in process definitions (see [Orchestrator — Processes](orchestrator.md#processes))
- The keys in `device_wrappers` and `sila_server_name` in `worker_adaption.py` (see [Orchestrator — Worker](orchestrator.md#worker))

### `pythonlab_translation`

Maps the device type categories to PythonLab resource classes:

```yaml
pythonlab_translation:
  storage: LabwareStorageResource
  movers: MoverServiceResource
  shakers: ShakerServiceResource
```

This tells the PythonLab scheduling framework which resource type to use when allocating each category of device.

### Adding a new device

1. Add an entry under the appropriate category in `sila_servers` with a `capacity` value.
2. Add a matching entry to `device_wrappers` and `sila_server_name` in `worker_adaption.py`.
3. Add the device's positions to the position graph.
4. Reference the device by the same name in your process definition.

## Position Graph

The file `src/openlab_vu/robot_arm/new_graphs/position_graph_VULabArm.gml` is a [GML](https://en.wikipedia.org/wiki/Graph_Modelling_Language) graph that encodes the 3D coordinates the robot arm uses to reach every device in the lab.

Each device has:
- An **entrypoint** node — a safe intermediate position the arm moves through before approaching the device
- One or more **path nodes** (`_ppath_N`) — waypoints for collision-free approach
- A **position node** (e.g. `shaker_1_d_pos_1`) — the final pick/place coordinate

Each node stores the arm's `x`, `y`, `z` position (in mm) and `roll`, `pitch`, `yaw` orientation (in degrees).

The graph was created using the [site_parser](https://github.com/OSLA-project/site_parser) tool, which provides a GUI for recording arm positions and exporting them as a GML file.

**To update positions** (e.g. after moving a device or adding a new one), use site_parser to record the new positions and export an updated GML file to `src/openlab_vu/robot_arm/new_graphs/`. The file is copied into the robot arm container at build time (`Dockerfile`: `COPY ./new_graphs/* /root/.config/GenericRoboticArm/`), so rebuild the container after any changes:

```bash
docker compose up --build robot_arm
```
```

- [ ] **Step 2: Commit**

```bash
cd /home/dsmits/osla/VU-lab && git add docs/lab-configuration.md && git commit -m "docs: add lab configuration page"
```

---

### Task 3: Write `docs/orchestrator.md`

**Files:**
- Create: `docs/orchestrator.md`
- Reference (read only): `src/openlab_vu/laborchestrator/config.py`, `src/openlab_vu/laborchestrator/vu_lab/worker_adaption.py`, `src/openlab_vu/robot_arm/vu_lab/xarm_impl.py`, `src/openlab_vu/laborchestrator/vu_lab/wrappers/generic_robot_arm_wrapper.py`, `src/openlab_vu/laborchestrator/vu_lab/wrappers/device_interface.py`, `src/openlab_vu/laborchestrator/vu_lab/processes/basic_process.py`, `src/openlab_vu/laborchestrator/vu_lab/processes/shaker_process.py`

**Interfaces:**
- Consumes: nothing
- Produces: `docs/orchestrator.md` with sections for config, worker, robot arm customization, wrappers, and processes

- [ ] **Step 1: Create the file**

Write `docs/orchestrator.md` with the following content:

```markdown
# Orchestrator

The laborchestrator is the main automation engine. It reads a lab configuration, schedules process steps across devices, dispatches commands to SiLA servers via device wrappers, and tracks container state in the platform status database.

The VU-lab customization lives in `src/openlab_vu/laborchestrator/`.

## Configuration (`config.py`)

`src/openlab_vu/laborchestrator/config.py` is the central wiring file. It is loaded at startup and controls the key behaviors of the orchestrator:

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from vu_lab.worker_adaption import Worker

db_client = StatusDBImplementation()   # database backend
worker = Worker                        # customized worker class

lab_config_file = "/opt/vu_lab/platform_config.yaml"
default_scheduling_time = 1            # seconds
scheduling_algorithm = "BottleneckPD" # or "CP-Solver", or None for scheduler default

from vu_lab import processes
process_module = processes             # where process classes are auto-discovered
```

To switch to simulation mode (no database, default worker), set `db_client = None` and `worker = None`.

## Worker (`worker_adaption.py`)

`src/openlab_vu/laborchestrator/vu_lab/worker_adaption.py` is the bridge between the orchestrator engine and the physical devices. The `Worker` class extends `WorkerInterface` and overrides the key dispatch methods.

### Controlling real vs simulated devices

```python
USE_REAL_SERVERS = [
    "robot_arm",
]
```

Any device name listed here will have commands sent to its real SiLA server. Devices not in this list are simulated: the orchestrator waits a random 2–12 seconds and moves on. To simulate a device, remove it from `USE_REAL_SERVERS`.

### Mapping device names to wrappers and servers

```python
device_wrappers: dict[str, type[DeviceInterface]] = {
    "robot_arm": GenericRobotArmWrapper,
    "shaker_1_d_pos_1": ShakerWrapper,
}

sila_server_name: dict[str, str] = {
    "robot_arm": "VULabArm",
    "shaker_1_d_pos_1": "Teleshake1536Server",
}
```

`device_wrappers` maps the device name (as it appears in `platform_config.yaml` and process definitions) to the wrapper class that translates process steps into SiLA commands. `sila_server_name` maps the same device names to the SiLA server name used for discovery on the network.

### Post-step hook

`process_step_finished()` is called after every completed step. The VU-lab implementation includes a barcode reading hook:

```python
if "read_barcode" in step.data:
    container.barcode = ...  # retrieve from barcode reader
    self.db_client.set_barcode(container)
```

You can add custom post-step logic here, for example triggering a measurement or logging an event.

## Robot Arm Customization

The VU-lab uses a UFactory 850 arm, which is an xArm variant. The `genericroboticarm` package provides a generic `XArmImplementation`. The VU-lab subclasses it in `src/openlab_vu/robot_arm/vu_lab/xarm_impl.py`:

```python
class VULabArm(XArmImplementation):
    @classmethod
    def get_name(cls) -> str:
        return "VULabArm"

    def site_to_position_identifier(self, device: str, slot: int) -> str:
        if slot > 0:
            return f"{device}_{slot}"
        else:
            return device
```

`get_name()` sets the SiLA server name to `"VULabArm"` — this must match the value in `sila_server_name` in `worker_adaption.py`.

`site_to_position_identifier()` controls how a `(device, slot)` pair maps to a node label in the position graph. For a device with a single position (slot 0), the label is just the device name (e.g. `shaker_1_d_pos_1`). For multi-slot devices, the slot number is appended (e.g. `hotel_1_d_pos_3`). This convention must be consistent with the node labels in `position_graph_VULabArm.gml`.

## Device Wrappers

A device wrapper translates a high-level process step into one or more SiLA commands. All wrappers implement `DeviceInterface`:

```python
class DeviceInterface(ABC):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: SilaClient,
        **kwargs,
    ) -> Observable:
        ...
```

`get_SiLA_handler()` must return an `Observable` — an object the orchestrator can monitor for completion.

### `GenericRobotArmWrapper`

`src/openlab_vu/laborchestrator/vu_lab/wrappers/generic_robot_arm_wrapper.py`

Handles plate movement with the robot arm. Two paths:

**Simple move** (no intermediate actions):
```python
return sila_client.RobotController.MovePlate(origin_site, target_site)
```

**Move with intermediate actions** (e.g. scanning a barcode mid-transfer):
Uses `LabwareTransferManipulatorController.GetLabware()` with `IntermediateActions` followed by `RobotController.PlacePlate()`. Intermediate actions are passed as a list of strings in the process step's `device_kwargs`.

### Writing a new wrapper

1. Create a file in `src/openlab_vu/laborchestrator/vu_lab/wrappers/`.
2. Subclass `DeviceInterface` and implement `get_SiLA_handler()`.
3. Import the wrapper type into `sila2_driver` (or fall back to `SilaClient`) with a `try/except ModuleNotFoundError` block, as done in `GenericRobotArmWrapper`.
4. Register it in `device_wrappers` and `sila_server_name` in `worker_adaption.py`.
5. Add the device to `USE_REAL_SERVERS` if it should not be simulated.

## Processes

A process defines a lab workflow as a sequence of steps over a set of containers and devices. All VU-lab processes live in `src/openlab_vu/laborchestrator/vu_lab/processes/` and are auto-discovered at startup via `process_module = processes` in `config.py`.

### `BasicProcess`

All VU-lab processes inherit from `BasicProcess`, which pre-defines the available resources:

```python
self.hotel1 = LabwareStorageResource(proc=self, name="hotel_1_d_pos_")
self.robot_arm = MoverServiceResource(proc=self, name="robot_arm")
self.shaker1 = ShakerServiceResource(proc=self, name="shaker_1_d_pos_1")
# ... shaker2 through shaker6
self.shaker_pool = ShakerServiceResource(proc=self, name=None)  # any available shaker
```

The `name` argument must match a device name in `platform_config.yaml`. `shaker_pool` with `name=None` lets the scheduler pick any available shaker.

### `ShakerProcess` — a worked example

```python
class ShakerProcess(BasicProcess):
    def __init__(self, priority=3, num_plates=6, duration=10, frequency=10):
        super().__init__(priority=priority, num_plates=num_plates,
                         process_name="Vu Test Process")
        self.duration = duration
        self.frequency = frequency

    def init_service_resources(self):
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i + 1)  # plates start in hotel slots 1–N

    def process(self):
        for idx in range(self.num_mw_plates):
            cont = self.containers[idx]
            self.robot_arm.move(cont, self.shaker_pool)
            self.shaker_pool.shake_plate(cont, self.duration, self.frequency)
            self.robot_arm.move(cont, self.hotel1)
```

### Creating a new process

1. Copy `src/openlab_vu/laborchestrator/vu_lab/processes/empty_process.py` and rename it.
2. Inherit from `BasicProcess` (or `PLProcess` directly if you need different resources).
3. Set starting positions in `init_service_resources()`.
4. Implement `process()` using `self.robot_arm.move()`, `self.shaker_pool.shake_plate()`, etc.
5. The new class is automatically discovered at startup — no registration needed.
```

- [ ] **Step 2: Commit**

```bash
cd /home/dsmits/osla/VU-lab && git add docs/orchestrator.md && git commit -m "docs: add orchestrator customization page"
```

---

### Task 4: Update `mkdocs.yml` nav

**Files:**
- Modify: `mkdocs.yml`

**Interfaces:**
- Consumes: `docs/components.md`, `docs/lab-configuration.md`, `docs/orchestrator.md` (must exist)
- Produces: updated nav in `mkdocs.yml`

- [ ] **Step 1: Update the nav section in `mkdocs.yml`**

Replace the existing `nav:` block with:

```yaml
nav:
  - Home: index.md
  - Overview:
      - Inventory: overview/inventory.md
  - Components: components.md
  - Lab Configuration: lab-configuration.md
  - Orchestrator: orchestrator.md
  - About:
      - Licence: about/licence.md
      - Contributing: about/contributing.md
      - Citation: about/citation.md
```

- [ ] **Step 2: Verify the site builds without errors**

```bash
cd /home/dsmits/osla/VU-lab && mkdocs build --strict 2>&1
```

Expected: `INFO - Documentation built in X.XX seconds` with no warnings or errors. If mkdocs is not installed locally, skip and rely on CI.

- [ ] **Step 3: Commit**

```bash
cd /home/dsmits/osla/VU-lab && git add mkdocs.yml && git commit -m "docs: update nav with new documentation pages"
```
