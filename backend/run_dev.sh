#!/usr/bin/env bash
uvicorn main:app --reload --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
