#!/usr/bin/env python

import os
import sys

here = lambda *a: os.path.join(os.path.dirname(__file__), *a)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('git push origin master:master')
    sys.exit()

readme = open(here('README.md')).read()

setup(
    name='airplanemode',
    version='0.2.0',
    description='Quickly enable/disable networking and background apps',
    long_description=readme,
    author='Robert Gardner',
    author_email='robert.gardner@nyu.edu',
    url='https://github.com/rgardner/airplanemode',
    packages=[
        'airplanemode',
    ],
    package_dir={'airplanemode': 'airplanemode'},
    include_package_data=True,
    keywords='nikola',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'airplanemode = airplanemode.cli:main',
        ]
    }
)
