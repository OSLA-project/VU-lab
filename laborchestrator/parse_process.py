#! /usr/bin/env python3

from pythonlab.pythonlab_reader import PLProcessReader
import argparse

def main():
    argparser = argparse.ArgumentParser(description="Parse a PythonLab process file.")
    argparser.add_argument("file", type=str, help="Path to the PythonLab process")

    args = argparser.parse_args()
    simulator = PLProcessReader.parse_process_from_file_path(args.file)

    simulator.visualize_workflow_graph()

if __name__ == "__main__":
    main()