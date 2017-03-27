#!/usr/bin/env bash
python3 -m venv --clear venv
venv/bin/pip install -U pip
venv/bin/pip install -U setuptools
venv/bin/pip install -r requirements.txt
#
