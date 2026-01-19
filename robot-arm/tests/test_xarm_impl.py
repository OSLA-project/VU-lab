from robot_arm.vu_lab.xarm_impl import VULabArm

SINGLE_SLOT_LOCATION = ""

def test_no_slot_num_for_single_slot():

    arm = VULabArm()
    position_id = arm.site_to_position_identifier("robot_arm", 0)
    assert position_id == "robot_arm"