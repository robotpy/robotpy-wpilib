#!/bin/bash

set -e
cd `dirname $0`

PYTHONPATH=..:../../hal-sim:../../hal-base python3 -m coverage run --source wpilib -m pytest $@
python -m coverage report -m

