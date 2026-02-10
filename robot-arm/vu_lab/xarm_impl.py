from genericroboticarm.robo_APIs.xfactory import XArmImplementation


class VULabArm(XArmImplementation):
    @classmethod
    def get_name(cls) -> str:
        return "VULabArm"

    def site_to_position_identifier(self, device: str, slot: int) -> str:
        """Convert device and slot to position identifier used in VU lab."""
        # the shakers have a different naming convention, so we need to handle them separately
        if device.startswith("shaker"):
            return f"shaker_{slot}_d_pos_1"

        if slot > 0:
            return f"{device}_{slot}"
        else:
            return device
