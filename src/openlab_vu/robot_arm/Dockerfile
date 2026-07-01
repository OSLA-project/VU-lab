FROM python:3.11

ENV PORT=50054
ENV ADDITIONAL_PARAMS=""
ENV HOST=0.0.0.0
RUN python -m pip install --upgrade pip
RUN python -m pip install "xarm-python-sdk==1.16.0"

COPY ./new_graphs/* /root/.config/GenericRoboticArm/

COPY . /opt/custom_arm/
RUN pip install /opt/custom_arm/
