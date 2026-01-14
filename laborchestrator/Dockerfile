FROM registry.gitlab.com/openlabautomation/lab-automation-packages/laborchestrator:caba9ba1a15ed88242179f7b559ce3058045469a

RUN pip install 'pyscipopt>=5.3.0'\
    'ortools==9.9.3963'\
    psycopg2-binary\
    git+https://gitlab.com/OpenLabAutomation/lab-automation-packages/lab-scheduler.git\
    git+https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git\
    git+https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git\
