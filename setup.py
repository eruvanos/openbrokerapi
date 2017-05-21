#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='cfbrokerapi',
    version='0.1.dev',
    packages=find_packages(),
    test_suite="test",

    # Metadata
    author="Maic Siemering",
    author_email="eruvanos@ewetel.net",
    license="MIT",
    description="A python package for the V2 CF Service Broker API",
    long_description=open('README.md').read(),
    url="https://github.com/eruvanos/cfbrokerapi"

)
