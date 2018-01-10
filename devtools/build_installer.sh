#!/bin/bash

set -e
cd `dirname $0`
source _windows_env.sh
source _gitver.sh

echo "Packaging RobotPy $VERSION"

cd ..
[ -d dist ] || mkdir dist

# Create a temporary directory, and populate it with things
tmpdir=`mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir'`

rpy_zipdir=robotpy-$VERSION
rpy_zipfile=robotpy-$VERSION.zip

rpy_tmpdir=$tmpdir/$rpy_zipdir

function cleanup {
	echo "Removing temporary directory"
	[ -d $tmpdir ] && rm -rf $tmpdir
}

trap "cleanup" EXIT

mkdir $rpy_tmpdir

cp README-dist.txt $rpy_tmpdir/README.txt
cp wpilib/LICENSE.txt $rpy_tmpdir

pushd $rpy_tmpdir

# Download + extract files from the installer
pip download --no-cache --disable-pip-version-check robotpy-installer -d .
tar --strip=2 -xf robotpy-installer*.tar.gz --wildcards '*/installer.py' '*/win32/*'
rm robotpy-installer*.tar.gz

find *

# Download the latest release of robotpy from the release sites
# -> This is intentionally NOT from local, bandwidth is cheap
# -> Use the git tag to figure out what release to download, and
#    can verify that it matches. This is here so we know that
#    we actually did the release correctly
python3 installer.py download-robotpy --basever $VERSION

# Finally, create a zipfile (not a tarball, windows users)
# -> Use python to create the zipfile because we know we have python, not
#    all systems have zip installed
cd ..
python3 -m zipfile -c $rpy_zipfile $rpy_zipdir
popd

mv $tmpdir/$rpy_zipfile dist

echo "Success!"
