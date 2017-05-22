#!/usr/bin/env python3
from setuptools import setup, find_packages


def get_long_description():
    try:
       import pypandoc
       return pypandoc.convert('README.md', 'rst')
    except (IOError, ImportError):
       return open('README.md').read()

setup(
    name='cfbrokerapi',
    version='0.1dev',
    packages=find_packages(),
    test_suite="test",

    # Metadata
    author="Maic Siemering",
    author_email="eruvanos@ewetel.net",
    license="MIT",
    description="A python package for the V2 CF Service Broker API",
    long_description=get_long_description(),
    url="https://github.com/eruvanos/cfbrokerapi"

)
