#!/bin/bash
#
# Builds a release, copies them to the pip_cache, and uses the
# installer to install it on a roborio
#

# TODO: This requires a pynetworktables release to already be
# installed, or it must be present in the pip_cache

set -e
cd `dirname $0`
source _windows_env.sh

cd ..
VERSION=`git describe --tags --dirty='--dirty'`

if [[ ! $VERSION =~ ^[0-9]+\.[0-9]\.[0-9]+$ ]]; then
    # Convert to PEP440
    IFS=- read VTAG VCOMMITS VLOCAL <<< "$VERSION"
    if [ -z $VCOMMITS ]; then VCOMMITS=0; fi
    VERSION=`printf "%s.post0.dev%s" $VTAG $VCOMMITS`
fi

echo "Installing $VERSION"

PIP_CACHE="pip_cache/"

[ -d $PIP_CACHE ] || mkdir $PIP_CACHE

for i in hal-base hal-roborio wpilib; do 
    pushd $i
    python3 setup.py sdist --formats=gztar
    popd
done

cp hal-base/dist/robotpy-hal-base-$VERSION.tar.gz $PIP_CACHE
cp hal-roborio/dist/robotpy-hal-roborio-$VERSION.tar.gz $PIP_CACHE
cp wpilib/dist/wpilib-$VERSION.tar.gz $PIP_CACHE

# Run the install now
python3 -m robotpy_installer install -U --no-deps --force-reinstall robotpy-hal-base==$VERSION robotpy-hal-roborio==$VERSION wpilib==$VERSION
