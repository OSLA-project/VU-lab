# pylint: disable=missing-class-docstring

from unitelabs.cdk.features.core.simulation_controller import (
    SimulationControllerBase,
    StartRealModeFailed,
    StartSimulationModeFailed,
)
from .io import Gen5OleCommandProtocol, UnsupportedPlatformError


class SimulationController(SimulationControllerBase):
    # pylint: disable=missing-class-docstring
    def __init__(self, protocol: Gen5OleCommandProtocol):
        super().__init__()
        self.protocol = protocol

    def start_simulation_mode(self):
        if self.protocol.simulation:
            raise StartSimulationModeFailed(description="Already in simulation mode")
        self.protocol.simulation = True
        self.protocol.reinitialize()

    def start_real_mode(self):
        if not self.protocol.simulation:
            raise StartRealModeFailed(description="Already in real mode")
        self.protocol.simulation = False
        try:
            self.protocol.reinitialize()
        except UnsupportedPlatformError as error:
            self.protocol.simulation = True
            self.protocol.reinitialize()
            raise StartRealModeFailed(
                description="Failed to start real mode because your connector is running on an UnsupportedPlatform."
            ) from error

    def simulation_mode(self) -> bool:
        return self.protocol.simulation
