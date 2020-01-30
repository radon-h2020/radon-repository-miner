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

    repos = load_repositories()
    
    for repo in repos:

        print(f'====================== Mining repository: {repo}')
        commits_miner = CommitsMiner(repo)
        
        for commit in commits_miner.mine():
            
            print(f'========== Mining commit: {commit.sha}')

            print(f'Extracting process metrics for parent commit.')
            metrics_miner = MetricsMiner()
            metrics_miner.mine_process_metrics(f'https://github.com/{commit.repo}', commit.release_start_at, commit.parents[0])
            
            scripts_miner = ScriptsMiner(commit)

            for content, defect_prone in scripts_miner.mine():
                print(f'Extracting product metrics from file: {content.filename}')
                metrics_miner.mine_product_metrics(content)
                metrics_miner.save(content, defect_prone)

            print(f'Found {len(scripts_miner.defective_scripts)} defective files and {len(scripts_miner.unclassified_scripts)} unclassified files so far.')

if __name__=='__main__':
    main()