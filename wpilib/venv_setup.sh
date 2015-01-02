#!/bin/bash

# Set up virtualenv for Python 3 and pytest.
# -> On Linux/OSX, consider using virtualenv-wrapper instead

cd `dirname $0`
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r testing-requirements.txt
pip install -e .
