---
name: documentation-design
description: Design for filling out the VU-lab MkDocs documentation site with component, lab configuration, and orchestrator pages
metadata:
  type: project
---

# VU-lab Documentation Site Design

## Audience

Primary: lab operators and researchers working in the VU lab. Some will need to make code changes (new processes, wrapper adjustments). People adapting this to a different lab are directed to the [OSLA tutorial](https://osla-project.github.io/python-lab-automation-tutorial/).

## Page Structure

Three new top-level pages added to the existing flat nav:

```
docs/
├── index.md                  (existing)
├── overview/
│   └── inventory.md          (existing)
├── components.md             (NEW)
├── lab-configuration.md      (NEW)
├── orchestrator.md           (NEW)
└── about/
    ├── licence.md
    ├── contributing.md
    └── citation.md
```

## Page Content

### `components.md` — Components & Servers

One page with a section per component:

- **Robot arm** (UFactory 850): source repo ([genericroboticarm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm)), Docker config, port, `ROBOT_IP` env var for real vs simulated hardware
- **Plate reader** (Agilent BioTek Synergy HTX): Gen5 private connector, `.env` configuration, port 50053
- **Platform status DB**: PostgreSQL, credentials, port 8000, what it tracks

Teleshake is intentionally omitted — documentation is being written on a separate branch.

### `lab-configuration.md` — Lab Configuration

- **`platform_config.yaml`**: what it defines (storage, movers, shakers with capacities), how `pythonlab_translation` maps to PythonLab resource types, how to add a new device
- **Position graph** (`position_graph_VULabArm.gml`): what it is (GML graph of 3D arm positions for every device), how it was created with [site_parser](https://github.com/OSLA-project/site_parser), overview-only (no node enumeration), note that it lives in `src/openlab_vu/robot_arm/new_graphs/` and is copied into the container at build time

### `orchestrator.md` — Orchestrator Customization

Sections in one page:

1. **Configuration** (`config.py`): worker class, DB client, scheduling algorithm, process module, lab config file path
2. **Worker** (`worker_adaption.py`): `USE_REAL_SERVERS`, `device_wrappers`, `sila_server_name`, how simulation fallback works, `process_step_finished` hook
3. **Robot arm customization** (`xarm_impl.py` + `VULabArm`): extends `XArmImplementation`, sets server name to `"VULabArm"`, `site_to_position_identifier` convention (`device_slot` vs `device` for slot 0)
4. **Device wrappers** (`wrappers/`): `DeviceInterface` interface, `GenericRobotArmWrapper` in detail (simple `MovePlate` vs `intermediate_actions` path), how to write a new wrapper
5. **Processes** (`processes/`): `BasicProcess` resources (hotel, robot arm, shaker pool), `ShakerProcess` as a worked example, how to create a new process

## mkdocs.yml Nav Update

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

## Out of Scope

- Teleshake documentation (separate branch)
- Position graph node-level reference
- Instructions for adapting to a different lab (covered by OSLA tutorial)
