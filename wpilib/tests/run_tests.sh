#!/bin/bash

set -e
cd `dirname $0`

abspath() {
	echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# Not strictly necessary if testing-requirements was installed...
PYTHONPATH=$(abspath ./..):$(abspath ../../hal-sim):$(abspath ../../hal-base):$PYTHONPATH

PYTHONPATH="$PYTHONPATH" python3 -m pytest $@
