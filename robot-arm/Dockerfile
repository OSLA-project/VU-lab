FROM python:3.11

ENV PORT=50054
ENV ADDITIONAL_PARAMS=""
ENV HOST=0.0.0.0
RUN python -m pip install --upgrade pip
RUN python -m pip install "xarm-python-sdk==1.16.0"


COPY ./default_graphs/* /opt/genericroboticarm/graphs/

WORKDIR /opt/genericroboticarm
RUN git clone https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git

WORKDIR /opt/genericroboticarm/genericroboticarm
RUN pip install -e .
