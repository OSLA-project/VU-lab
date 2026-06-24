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
