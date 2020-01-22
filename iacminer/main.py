import json
import os
import pandas as pd
import sys
import yaml

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from io import StringIO

from iacminer.metrics.metrics import Metrics
from iacminer.miners.commits import CommitsMiner
from iacminer.miners.scripts import ScriptsMiner
from iacminer.utils import load_repositories

def main():
    repos = load_repositories()

    miner = CommitsMiner()
    for repo in repos:
        fc = miner.mine_commits(repo)
        print(f'Found {len(fc)} fixing commits')
    
    
    fixing_commits = miner.fixing_commits
    print(f'Found {len(fixing_commits)} in total')

    miner = ScriptsMiner()
    for commit in fixing_commits:
        defective, unclassified = miner.mine_scripts(commit)
        print(f'Found {len(defective)} defective files and {len(unclassified)} unclassified files')

    defective_scripts = miner.defective_scripts
    unclassified_scripts = miner.unclassified_scripts
    
    dataset = Metrics().calculate(defective_scripts, unclassified_scripts)

if __name__=='__main__':
    main()