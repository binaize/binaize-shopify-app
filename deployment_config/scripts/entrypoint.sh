#!/usr/bin/env bash

# --------------------------------------------------------------------------------------------------
# start web service to provide rest end points for this container at 8080
# --------------------------------------------------------------------------------------------------

gunicorn --pythonpath / -b 0.0.0.0:8000 -k gevent -t 300 -w 1 application_platform.deployment.server:app


