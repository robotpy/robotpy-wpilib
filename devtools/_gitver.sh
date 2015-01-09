
VERSION=`git describe --tags --dirty='-dirty'`

if [[ $VERSION =~ ^.*-dirty$ ]]; then
    echo "Cannot build an installer from a dirty git tree! Stash and try again"
    exit 1    
fi

if [[ ! $VERSION =~ ^[0-9]+\.[0-9]\.[0-9]+$ ]]; then
    if [ "$1" != "--pre" ]; then 
        echo "You are building from a prerelease git checkout ($VERSION)"
        echo 
        echo "If you really want to build a prelease, then use --pre"
        echo 
        echo "Otherwise, checkout the tag you wish to build or make a new tag,"
        echo "and try again"
        exit 1
    fi

    # Convert to PEP440
    IFS=- read VTAG VCOMMITS VLOCAL <<< "$VERSION"
    VERSION=`printf "%s.post0.dev%s" $VTAG $VCOMMITS`
fi
