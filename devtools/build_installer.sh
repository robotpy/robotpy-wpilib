#!/bin/bash

set -e 
cd `dirname $0`
source _gitver.sh

echo "Packaging RobotPy $VERSION"

cd ../installer

# Download the latest version of the PuTTY tools
pushd win32
wget -N http://the.earth.li/~sgtatham/putty/latest/x86/plink.exe
wget -N http://the.earth.li/~sgtatham/putty/latest/x86/psftp.exe
popd


# Download the latest release of robotpy from the release sites
# -> This is intentionally NOT from local, bandwidth is cheap
# -> Use the git tag to figure out what release to download, and
#    can verify that it matches. This is here so we know that
#    we actually did the release
python3 installer.py download-robotpy --basever $VERSION

# TODO .. need to create a manifest of what to include in the zip?

# Finally, create a zipfile (not a tarball, windows users)
# TODO..
cd ..


# Add installer.py, win32 directory + exe/license,
# add pip-cache (only most recent + relevant pieces)
# add opkg-cache (only python3)
# license, dist-readme, installer readme..
echo "TODO"
exit 1

echo "Success!"
