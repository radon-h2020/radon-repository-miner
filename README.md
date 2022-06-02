![Build](https://github.com/radon-h2020/radon-repository-miner/workflows/Build/badge.svg)
![Documentation](https://github.com/radon-h2020/radon-repository-miner/workflows/Documentation/badge.svg)
![Codecov](https://img.shields.io/codecov/c/github/radon-h2020/radon-repository-miner)
![lgtm](https://img.shields.io/lgtm/grade/python/github/radon-h2020/radon-repository-miner)
![pypi-version](https://img.shields.io/pypi/v/repository-miner)
![python-version](https://img.shields.io/pypi/pyversions/repository-miner)

# radon-repository-miner

RepositoryMiner is a Python framework that helps developers and researchers to mining software repositories.
It currently supports the Infrastructure as Code technology Ansible and Tosca.


# How to install

From [PyPI](https://pypi.org/project/repository-miner/):

```pip install repository-miner```

From source code:

```text
git clone https://github.com/radon-h2020/radon-repository-miner.git
cd radon-repository-miner
pip install -r requirements.txt
pip install .
```

**Important:** to properly use the FixingCommitCategorized, install the spaCy statistical model `en_core_web_sm`: 

`python -m spacy download en_core_web_sm`


# Usage

```python
from repominer.mining.<ansible|tosca> import <Ansible|Tosca>Miner
from repominer.metrics.<ansible|tosca> import <Ansible|Tosca>MetricsExtractor
    
miner = <Ansible|Tosca>Miner(url_to_repo='github.com/adriagalin/ansible.motd', clone_repo_to='/tmp') 
miner.get_fixing_commits()
miner.get_fixed_files()
failure_prone_files = miner.label()

metrics_extractor = <Ansible|Tosca>MetricsExtractor(path_to_repo='/tmp/ansible.motd')
metrics_extractor.extract(failure_prone_files, product=True, process=True, delta=True)
metrics_extractor.to_csv('metrics.csv')

print('FIXING COMMITS:', miner.fixing_commits)
print('FAILURE-PRONE FILES:', failure_prone_files)
print('METRICS:', metrics_extractor.dataset.head())
```

# How to test

```text
pip install pytest
unzip test_data.zip -d .
pytest
```
