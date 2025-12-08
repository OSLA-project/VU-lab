FROM python:3.11

ENV PORT=50054
ENV ADDITIONAL_PARAMS=""
ENV HOST=0.0.0.0
RUN python -m pip install --upgrade pip
RUN python -m pip install xarm-python-sdk==1.17.0


RUN git clone https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git /opt/genericroboticarm

COPY ./default_graphs/* /opt/genericroboticarm/genericroboticarm/graphs/

WORKDIR /opt/genericroboticarm

RUN pip install -e .

CMD python -m genericroboticarm --port 50054 -r XArm --address 0.0.0.0 --robot-ip