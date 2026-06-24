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
3. Import the wrapper's SiLA client type with a `try/except ModuleNotFoundError` fallback to `SilaClient`, as done in `GenericRobotArmWrapper`.
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
