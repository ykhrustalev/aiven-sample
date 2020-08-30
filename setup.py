#!/usr/bin/env python
from setuptools import setup

setup(
    name='webcheck',
    version='0.0.1',
    install_requires=[],  # pipenv managed
    packages=['webcheck'],
    entry_points={
        'console_scripts': [
            'webcheckctl = webcheck.main:main',
        ]
    },
    zip_safe=False,
)
