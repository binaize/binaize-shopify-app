#!/usr/bin/env bash

# --------------------------------------------------------------------------------------------------
# start web service to provide rest end points for this container at 8080
# --------------------------------------------------------------------------------------------------

gunicorn --pythonpath / -b 0.0.0.0:$SERVICE_PORT -k gevent -t $SERVICE_TIMEOUT -w $WORKER_COUNT application_platform.deployment.server:app


