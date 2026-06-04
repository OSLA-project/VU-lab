FROM python:3.12-slim
RUN apt update && apt install -y git

RUN pip install uulaborchestrator \
    psycopg2-binary \
    uulabscheduler \
    uupythonlab \
    'pyscipopt>=5.3.0' \
    'ortools==9.9.3963' \
    git+https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git \
    git+https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git

CMD ["python", "-m", "laborchestrator.start_script"]
