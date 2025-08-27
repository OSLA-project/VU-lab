# pylint: disable=missing-class-docstring

from unitelabs.cdk import sila

from .features.door_controller import DoorControllerBase, ReadInProgressError
from .io import Gen5OleCommandProtocol


class DoorController(DoorControllerBase):
    def __init__(self, protocol: Gen5OleCommandProtocol):
        super().__init__()
        self.protocol = protocol

    async def subscribe_door_open(self):
        self.protocol.door_open_change_event.clear()
        yield self.protocol.door_open
        while True:
            await self.protocol.door_open_change_event.wait()
            self.protocol.door_open_change_event.clear()
            yield self.protocol.door_open

    async def get_door_open_once(self):
        return self.protocol.door_open

    async def open_door(self, *, status, intermediate):
        if self.protocol.door_open and self.protocol.door_open is not None:
            status.update(
                progress=1,
                remaining_time=sila.datetime.timedelta(0),
            )
            intermediate.send("Door already open")
            return self.protocol.door_open, "Door already open"
        status.update(
            progress=0,
            remaining_time=sila.datetime.timedelta(0),
        )
        intermediate.send("Door opening")
        try:
            self.protocol.carrier_out()
        except RuntimeError as error:
            raise ReadInProgressError(description="Cannot open door while read is in progress") from error
        self.protocol.door_open = True
        self.protocol.door_open_change_event.set()
        status.update(
            progress=1,
            remaining_time=sila.datetime.timedelta(0),
        )
        return self.protocol.door_open, "Door open"

    async def close_door(self, *, status, intermediate):
        if not self.protocol.door_open and self.protocol.door_open is not None:
            status.update(
                progress=1,
                remaining_time=sila.datetime.timedelta(0),
            )
            intermediate.send("Door already closed")
            return self.protocol.door_open, "Door already closed"
        status.update(
            progress=0,
            remaining_time=sila.datetime.timedelta(0),
        )
        intermediate.send("Door closing")
        try:
            self.protocol.carrier_in()
        except RuntimeError as error:
            raise ReadInProgressError(description="Cannot close door while read is in progress") from error
        self.protocol.door_open = False
        self.protocol.door_open_change_event.set()
        status.update(
            progress=1,
            remaining_time=sila.datetime.timedelta(0),
        )
        return self.protocol.door_open, "Door closed"
