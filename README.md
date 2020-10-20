![lgtm](https://img.shields.io/lgtm/grade/python/github/radon-h2020/radon-repository-miner)
![LGTM Alerts](https://img.shields.io/lgtm/alerts/github/radon-h2020/radon-repository-miner)
![pypi-version](https://img.shields.io/pypi/v/repository-miner)
![pypi-status](https://img.shields.io/pypi/status/repository-miner)
![release-date](https://img.shields.io/github/release-date/radon-h2020/radon-repository-miner)


# radon-repository-miner
A Python package for mining Infrastructure-as-Code software repositories.

## How to install

The package can be downloaded from [PyPI](https://pypi.org/project/repository-miner/) as follows:

```pip install repository-miner```

Alternatively, it can be installed from the source code with:

```
pip install -r requirements.txt
pip install .
```

## Command-line usage

```
usage: radon-miner [-h] [-v] [--branch BRANCH] [--verbose]
                            path_to_repo owner name dest

A Python library to mine Infrastructure-as-Code based software repositories.

positional arguments:
  path_to_repo     the local path to the git repository
  {github,gitlab}  the source code versioning host
  full_name_or_id  the repository full name or id
  dest             destination folder for the reports

optional arguments:
  -h, --help       show this help message and exit
  -v, --version    show program's version number and exit
  --branch BRANCH  the repository branch to mine (default: master)
  --verbose        show log
```

**Important!** The package requires a personal access token to access the GraphQL APIs. See how to get one [here](https://github.com/settings/tokens).
Once generated, paste the token in the input field when asked. For example:

```
radon-miner path/to/the/cloned/repository github radon-h2020/radon-repository-miner .

Github access token: <paste your token here>
```  

You may want to avoid the previous step. If so, add ```GITHUB_ACCESS_TOKEN=<paste here your token>``` to the environment variables.

Same applies with the option `gitlab`. In that case, you might want to add  add ```GITLAB_ACCESS_TOKEN=<paste here your token>``` to the environment variables.

### Output
Running the tool from command-line generates an HTML report accessible at *\<dest\>/report.html*.


## CHANGELOG
See the [CHANGELOG](CHANGELOG.md) for information about the release history.
