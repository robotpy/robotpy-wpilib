#!/usr/bin/env python3

import os
import subprocess
import sys
from os.path import abspath, dirname

if __name__ == "__main__":

    root = abspath(dirname(__file__))
    os.chdir(root)

    subprocess.check_call([sys.executable, "-m", "pytest"])
