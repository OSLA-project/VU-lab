"""Duplicate this file and add/modify the missing parts to create new processes"""

from pythonlab.process import PLProcess
from vu_lab.processes.basic_process import BasicProcess
from pythonlab.resource import LabwareResource

DURATION = 10
FREQUENCY = 10
NUM_BEDS = 1
PRIORITY = 3


class ScannerResource(LabwareResource):

    def scan(
        self,
        container: LabwareResource,
        resolution: int,
        **kwargs,
    ):
        kwargs.update(
            {
                "fct": "scan",
                "resolution": resolution,
            }
        )

        self.proc.add_process_step(self, [container], **kwargs)
        print(f"==[ Scan invoked.")
