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

def main():

    repos = load_repositories()
    
    for repo in repos:
        print(f'====================== Mining repository: {repo}')
        
        # Clone repo
        author = repo.split('/')[0]
        repo_name = repo.split('/')[1]
        root_path = str(Path(f'repositories/{author}'))
        repo_path = os.path.join(root_path, repo_name)
        
        delete_repo(root_path)
        os.makedirs(root_path)

        git.Git(root_path).clone(f'https://github.com/{repo}.git', branch='master')
        git_repo = GitRepository(repo_path)
        
        commits_miner = CommitsMiner(git_repo)
        
        metrics_miners = {}

        for commit in commits_miner.mine():
            #print(f'========== Checkout to commit: {commit.hash}')
            
            git_repo.checkout(commit.hash)

            #print(f'Extracting process metrics.')
            if commit.hash not in metrics_miners:
                mm = MetricsMiner()
                mm.mine_process_metrics(repo_path, commit.release[0], commit.release[1])
                metrics_miners[commit.hash] = mm

            mm = metrics_miners[commit.hash]

            # mine(buggy_commit)# => all files in buggy commits are defective. The others are not: use filters.is_ansible_file to get content that are ansible files
            for filepath in commit.filenames:
                # Script miner => find filepath at commit.hash
                # Get file and label it defective.
            # Get all other files from repo at that commit and label them 'defect-prone'

                with open(os.path.join(repo_path, filepath), 'r') as f:
                    content = f.read()
                    #mm.mine_product_metrics(content)
                    mm.save(filepath, defect_prone=True)
            """
            scripts_miner = ScriptsMiner(commit)

            for content, defect_prone in scripts_miner.mine():
                print(f'Extracting product metrics from file: {content.filename}')
                mm.mine_product_metrics(content)
                mm.save(content, defect_prone)

            print(f'Found {len(scripts_miner.defective_scripts)} defective files and {len(scripts_miner.unclassified_scripts)} unclassified files so far.')
            """

        git_repo.clear()
        delete_repo(root_path)

def delete_repo(path_to_repo: str):
    # delete local repo
    if os.path.isdir(path_to_repo):
        shutil.rmtree(path_to_repo)

if __name__=='__main__':
    main()