from genericroboticarm.robo_APIs.xfactory import XArmImplementation


class VULabArm(XArmImplementation):

    def site_to_position_identifier(self, device: str, slot: int):
        if slot > 0:
            return f"{device}{slot}"
        else:
            return device
