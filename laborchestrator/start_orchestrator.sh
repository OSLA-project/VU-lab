#!/usr/bin/env bash

pip install git+https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git
pip install git+https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git
pip install psycopg2-binary

./start_script.py