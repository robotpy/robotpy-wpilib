#!/bin/bash
cd /src
python --version
pip --version
pip install -U pip
pushd wpilib; pip install -r travis-requirements.txt; popd
pip install -r docs/requirements.txt
wpilib/tests/run_tests.sh
pushd docs && make html && popd
