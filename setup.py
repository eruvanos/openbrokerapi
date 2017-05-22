#!/usr/bin/env python3
from setuptools import setup, find_packages


def get_long_description():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except (IOError, ImportError, RuntimeError):
        print('WARNING: Please install pypandoc and pandoc. Otherwise long description will not be available.')


setup(
    name='cfbrokerapi',
    version='0.1.dev3',
    packages=find_packages(),
    install_requires=['flask'],
    test_suite="test",

    # Metadata
    author="Maic Siemering",
    author_email="eruvanos@ewetel.net",
    license="MIT",
    description="A python package for the V2 CF Service Broker API",
    long_description=get_long_description(),
    url="https://github.com/eruvanos/cfbrokerapi",
    keywords="cloudfoundry servicebroker openservicebroker api",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

)
