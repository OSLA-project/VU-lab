FROM python:3.11

ENV SILA_SERVER__NAME='Gen5'
ENV SILA_SERVER__UUID = 5d902dfb-f4e6-41b4-8fa7-4fc5c6ff555a
ENV SILA_SERVER__HOST = 0.0.0.0
ENV SILA_SERVER__PORT = 50001

COPY ./gen5 /opt/gen5/

RUN python -m pip install /opt/gen5

CMD connector start
