#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='openbrokerapi',
    version='4.0.2',
    python_requires='>=3.5',
    packages=find_packages(exclude=['tests']),
    install_requires=['flask'],
    test_suite="tests",

    # Metadata
    author="Maic Siemering",
    author_email="maic@siemering.tech",
    license="MIT",
    description="A python package for the V2 CF Service Broker API and Open Broker API (version 2.13+)",
    long_description=open('README.rst').read(),
    url="https://github.com/eruvanos/openbrokerapi",
    keywords=["cloudfoundry", "cfbrokerapi", "openbrokerapi", "openservicebrokerapi", "servicebroker", "flask"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Frameworks
        'Framework :: Flask',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    # Optional installations
    extras_require={
        'docs': [
            'sphinx >= 1.4',
            'sphinx_rtd_theme'
        ],
        'gevent': ['gevent'],
        'gunicorn': ['gunicorn']
    }

)
