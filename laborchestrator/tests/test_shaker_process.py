from pythonlab.pythonlab_reader import PLProcessReader

from vu_lab.processes.shaker_process import ShakerProcess


def test_all_containers_handled():
    # Bit of a pointless tests but checks if all planned containers will actually be handled
    process = ShakerProcess(num_plates=6)

    simulator = PLProcessReader.parse_process(process)
    assert len(process.containers) == len(simulator.containers)
