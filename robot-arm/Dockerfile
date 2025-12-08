FROM python:3.11

ENV PORT=50054
ENV ADDITIONAL_PARAMS=""
ENV HOST=0.0.0.0
RUN python -m pip install --upgrade pip
RUN python -m pip install "xarm-python-sdk==1.16.0"


RUN pip install genericroboticarm --index-url https://gitlab.com/api/v4/projects/59230771/packages/pypi/simple

COPY ./default_graphs/* /opt/genericroboticarm/genericroboticarm/graphs/

WORKDIR /opt/genericroboticarm

CMD python -m genericroboticarm --port 50054 -r XArm --address 0.0.0.0 --robot-ip $ROBOT_IP