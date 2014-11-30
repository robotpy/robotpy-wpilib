#!/bin/bash

set -e
cd `dirname $0`

if [ "$1" == "" ]; then
	echo "Usage: $0 path/to/allwpilib"
	exit 1
fi

ALLWPILIB_PATH=$1
MSG_PATH=$ALLWPILIB_PATH/simulation/frc_gazebo_plugins/msgs/proto

rm *_pb2.py || true
protoc --proto_path $MSG_PATH $MSG_PATH/*.proto --python_out=.
