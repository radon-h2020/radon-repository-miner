.. radon-repository-miner documentation master file, created by
   sphinx-quickstart on Fri Dec 18 12:19:56 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to repominer's documentation!
=====================================

RepoMiner is a Python package and CLI for mining Infrastructure-as-Code software repositories.
It can be extended to support other languages (e.g., Python), though.

Installation
************

``pip install repository-miner``

Quick Usage
***********

Python
------

.. code-block:: python

    from repominer.metrics.ansible import AnsibleMetricsExtractor
    from repominer.mining.ansible import AnsibleMiner

    miner = AnsibleMiner('https://github.com/owner/repository')
    miner.get_fixing_commits_from_closed_issues()
    miner.get_fixing_commits_from_commits_message()
    miner.get_fixing_files()
    failure_prone_files = miner.label()

    metrics_extractor = AnsibleMetricsExtractor()
    metrics_extractor.extract(failure_prone_files)
    print(metrics_extractor.dataset.head())


Command-Line
------------

.. code-block:: RST

    usage: repo-miner [-h] [-v] {mine,extract-metrics} ...

    A Python library and command-line tool to mine Infrastructure-as-Code based software repositories.

    positional arguments:
      {mine,extract-metrics}
        mine                Mine fixing- and clean- files
        extract-metrics     Extract metrics from the mined files

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit



.. toctree::
   :maxdepth: 3
   :caption: Contents:

   cli
   apis
   help

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
