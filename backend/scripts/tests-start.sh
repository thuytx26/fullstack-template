#!/usr/bin/env bash

set -e
set -x

# Check if the database (DB) has started
# and wait until the DB is actually ready to accept connections (tenacity)
python app/prestart/tests_pre_start.py

bash scripts/test.sh "$@"