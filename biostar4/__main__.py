#!/usr/bin/env python
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

sys.path.append(PARENT_DIR)

if __name__ == "__main__":
    print("Usage python -m biostar.manage")