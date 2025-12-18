#!/usr/bin/env python3

import argparse
import importlib
from laborchestrator.logging_manager import StandardLogger as Logger
from pythonlab.pythonlab_reader import PLProcessReader



def main() -> None:
    """Load a process file as a module path and class and parse it with PythonLab."""
    parser = argparse.ArgumentParser(description="Load a PythonLab process file.")
    parser.add_argument(
        "process_module",
        type=str,
        help="Path of the proces class file to load.",
    )
    parser.add_argument(
        "process_class",
        type=str,
        help="Name of the proces class to load.",
    )

    args = parser.parse_args()
    process_module = importlib.import_module(args.process_module)
    process_class = getattr(process_module, args.process_class)

    reader = PLProcessReader()
    reader.parse_process_from_instance(process_class())

    logger.info("Process succesfully parsed!")


if __name__ == "__main__":
    main()
