FROM python:3.12-slim
RUN apt update && apt install -y git

RUN git clone https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git /opt/platform_status_db
WORKDIR /opt/platform_status_db
COPY ./init_db.sh /opt/platform_status_db/init_db.sh
RUN pip install psycopg2-binary -e .

CMD bash init_db.sh
