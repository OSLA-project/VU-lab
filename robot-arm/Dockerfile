FROM python:3.11

ENV PORT=50054
ENV ADDITIONAL_PARAMS=""
ENV HOST=0.0.0.0
ENV ROBOT_IP=""
RUN python -m pip install --upgrade pip
RUN python -m pip install xarm-python-sdk


RUN git clone https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git /opt/genericroboticarm

WORKDIR /opt/genericroboticarm

RUN pip install -e .

CMD python -m genericroboticarm --port 50054 -r XArm --address 0.0.0.0 --robot-ip $ROBOT_IP