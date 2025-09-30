"""Duplicate this file and add/modify the missing parts to create new processes."""

from lab_adaption.processes.basic_process import BasicProcess


class InterestingExample(BasicProcess):
    def __init__(self):
        super().__init__(priority=3, num_plates=3, process_name="InterestingExample")

    def init_service_resources(self) -> None:
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i)

    def judge_answer(self, answer) -> bool:
        # extract the number from the response
        number = answer.Response.value
        # return whether the number is even
        return number % 2 == 0

    def process(self) -> None:
        # loop through all containers
        for cont in self.containers:
            # move all containers to hotel2 and read their barcodes
            self.robot_arm.move(cont, self.hotel2, read_barcode=True)
            # move all containers to the human for inspection (it can hold up to two)
            self.robot_arm.move(cont, self.human)
            # have the human assign a number to each container
            answer = self.human.request_number(
                cont,
                message=f"assign number to {cont.name}!",
            )
            # do some computation on the result
            judgement = self.judge_answer(answer)
            # depending on the result, put the labware in hotel1 or hotel 3
            if judgement:
                self.robot_arm.move(cont, self.hotel3)
            else:
                self.robot_arm.move(cont, self.hotel1)
