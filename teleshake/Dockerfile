FROM python:3.11

ENV PORT=50050
RUN python -m pip install --upgrade pip
RUN git clone https://gitlab.com/sila-driver-group/teleshake.git /opt/teleshake
COPY codegen.sh /opt/teleshake/codegen.sh
WORKDIR /opt/teleshake
RUN python -m pip install -r dev-requirements.txt && \
    python -m pip install -e .

RUN ./codegen.sh

# Start driver on port 50050
CMD python -m sila2_driver.thermoscientific.teleshake1536 --port $PORT

