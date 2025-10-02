#!/usr/bin/env bash

set -e
set -x

pytest

# four lines below are for coverage from fullstack fastapi template
# coverage run -m pytest
# coverage run -m pytest tests/
# coverage report
# coverage html --title "${@-coverage}"