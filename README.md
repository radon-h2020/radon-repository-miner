![Build](https://github.com/radon-h2020/radon-repository-miner/workflows/Build/badge.svg)
![Documentation](https://github.com/radon-h2020/radon-repository-miner/workflows/Documentation/badge.svg)
![lgtm](https://img.shields.io/lgtm/grade/python/github/radon-h2020/radon-repository-miner)
![Total alerts](https://img.shields.io/lgtm/alerts/github/radon-h2020/radon-repository-miner)
![pypi-version](https://img.shields.io/pypi/v/repository-miner)
![pypi-status](https://img.shields.io/pypi/status/repository-miner)
![release-date](https://img.shields.io/github/release-date/radon-h2020/radon-repository-miner)


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
For the sake of the example let's use `/tmp/`.
 
## Mine

Using the `github` argument:

`docker run -v /tmp:/app  -e GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN repo-miner:test repo-miner mine github ansible adriagalin/ansible.motd . --verbose`

Using the `github` argument:

`docker run -v /tmp:/app  -e GITLAB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN repo-miner:test repo-miner mine github ansible adriagalin/ansible.motd . --verbose`


## Extract metrics

`docker run -v /tmp:/app  repo-miner:test repo-miner extract-metrics https://github.com/<owner>/<repository>.git /tmp/failure-prone-files.json ansible all release . --verbose`


## CHANGELOG
See the [CHANGELOG](CHANGELOG.md) for information about the release history.
