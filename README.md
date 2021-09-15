![Build](https://github.com/radon-h2020/radon-repository-miner/workflows/Build/badge.svg)
![Documentation](https://github.com/radon-h2020/radon-repository-miner/workflows/Documentation/badge.svg)
![Codecov](https://img.shields.io/codecov/c/github/radon-h2020/radon-repository-miner)
![lgtm](https://img.shields.io/lgtm/grade/python/github/radon-h2020/radon-repository-miner)
![pypi-version](https://img.shields.io/pypi/v/repository-miner)
![python-version](https://img.shields.io/pypi/pyversions/repository-miner)

# radon-repository-miner
A Python package for mining Infrastructure-as-Code software repositories.

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

# How to test

```text
pip install pytest
unzip test_data.zip -d .
pytest
```


# How to build Docker container

`docker build --tag repo-miner:latest .`

# How to run Docker container

First create or define a directory to mount inside the Docker container to access the results once generated.
For the sake of the example let's use `/tmp/repo-miner`.
 
## Mine

Using the `github` argument:

`docker run -v /tmp/repo-miner:/app  -e GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN repo-miner:latest repo-miner mine failure-prone-files github ansible adriagalin/ansible.motd . --verbose`

Using the `gitlab` argument:

`docker run -v /tmp/repo-miner:/app  -e GITLAB_ACCESS_TOKEN=$GITLAB_ACCESS_TOKEN repo-miner:latest repo-miner mine failure-prone-files gitlab ansible adriagalin/ansible.motd . --verbose`


## Extract metrics

`docker run -v /tmp/repo-miner:/app  repo-miner:latest repo-miner extract-metrics https://github.com/<owner>/<repository>.git ./failure-prone-files.json ansible all release . --verbose`



# CHANGELOG
See the [CHANGELOG](CHANGELOG.md) for information about the release history.
