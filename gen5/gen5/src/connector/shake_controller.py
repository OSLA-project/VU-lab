import os
import asyncio

from .features.shake_controller import (
    ShakeControllerBase,
    ReadInProgressError,
    ExperimentAlreadyOpenError,
    InvalidParameterError,
    NoActivePlateError,
    NoActiveShakeError,
    ShakeStartError,
)
from .io import Gen5OleCommandProtocol


def error_handler(func):
    """
    Decorator to handle all the errors thrown by the io layer.
    """

    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except RuntimeError as error:
            if "This action cannot be performed while a read is in progress." in str(error):
                raise ReadInProgressError(description=str(error)) from error
            if "Error starting measurement." in str(error):
                raise ShakeStartError from error
            raise error
        except TypeError as error:
            if "None is not a valid active plate" in str(error):
                raise NoActivePlateError(description=str(error)) from error
            raise error
        except ValueError as error:
            if "No read in progress to abort" in str(error):
                raise NoActiveShakeError(description=str(error)) from error

    return wrapper


class ShakeController(ShakeControllerBase):
    # pylint: disable=missing-class-docstring
    def __init__(self, protocol: Gen5OleCommandProtocol):
        super().__init__()
        self.protocol = protocol

    @error_handler
    async def start_shake_step(self, mode, duration_sec, displacement_mm, orbital_speed):
        modes = {
            0: "Linear",
            1: "Orbital",
            2: "DoubleOrbital",
        }
        orbital_speeds = {
            0: "Slow",
            1: "Fast",
        }
        try:
            procedure = f"""
                <BTIProcedure Version="1.00">
                    <Labware>
                        <Type>Microplate</Type>
                        <Name>96 WELL PLATE</Name>
                        <UseLid>true</UseLid>
                    </Labware>
                    <StepList>
                        <ShakeStep>
                            <Mode>{modes[mode]}</Mode>
                            <DurationSec>{duration_sec}</DurationSec>
                            <DisplacementMM>{displacement_mm}</DisplacementMM>
                            {f'<OrbitalSpeed>{orbital_speeds[orbital_speed]}</OrbitalSpeed>' if mode in [1, 2] else ''}
                        </ShakeStep>
                    </StepList>
                </BTIProcedure>
            """
            if self.protocol.experiment:
                raise ExperimentAlreadyOpenError(
                    description="An experiment is already open. Please (save and) close the current experiment before "
                    "creating a new one."
                )
            self.protocol.new_experiment(os.path.abspath(".\\src\\connector\\features\\empty.prt"), "")
            self.protocol.activate_plate(self.protocol.get_plate_list()[0])
            self.protocol.set_procedure(procedure)
            validation, message = self.protocol.validate_procedure(False)
            if validation != 1:
                raise InvalidParameterError(description=message)
            self.protocol.start_read()
        except KeyError as error:
            raise InvalidParameterError(description=str(error)) from error
        except RuntimeError as error:
            if "This action cannot be performed while a read is in progress." in str(error):
                raise ReadInProgressError(description=str(error)) from error
            if "An experiment is already open" in str(error):
                raise ExperimentAlreadyOpenError(description=str(error)) from error
            raise error

    @error_handler
    async def abort_shake(self):
        self.protocol.abort_read()
        while self.protocol.get_read_status() in (1, 3):
            await asyncio.sleep(0.5)
        final_status = self.protocol.get_read_status()
        return (
            "Measurement aborted with final read status "
            + str(final_status)
            + " (0: Not started, 1: In progress, 2: Aborted, 3: Paused, 4: Error, 5: Completed)."
        )

    @error_handler
    async def get_shake_in_progress(self):
        return self.protocol.get_read_in_progress()
