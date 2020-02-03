import json
import os
import pandas as pd
import sys
import yaml

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from io import StringIO

from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.commits import CommitsMiner
from iacminer.miners.scripts import ScriptsMiner
from iacminer.utils import load_repositories


import git
import shutil
from pathlib import Path
from pydriller.repository_mining import GitRepository

def clone_repo(repo: str):
     # Clone repo
    author = repo.split('/')[0]
    repo_name = repo.split('/')[1]
    root_path = str(Path(f'repositories/{author}'))
    repo_path = os.path.join(root_path, repo_name)
    
    delete_repo(root_path)
    os.makedirs(root_path)

    git.Git(root_path).clone(f'https://github.com/{repo}.git', branch='master')
    git_repo = GitRepository(repo_path)
    
    return git_repo
    

def main():

    repos = load_repositories()
    
    for repo in repos:

        print(f'====================== Mining repository: {repo}')
        
        # Clone repo
        git_repo = clone_repo(repo)
        commits_miner = CommitsMiner(git_repo)
        scripts_miner = ScriptsMiner(git_repo)
        
        metrics_miners = {}

        for commit in commits_miner.mine():
            print(f'========== Checkout to commit: {commit.hash}')            
            
            print(f'Extracting process metrics.')
            if commit.hash not in metrics_miners:
                mm = MetricsMiner()
                mm.mine_process_metrics(str(git_repo.path), commit.hash, commit.release[0], commit.release[1])
                metrics_miners[commit.hash] = mm

            mm = metrics_miners[commit.hash]

            for content in scripts_miner.mine(commit):
                metadata = {
                    'repo': repo,
                    'commit': commit.hash,
                    'filepath': content.filepath,
                    'defective': 'yes' if content.defective else 'no',
                    'release_starts_at': commit.release_starts_at,
                    'release_ends_at': commit.release_ends_at,
                    'commit_date': str(commit.date)
                } 
                
                mm.mine_product_metrics(content.content)
                mm.save(content.filepath, metadata)

        git_repo.clear()

        author = repo.split('/')[0]
        root_path = str(Path(f'repositories/{author}'))
        delete_repo(root_path)

def delete_repo(path_to_repo: str):
    # delete local repo
    if os.path.isdir(path_to_repo):
        shutil.rmtree(path_to_repo)

if __name__=='__main__':
    main()