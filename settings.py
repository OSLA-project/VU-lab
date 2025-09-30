import os
from platform_status_db.larastatus.settings import *  # noqa: F403

db_host = "172.17.0.1" if os.name == "posix" else "host.docker.internal"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "platform_status_db",
        "USER": "platform_status",
        "PASSWORD": "platform_status",
        "HOST": "172.17.0.1",
        "PORT": "5432",
    },
}
