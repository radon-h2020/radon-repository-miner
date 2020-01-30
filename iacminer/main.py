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

def main():
    """
    repos = load_repositories()

    commits_miner = CommitsMiner()
    for repo in repos:
        fc = commits_miner.mine(repo)
        print(f'Found {len(fc)} fixing commits in {repo}')
    
    fixing_commits = commits_miner.fixing_commits
    """
   
    from iacminer.entities.commit import Commit
    from iacminer.entities.file import File

    fixing_commits = set()
    filepath = os.path.join('data','fixing_commits.json')
    if os.path.isfile(filepath):
        with open(filepath, 'r') as infile:
            json_array = json.load(infile)

            for json_obj in json_array:
                files = set()
                for file in json_obj['files']:
                    files.add(File(file))
                
                commit = Commit(json_obj)
                commit.files = files
                fixing_commits.add(commit)

    print(f'Found {len(fixing_commits)} fixing commits in total.')

    scripts_miner = ScriptsMiner()
    for commit in fixing_commits:

        print(f'Extracting process metrics from {commit.sha}')
        metrics_miner = MetricsMiner()
        metrics_miner.mine_process_metrics(None, commit)
        
        for content, defect_prone in scripts_miner.mine(commit):
            # TODO: Start thread for metric passing Compute process metrics in parent commit
            print(f'Extracting product metrics from {commit.sha}/{content.filename}')
            metrics_miner.mine_product_metrics(content)
            print(f'Saving metris')
            metrics_miner.save(content, defect_prone)

        print(f'Found {len(scripts_miner.defective_scripts)} defective files and {len(scripts_miner.unclassified_scripts)} unclassified files so far.')

if __name__=='__main__':
    main()