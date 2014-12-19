#!/bin/bash
#
# Builds a release, copies them to the pip_cache, and uses the
# installer to install it on a roborio
#

# TODO: This requires a pynetworktables release to already be
# installed, or it must be present in the pip_cache

set -e

cd `dirname $0`/..
VERSION=`git describe --tags --dirty='-dirty'`

PIP_CACHE="installer/pip_cache/"

[ -d $PIP_CACHE ] || mkdir $PIP_CACHE

for i in hal-base hal-roborio wpilib; do 
    pushd $i
    python setup.py sdist
    popd
done

cp hal-base/dist/robotpy-hal-base-$VERSION.tar.gz $PIP_CACHE
cp hal-roborio/dist/robotpy-hal-roborio-$VERSION.tar.gz $PIP_CACHE
cp wpilib/dist/wpilib-$VERSION.tar.gz $PIP_CACHE

# Run the install now
python3 installer/installer.py install-robotpy --basever $VERSION --no-tools
