FROM python:3.12

ENV PORT=50050
#ENV PRIVATE_KEY=/certs/teleshake.key
#ENV CERT_FILE=/certs/teleshake.pem
ENV ADDRESS=teleshake

RUN python -m pip install --upgrade pip
RUN git clone https://github.com/OSLA-project/Teleshake-1536.git /opt/teleshake

RUN sed -i 's/\r$//' /opt/teleshake/codegen.sh
WORKDIR /opt/teleshake
RUN python -m pip install .

CMD python -m sila2_driver.thermoscientific.teleshake1536 --port $PORT --debug --insecure