#!/bin/bash

# Set up virtualenv for Python 3 and pytest.

virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install pytest-cov
pip install -e .
