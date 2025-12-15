FROM python:3.11

ENV SILA_SERVER__NAME='Gen5'
ENV SILA_SERVER__UUID=0797536e-1e6e-478e-983b-38425a7bf1d5
ENV SILA_SERVER__HOST=0.0.0.0
ENV SILA_SERVER__PORT=50053
ENV READER_TYPE='Synergy H1'
ENV CON_TYPE='USB'
ENV COM_PORT=0
ENV READER_SERIAL_NUMBER=''
ENV PROTOCOL_PATH=/opt/gen5/protocols
ENV SIMULATION=True

RUN unlink /bin/sh && ln -s /bin/bash /bin/sh

RUN apt update && apt install -y g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386 iproute2

COPY ./gen5 /opt/gen5/
WORKDIR /opt/gen5

RUN pip install pythonnet
RUN pip install uv && uv venv
RUN source .venv/bin/activate && uv pip install -e .

# CMD connector start --app connector:create_app -vvv
CMD uv run connector start --app unitelabs.gen5:create_app -v
