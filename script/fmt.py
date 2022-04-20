#!/usr/bin/env python

import os
import pathlib
import subprocess
import sys

ROOT_DIR = pathlib.Path(__file__).parents[1]
os.chdir(ROOT_DIR)

subprocess.run([sys.executable, "-m", "black", "."], check=True)
subprocess.run([sys.executable, "-m", "isort", "."], check=True)
