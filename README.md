# iac-miner
A mining tool written in Python to mine software repositories for Infrastructure-as-Code

Available on [PyPI](https://pypi.org/project/iacminer/): ```pip install iaciminer```.


## APIs usage

### Mine Github

```python
import os
from datetime import datetime
from iacminer.miners.github import GithubMiner

    
    
miner = GithubMiner(access_token = os.get_env('GITHUB_ACCESS_TOKEN'),
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

### Mine repository

```python
from iacminer.miners.repository import RepositoryMiner

miner = RepositoryMiner(access_token = os.get_env('GITHUB_ACCESS_TOKEN'),
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

# Execute the previous methods at once and extract metrics from labeled files on a per-release basis
for metrics in miner.mine():
    print(metrics)

```



### Combine GithubMiner and RepositoryMiner

```python
import os
from iacminer.miners.github import GithubMiner
from iacminer.miners.repository import RepositoryMiner

gh_miner = GithubMiner(access_token = os.get_env('GITHUB_ACCESS_TOKEN'),
                       min_stars=<int>,   # Optional (default 0)
                       min_issues=<int>,   # Optional (default 0)
                    )

for repository in gh_miner.mine():
    print(repository)
    repo_miner = RepositoryMiner(access_token = os.get_env('GITHUB_ACCESS_TOKEN'),
                                 path_to_repo='path/to/cloned/repository',
                                 branch='development') # Optional (default 'master')
                                 
    # Mine repository as previous example ...
```



## Command-line usage
