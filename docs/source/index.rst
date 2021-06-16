.. radon-repository-miner documentation master file, created by
   sphinx-quickstart on Fri Dec 18 12:19:56 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RepoMiner Docs!
=====================================

RepoMiner is a Python package mining Infrastructure-as-Code software repositories.
It can be extended to support other languages (e.g., Python), though.

Installation
************

``pip install repository-miner``

Quick Usage
***********


.. code-block:: python

    from repominer.metrics.ansible import AnsibleMetricsExtractor
    from repominer.mining.ansible import AnsibleMiner

    miner = AnsibleMiner('https://github.com/owner/repository')
    miner.get_fixing_commits()
    miner.get_fixed_files()
    failure_prone_files = [file for file in miner.label()]

    metrics_extractor = AnsibleMetricsExtractor()
    metrics_extractor.extract(failure_prone_files)
    print(metrics_extractor.dataset.head())


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   apis
   help

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
