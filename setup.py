#!/usr/bin/env python

import json
from setuptools import setup, find_packages

with open("config.json", "r") as fh:
    config = json.load(fh)

with open("requirements.txt", "r") as reqs_file:
    requirements = reqs_file.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = config.get("version", "0.0")

setup(name='iacminer',
      version=VERSION,
      description='A module to crawl infrastructure code repositories and scripts from GitHub',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Stefano Dalla Palma',
      maintainer='Stefano Dalla Palma',
      author_email='stefano.dallapalma0@gmail.com',
      url='https://github.com/stefanodallapalma/iac-miner',
      download_url=f'https://github.com/stefanodallapalma/iac-miner/archive/{VERSION}.tar.gz',
      packages=find_packages(exclude=('tests',)),
      entry_points = {
        'console_scripts': ['iac-miner=iacminer.command_line:cli'],
      },
      classifiers=[
         "Development Status :: 3 - Alpha",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 3.7",
         "License :: OSI Approved :: Apache Software License",
         "Topic :: Software Development :: Libraries :: Python Modules",
         "Operating System :: OS Independent"
      ],
      insall_requires=requirements
)