#!/bin/bash

source .venv/bin/activate
gunicorn api:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --error-logfile - --access-logfile -
