#!/bin/bash

set -e
cd `dirname $0`

abspath() {
	echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# Not strictly necessary if testing-requirements was installed...
PYTHONPATH=$(abspath ./..):$(abspath ../../hal-sim):$(abspath ../../hal-base):$PYTHONPATH

python3 -m coverage run --source wpilib -m pytest $@
python -m coverage report -m


EXAMPLES="
	iterative/
	sample/
	test/
	
	examples/CANTalon/
	examples/CANTalonPID/
	examples/GettingStarted/
	examples/MecanumDrive/
	examples/MotorControl/
	
	examples/QuickVision/
	examples/TankDrive/
"

# Doesn't work right now:
# - examples/GearsBot/
# - examples/pacgoat/

if [ -z "${NOPYFRC}" ]; then
	for example in $EXAMPLES; do
		pushd ../../examples/$example
		python3 robot.py test --builtin
		popd
	done
fi

