"""Duplicate this file and add/modify the missing parts to create a new resource"""

import logging
from pythonlab.resource import ServiceResource

DURATION = 10
FREQUENCY = 10
NUM_BEDS = 1
PRIORITY = 3


class ScannerResource(ServiceResource):
    """
    Flatbed scanner resource as a service.

    :param Resource: [description]
    :type Resource: [type]
    """

    def __init__(self, proc, name: str = "Scanner"):
        super().__init__(proc=proc, name=name)

        self._resolution = 640

    def init(self):
        logging.debug(f"init {self.name}")

    def scan(
        self,
        container: ServiceResource,
        resolution: int,
        **kwargs,
    ):
        kwargs.update(
            {
                "fct": "scan",
                "resolution": resolution,
            }
        )

        print(f"==[ Scan invoked.")
        self.proc.add_process_step(self, [container], **kwargs)
