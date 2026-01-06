FROM python:3.11

ENV PORT=50050
#ENV PRIVATE_KEY=/certs/teleshake.key
#ENV CERT_FILE=/certs/teleshake.pem
ENV ADDRESS=teleshake

RUN python -m pip install --upgrade pip
RUN git clone https://gitlab.com/sila-driver-group/teleshake.git /opt/teleshake
COPY ./codegen.sh /opt/teleshake/codegen.sh
RUN sed -i 's/\r$//' /opt/teleshake/codegen.sh
RUN chmod +x /opt/teleshake/codegen.sh
WORKDIR /opt/teleshake
RUN python -m pip install -r dev-requirements.txt && \
    python -m pip install -e .

RUN /opt/teleshake/codegen.sh

CMD python -m sila2_driver.thermoscientific.teleshake1536 --port $PORT --debug --insecure