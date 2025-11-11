FROM python:3.11

COPY ./microplate /opt/microplate/
WORKDIR /opt/microplate

RUN pip install .

CMD python -m microplate --port 50099 --insecure
