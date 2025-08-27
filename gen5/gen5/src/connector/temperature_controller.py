# pylint: disable=missing-class-docstring

from unitelabs.cdk import sila

from .features.temperature_controller import TemperatureControllerBase
from .io import Gen5OleCommandProtocol


class TemperatureController(TemperatureControllerBase):
    # pylint: disable=missing-class-docstring
    def __init__(self, protocol: Gen5OleCommandProtocol):
        super().__init__()
        self.protocol = protocol
        self.target_temperature: int = self.protocol.get_temperature_set_point()[0]
        self.incubating: bool = False

    async def subscribe_current_temperature(self):
        self.protocol.publish_temperature_reads()
        yield self.protocol.current_temperature

        self.protocol.subscribe_current_temperature()
        try:
            while True:
                await self.protocol.current_temperature_event.wait()
                yield self.protocol.current_temperature
        finally:
            self.protocol.unsubscribe_current_temperature()

    async def get_target_temperature(self):
        return self.target_temperature

    async def set_target_temperature(self, target_temperature):
        """
        Sets the target temperature, while not automatically turning incubation on.
        Use turn_incubation_on() to turn incubation on.
        """
        self.target_temperature = target_temperature
        self.protocol.set_temperature_set_point(self.incubating, self.target_temperature, 0)

    @sila.UnobservableProperty()
    async def get_incubation_on(self) -> bool:
        """
        Returns whether the heating and/or cooling element is on.
        """
        return self.incubating

    @sila.UnobservableCommand()
    async def turn_incubation_off(self):
        """
        Turn the heating and/or cooling element off.
        """
        self.incubating = False
        self.protocol.set_temperature_set_point(False, self.target_temperature, 0)

    @sila.UnobservableCommand()
    async def turn_incubation_on(self):
        """
        Turn the heating and/or cooling element on.
        """
        self.incubating = True
        self.protocol.set_temperature_set_point(True, self.target_temperature, 0)
