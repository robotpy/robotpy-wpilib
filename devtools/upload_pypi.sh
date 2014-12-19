#!/bin/bash

set -e 
cd `dirname $0`
source _gitver.sh

echo "Starting upload process for RobotPy $VERSION"

cd ..

# Run the tests (even though Travis-CI will do this, can't hurt)
echo "Running tests"
wpilib/tests/run_tests.sh

# Test that all the packages can be built
echo "Testing package build"
for i in hal-base hal-roborio wpilib; do 
    pushd $i
    python setup.py sdist
    popd
done

# Ok, actually upload them now
echo "Doing upload!"
for i in hal-base hal-roborio wpilib; do 
    pushd $i
    #python setup.py sdist upload
    popd
done

echo "Success!"
