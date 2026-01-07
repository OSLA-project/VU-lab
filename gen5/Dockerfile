FROM python:3.11

ENV CLOUD_SERVER_ENDPOINT__HOSTNAME=ffffffff-ffff-ffff-ffff-ffffffffffff.unitelabs.io
ENV CLOUD_SERVER_ENDPOINT__PORT=443
ENV CLOUD_SERVER_ENDPOINT__TLS=True
ENV SILA_SERVER__UUID=00000000-0000-0000-0000-000000000000
ENV SILA_SERVER__HOSTNAME=0.0.0.0
ENV SILA_SERVER__PORT=50001

ENV SILA_SERVER__NAME='Gen5'
ENV READER_TYPE='Synergy H1'
ENV CON_TYPE='USB'
ENV COM_PORT=0
ENV READER_SERIAL_NUMBER=''
ENV PROTOCOL_PATH=/opt/gen5/protocols
ENV SIMULATION=True

RUN unlink /bin/sh && ln -s /bin/bash /bin/sh
RUN dpkg --add-architecture i386
RUN apt update
RUN apt install -y bash-completion nano iproute2 g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386

COPY ./gen5 /opt/gen5/
WORKDIR /opt/gen5

RUN pip install pythonnet
RUN pip install uv && uv venv
RUN source .venv/bin/activate && uv pip install -e .

CMD uv run connector start --app unitelabs.gen5:create_app -v
