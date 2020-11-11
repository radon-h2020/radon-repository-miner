#!/usr/bin/env python

from setuptools import setup, find_packages

with open("requirements.txt", "r") as reqs_file:
    requirements = reqs_file.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.8.8'

setup(name='repository-miner',
      version=VERSION,
      description='A tool to mine IaC-based repositories.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Stefano Dalla Palma',
      maintainer='Stefano Dalla Palma',
      author_email='stefano.dallapalma0@gmail.com',
      url='https://github.com/radon-h2020/radon-repository-miner',
      download_url=f'https://github.com/radon-h2020/radon-repository-miner/archive/{VERSION}.tar.gz',
      packages=find_packages(exclude=('tests',)),
      entry_points={
          'console_scripts': ['repo-miner=repominer.cli:main'],
      },
      python_requires='>=3.6',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "License :: OSI Approved :: Apache Software License",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Operating System :: POSIX :: Linux"
      ],
      insall_requires=requirements
)
