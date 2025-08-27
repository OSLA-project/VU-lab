import abc
import typing

from unitelabs.cdk import sila


class TemperatureControllerBase(sila.Feature, metaclass=abc.ABCMeta):
    """
    Control temperature by setting a target temperature that should be reached and held.
    """

    def __init__(self):
        super().__init__(
            originator="io.unitelabs",
            category="temperature",
            version="1.0",
            maturity_level="Draft",
        )

    @abc.abstractmethod
    @sila.ObservableProperty()
    async def subscribe_current_temperature(
        self,
    ) -> sila.Stream[
        typing.Annotated[
            float,
            sila.constraints.Unit(
                label="°C",
                offset=273.15,
                components=[
                    sila.constraints.UnitComponent(
                        unit=sila.constraints.SIUnit.KELVIN,
                    )
                ],
            ),
        ]
    ]:
        """Returns the currently measured temperature in °C."""

    @sila.UnobservableProperty()
    async def get_target_temperature(
        self,
    ) -> typing.Annotated[
        int,
        sila.constraints.Unit(
            label="°C",
            offset=273.15,
            components=[
                sila.constraints.UnitComponent(
                    unit=sila.constraints.SIUnit.KELVIN,
                )
            ],
        ),
    ]:
        """Returns the currently set target temperature in °C."""

    @sila.UnobservableCommand()
    async def set_target_temperature(
        self,
        target_temperature: typing.Annotated[
            int,
            sila.constraints.Unit(
                label="°C",
                offset=273.15,
                components=[
                    sila.constraints.UnitComponent(
                        unit=sila.constraints.SIUnit.KELVIN,
                    )
                ],
            ),
        ],
    ) -> None:
        """Set the target temperature in °C."""
