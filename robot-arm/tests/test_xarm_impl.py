from vu_lab.xarm_impl import VULabArm


def test_no_slot_num_for_single_slot():
    arm = VULabArm()
    position_id = arm.site_to_position_identifier("shaker_1", 0)
    assert position_id == "shaker_1"


def test_slot_num_for_multiple_slots():
    arm = VULabArm()
    position_id = arm.site_to_position_identifier("hotel_1", 3)
    assert position_id == "hotel_1_3"
