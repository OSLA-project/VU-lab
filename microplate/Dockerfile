FROM python:3.11

RUN git clone --depth 1 https://github.com/OSLA-project/microplate.git /opt/microplate/
WORKDIR /opt/microplate

RUN pip install .

CMD python -m microplate --port 50099 --insecure
