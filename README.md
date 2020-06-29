# iac-miner
A mining tool written in Python to mine software repositories for Infrastructure-as-Code

Available on [PyPI](https://pypi.org/project/iacminer/): ```pip install iacminer```.


## APIs usage

<br>

First, export your Github's access token in an environment variable called ```GITHUB_ACCESS_TOKEN```, with:

```export GITHUB_ACCESS_TOKEN='yourtokenhere'``` (on Linux)

This variable will contain the token to access the GitHub APIs and avoid to be hard-coded in the code.


### Mine Github

```python
import os
from datetime import datetime
from iacminer.miners.github import GithubMiner

    
    
miner = GithubMiner(access_token = os.getenv('GITHUB_ACCESS_TOKEN'),
                    date_from = datetime.strptime('2020-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
                    date_to = datetime.strptime('2020-01-02 00:00:00', '%Y-%m-%d %H:%M:%S'),
                    push_after=datetime.strptime('2020-06-07 00:00:00', '%Y-%m-%d %H:%M:%S'),
                    min_stars = <int>, # (default = 0)
                    min_releases = <int>, # (default = 0)
                    min_watchers = <int>, # (default = 0)
                    min_issues = <int>, # (default = 0)
                    primary_language = <str|None>, # e.g., 'python' (default = None)
                    include_fork = <True|False>) # (default = False)

for repository in miner.mine():
    print(repository)

```

<br>

### Mine repository

```python
from iacminer.miners.repository import RepositoryMiner

miner = RepositoryMiner(token = os.getenv('GITHUB_ACCESS_TOKEN'),
                        path_to_repo='path/to/cloned/repository',
                        branch='development') # Optional (default 'master')

# Get only fixing commits by analyzing issues
fix_from_issues = miner.get_fixing_commits_from_closed_issues()
for sha in fix_from_issues:
    print(sha)

# Get only fixing commits by analyzing commit messages
fix_from_commits = miner.get_fixing_commits_from_commit_messages()
for sha in fix_from_commits:
    print(sha)

# Get all Ansible files touched by fixing commits
miner.set_fixing_commits() # Must call this method first
fixing_files = miner.get_fixing_files()

# Get files labeled as 'defect-prone' or 'defect-free'
labeled_files = miner.label(fixing_files)

```

Alternatively, execute the previous methods at once and extract metrics from labeled files on a per-release basis with:

```python
from iacminer.miners.repository import RepositoryMiner

miner = RepositoryMiner(token = os.getenv('GITHUB_ACCESS_TOKEN'),
                        path_to_repo='path/to/cloned/repository',
                        branch='development', # Optional (default='master')
                        owner='radon-h2020',  # Optional (default=None)
                        repo='radon-iac-miner')  # Optional (default=None)

for metrics in miner.mine():
    print(metrics)

```

<br>

### Combine GithubMiner and RepositoryMiner

```python
import os
from iacminer.miners.github import GithubMiner
from iacminer.miners.repository import RepositoryMiner

gh_miner = GithubMiner(access_token = os.getenv('GITHUB_ACCESS_TOKEN'),
                       min_stars=<int>,   # Optional (default 0)
                       min_issues=<int>,   # Optional (default 0)
                    )

for repository in gh_miner.mine():
    print(repository)
    repo_miner = RepositoryMiner(token = os.getenv('GITHUB_ACCESS_TOKEN'),
                                 path_to_repo='path/to/cloned/repository',
                                 branch='development', # Optional (default='master')
                                 owner='radon-h2020',  # Optional (default=None)
                                 repo='radon-iac-miner')  # Optional (default=None)
                                 
    # Mine repository as previous example ...
```



<br>

## Command-line usage

```
usage: iac-miner [-h] [-v] {mine-github,mine-repository} ...

A Python library to crawl GitHub for Infrastructure-as-Code based repositories
and minethose repositories to identify fixing commits and label defect-prone
files.

positional arguments:
  {mine-github,mine-repository}
    mine-github         Mine repositories from Github
    mine-repository     Mine a single repository

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
 ```

<br>

#### iac-miner mine-github

```
usage: iac-miner mine-github [-h] [--from DATE_FROM] [--to DATE_TO]
                             [--pushed-after DATE_PUSH]
                             [--iac-languages [{ansible,chef,puppet,all} [{ansible,chef,puppet,all} ...]]]
                             [--include-fork] [--min-issues MIN_ISSUES]
                             [--min-releases MIN_RELEASES]
                             [--min-stars MIN_STARS]
                             [--min-watchers MIN_WATCHERS]
                             [--primary-language PRIMARY_LANGUAGE] [--verbose]
                             dest tmp_clones_folder

positional arguments:
  dest                  destination folder to save results
  tmp_clones_folder     path to temporary clone the repositories for the
                        analysis

optional arguments:
  -h, --help            show this help message and exit
  --from DATE_FROM      start searching from this date (default: 2014-01-01
                        00:00:00)
  --to DATE_TO          search up to this date (default: 2020-01-01 00:00:00)
  --pushed-after DATE_PUSH
                        search up to this date (default: 2019-01-01 00:00:00)
  --iac-languages [{ansible,chef,puppet,all} [{ansible,chef,puppet,all} ...]]
                        only repositories with this language(s) will be
                        analyzed (default: all)
  --include-fork        whether to include forked repositories (default:
                        False)
  --min-issues MIN_ISSUES
                        minimum number of issues (default: 0)
  --min-releases MIN_RELEASES
                        minimum number of releases (default: 0)
  --min-stars MIN_STARS
                        minimum number of stars (default: 0)
  --min-watchers MIN_WATCHERS
                        minimum number of watchers (default: 0)
  --primary-language PRIMARY_LANGUAGE
                        the primary language of the repository (default: None)
  --verbose             whether to output results (default: False)
```

<br>

#### iac-miner mine-repository

```
usage: iac-miner mine-repository [-h] [--branch REPO_OWNER]
                                 [--owner REPO_OWNER] [--name REPO_NAME]
                                 [--verbose]
                                 path_to_repo dest

positional arguments:
  path_to_repo         Name of the repository (owner/name).
  dest                 Destination folder to save results.

optional arguments:
  -h, --help           show this help message and exit
  --branch REPO_OWNER  the repository's default branch (default: master)
  --owner REPO_OWNER   the repository's owner (default: None)
  --name REPO_NAME     the repository's name (default: None)
  --verbose            whether to output results (default: False)
```

## Current release
## [0.1.3]
- The mine-repository option is now supported
