import sys
import time
import config
from laborchestrator.logging_manager import StandardLogger as Logger
from laborchestrator.old_dash_app import SMDashApp
from laborchestrator.orchestrator_implementation import Orchestrator

from platform_status_db.larastatus.status_db_implementation import (
    StatusDBImplementation,
)
from pathlib import Path


def add_lab_setup_to_db(platform_config_path) -> None:
    """
    Use this script to populate the database with devices and positions according to the lab_config file.
    It does not check whether devices already exists. So, running this multiple times results in duplicate database entries.
    You can remove all present devices and positions running the wipe_lab command.
    """
    lab_config_file = Path(platform_config_path).resolve()
    # creates a client for the database
    db_client = StatusDBImplementation()
    # clear the database, if necessary
    db_client.wipe_lab()

    print("Populating the database with config from:", lab_config_file)
    # populates the database
    db_client.create_lab_from_config(lab_config_file.as_posix())



def main() -> None:
    """Main function to start the orchestrator and scheduler with a dash app."""

    # Fill the database
    platform_config_path = Path(config.lab_config_file)

    add_lab_setup_to_db(platform_config_path)

    if config.worker:
        orchestrator = Orchestrator(reader="PythonLab", worker_type=config.worker)
    else:
        orchestrator = Orchestrator(reader="PythonLab")
    orchestrator.schedule_manager.time_limit_short = config.default_scheduling_time

    # create and run dash app until eternity
    dash_app = SMDashApp(orchestrator, port=8050, process_module=config.process_module)
    dash_app.run()

    # add database client
    if config.db_client:
        orchestrator.inject_db_interface(config.db_client)

    # configure scheduler
    # try to find a running scheduler server and set its lab configuration:
    try:
        from labscheduler.sila_server import Client as SchedulerClient

        scheduler = SchedulerClient.discover(insecure=True, timeout=5)
        if config.scheduling_algorithm:
            available_algorithms = scheduler.SchedulingService.AvailableAlgorithms.get()
            if config.scheduling_algorithm in [algo.Name for algo in available_algorithms]:
                scheduler.SchedulingService.SelectAlgorithm(config.scheduling_algorithm)
            else:
                Logger.warning(
                    f"Algorithm {config.scheduling_algorithm} is not available in scheduler.",
                )
        # get the absolute filepath
        with platform_config_path.open() as reader:
            scheduler.LabConfigurationController.LoadJobShopFromFile(reader.read())
        Logger.info("Configured the lab of the scheduling service")
    except ModuleNotFoundError as mnfe:
        Logger.warning(f"Scheduler seems to be not installed:\n{mnfe}")
    except TimeoutError:
        Logger.warning(
            "Could not find a running scheduler server. You will have to configure the lab manually.",
        )

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
