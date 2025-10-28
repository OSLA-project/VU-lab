"""Config file for vu lab orchestrator.""" # noqa: INP001

from pathlib import Path
# Change db_client to None to not use any database or
# change it to your own implementation of laborchestrator.database_integration.status_db_interface.StatusDBInterface
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from vu_lab.worker_adaption import Worker

db_client = StatusDBImplementation()

# worker = None  # uncomment to use the default worker (i.e., just simulation) # noqa: ERA001
worker = Worker  # uncomment to use your customized worker

# lab_config to be sent to the scheduler
lab_config_file = Path(__file__).resolve().parent.parent / "lab_adaption" / "platform_config.yaml"

# controls the default time limit the orchestrator gives the scheduler for computing new schedules
# It can be changed via GUI at runtime
default_scheduling_time = 1  # seconds

# change to a solver name like CP-Solver or BottleneckPD which will be chosen on the scheduler.
# None keeps the schedulers default
scheduling_algorithm: str | None = "BottleneckPD"

# change this to the module where you save your pythonLab processes
from vu_lab import processes  # noqa: E402

process_module = processes
