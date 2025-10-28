# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VU-lab is an OpenLab configuration for the VU lab that orchestrates automated lab equipment through SiLA2 protocol. It integrates multiple SiLA connectors (teleshake, Gen5 plate reader, generic robot arm) with a lab orchestration system.

The system uses Docker Compose to run multiple services:
- **laborchestrator**: Main orchestration engine (port 8050)
- **labscheduler**: Job scheduling service
- **sila-browser**: Web UI for SiLA servers (port 3000)
- **robot-arm**: Generic robotic arm controller (port 50054)
- **teleshake**: Plate shaker controller (port 50050)
- **gen5**: Plate reader controller (port 50053)
- **platform_status_db**: PostgreSQL database for tracking platform status
- **database**: PostgreSQL backend

## Development Commands

### Running the System
```bash
# Start all services
docker compose up

# Build and start (after code changes)
docker compose up --build
```

### SELinux Configuration (Fedora/RHEL)

On systems with SELinux enabled (Fedora, RHEL, CentOS), Docker bind mounts require special handling:

1. **Volume mounts must use SELinux labels**: Add `:z` (shared) or `:Z` (private) suffix to bind mounts
   ```yaml
   volumes:
     - ./laborchestrator/:/opt/vu_lab/:z  # :z for shared access
   ```

2. **Database volumes**: Use Docker-managed named volumes instead of bind mounts to avoid permission issues
   ```yaml
   volumes:
     - pgdata:/var/lib/postgresql/data  # Named volume, not ./pgdata
   ```

All bind mounts in this repository are already configured with `:z` flags. The postgres database uses a named volume (`pgdata`) to avoid SELinux mount propagation errors.

### Testing and Linting
```bash
# Install development dependencies
python -m pip install .[dev,publishing]

# Run tests
pytest
pytest -v  # verbose output

# Lint code
ruff check
ruff format --check

# Format code
ruff format

# Run full build
python -m build
```

### Python Environment
Python 3.11+ required. Uses `uv.lock` for dependency management.

## Architecture

### Orchestration Layer (`laborchestrator/`)

The orchestration system is the core of this lab automation setup:

- **`start_script.py`**: Entry point that initializes the Orchestrator with PythonLab reader and starts the Dash web interface (port 8050)
- **`config.py`**: Configuration hub that wires together:
  - Database client (StatusDBImplementation)
  - Custom Worker implementation
  - Process module location
  - Scheduler settings (uses BottleneckPD algorithm by default)
  - Lab configuration path

### Worker System (`laborchestrator/vu_lab/worker_adaption.py`)

The Worker class is the bridge between the orchestrator and physical devices:

- Extends `WorkerInterface` to execute process steps on real or simulated devices
- Manages SiLA client connections with automatic discovery and health checking
- `USE_REAL_SERVERS` list controls which devices run real vs simulated
- `device_wrappers` maps device names to wrapper classes
- `execute_process_step()`: Routes commands to appropriate device wrapper or simulation
- `get_client()`: Discovers and maintains SiLA server connections
- `process_step_finished()`: Post-processing hook (e.g., barcode reading)
- Simulated devices use DummyHandler with random 2-12 second delays

### Device Wrappers (`laborchestrator/vu_lab/wrappers/`)

Device wrappers translate high-level process steps into device-specific SiLA commands:

- **`device_interface.py`**: Abstract base class defining the `get_SiLA_handler()` interface
- **`generic_robot_arm_wrapper.py`**: Implements commands for the generic robotic arm
- Each wrapper returns an Observable that the orchestrator can monitor for completion

### Process Definitions (`laborchestrator/vu_lab/processes/`)

Process files define lab workflows using the PythonLab framework:

- Inherit from `BasicProcess` (which extends `PLProcess`)
- Define required resources (plates, reagents, storage, movers)
- Specify workflow steps and their execution order
- **`basic_process.py`**: Base class providing common initialization
- **`empty_process.py`**: Template for creating new processes
- New processes are automatically discovered via the `processes` module

### Configuration Files

- **`platform_config.yaml`**: Defines the lab layout (storage capacity, movers) and maps to PythonLab resource types
- **`settings.py`**: Django database settings for platform_status_db
- **Root-level files**: Mounted into laborchestrator container as `/opt/vu_lab/`
- **`laborchestrator/` symlinks**: `platform_config.yaml` and `settings.py` are symlinked from root

### SiLA Device Containers

Each device runs as a separate container with its own SiLA server:
- **teleshake/**: Uses codegen.sh to generate SiLA2 server code
- **robot-arm/**: Runs genericroboticarm in simulation mode by default (change ROBOT_IP for real hardware)
- **gen5/**: Private connector for Gen5 plate reader (requires .env configuration)

## Key Integration Points

1. **Adding a new device**:
   - Create wrapper in `laborchestrator/vu_lab/wrappers/`
   - Add to `device_wrappers` and `sila_server_name` in `worker_adaption.py`
   - Add to `USE_REAL_SERVERS` if not simulated
   - Update `platform_config.yaml` if it's a new resource type

2. **Creating a new process**:
   - Copy `empty_process.py` in `laborchestrator/vu_lab/processes/`
   - Define resources in `create_resources()`
   - Implement workflow logic
   - Module is auto-discovered via `config.py`

3. **Scheduler integration**:
   - Scheduler reads lab config from `platform_config.yaml`
   - Orchestrator communicates via SiLA2 to scheduler service
   - Algorithm can be changed in `config.py` (scheduling_algorithm)

## Important Notes

- The system uses host networking mode for all containers
- Database credentials: `platform_status/platform_status` (dev only)
- Web interfaces available at localhost:3000 (browser), :8050 (orchestrator), :8055 (robot)
- Ruff excludes `worker_adaption.py` from some lint rules (see pyproject.toml)
- Gen5 connector requires environment configuration (see gen5/.env.example)