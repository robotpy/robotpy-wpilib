#!/bin/bash

set -e
cd `dirname $0`

_inst() {
	pushd $1
	pip install -e . --no-deps
	popd	
}

_inst ../wpilib
_inst ../hal-base
_inst ../hal-sim
