from typing import Any
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.structures import ContainerInfo
from laborchestrator.structures import ProcessStep
from sila2.client import SilaClient
from vu_lab.wrappers import DeviceInterface


class ShakerWrapper(DeviceInterface):
    """Wrapper for the Thermo Scientific Teleshake 1536 SiLA2 server."""

    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: SilaClient,
        **kwargs: dict[str, Any],
    ) -> Observable:
        """Provides an Observable for shaking a container for the duration and speed specified in the step data.

        Expected keys in step.data:
            duration (int): shaking duration in seconds (default: 60)
            frequency (float): target speed in RPM (default: 6000)
            power (float): target power in percent 0-100 (default: 80)

        Expected keys in kwargs (injected by worker_adaption from device name):
            shaker_id (int): 0-indexed daisy-chain address of the target shaker (default: 0)
        """
        shaker_id = int(kwargs.get("shaker_id", step.data.get("shaker_id", 0)))
        duration = int(step.data.get("duration", 60))
        target_speed = float(step.data.get("frequency", 6000))
        target_power = float(step.data.get("power", 80))

        return sila_client.ShakeController.ShakeForTime(
            ShakerId=shaker_id,
            Runtime=duration,
            TargetSpeed=target_speed,
            TargetPower=target_power,
        )
