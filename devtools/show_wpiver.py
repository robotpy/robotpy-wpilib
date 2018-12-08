#!/usr/bin/env python
#
# Scrapes the wpilib download directories to determine what the latest
# release is, instead of searching for it manually
#
# This is done in a separate script to avoid import errors
#
# As this is just a utility -- these are NOT added to the requirements.txt
# - pip install beautifulsoup4
# - pip install htmllistparse

from os.path import dirname, join
import sys

import htmllistparse


def print_site(uri, show_all):
    _, l = htmllistparse.fetch_listing(uri)
    l = sorted(l, key=lambda i: i.modified, reverse=True)
    for i in l:

        # TODO: figure out what the latest 'stable' release is and print
        # that instead.. probably can use a regex?

        if not i.name.endswith("/"):
            continue

        print(i.name.strip("/"))
        if not show_all:
            break


if __name__ == "__main__":

    show_all = False
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        show_all = True

    filename = join(dirname(__file__), "..", "hal-roborio", "hal_impl", "distutils.py")
    d = {}

    with open(filename) as f:
        code = compile(f.read(), filename, "exec")
        exec(code, d, d)

    print("Current HAL:", d["hal_version"])
    print_site(d["hal_site"], show_all)

    print()
    print("Current WPIUtil", d["wpiutil_version"])
    print_site(d["wpiutil_site"], show_all)
