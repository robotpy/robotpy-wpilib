#!/bin/bash

cd $(dirname $0)
python ../wpilib/tests/spec_scanners/hal_scanner.py ../../allwpilib/hal/src/main/native/include "$@"
