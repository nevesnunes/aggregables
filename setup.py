#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

cwd = os.path.dirname(os.path.realpath(__file__))
requirements_path = cwd + "/requirements.txt"
install_requires = []
if os.path.isfile(requirements_path):
    with open(requirements_path) as f:
        install_requires = f.read().splitlines()

setup(
    name="aggregables",
    version="1.0",
    install_requires=install_requires,
    packages=find_packages(),
)
