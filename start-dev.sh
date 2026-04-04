#!/bin/bash

source .venv/bin/activate
uvicorn api:app --reload --host 0.0.0.0