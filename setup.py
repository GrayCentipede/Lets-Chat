#!/usr/bin/env python3

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Let's Chat",
    version = "0.0.0",
    author = "Mauricio Carrasco Ruiz",
    author_email = "maucarrui@ciencias.unam.mx",
    description = ("A very simple chat made with python"),
    install_requires = ['npyscreen'],
    test_suite = "src.test",
)
