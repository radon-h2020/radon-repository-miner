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
    """
    repos = load_repositories()

    miner = CommitsMiner()
    for repo in repos:
        fc = miner.mine_commits(repo)
        print(f'Found {len(fc)} fixing commits')
    
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
    
    #fixing_commits = miner.fixing_commits
    print(f'Found {len(fixing_commits)} in total')

    miner = ScriptsMiner()
    for commit in fixing_commits:
        defective, unclassified = miner.mine_scripts(commit)
        print(f'Found {len(defective)} defective files and {len(unclassified)} unclassified files')
    
    defective_scripts = miner.defective_scripts
    unclassified_scripts = miner.unclassified_scripts
    """

    from iacminer.entities.content import ContentFile

    defective_scripts = set()
    unclassified_scripts = set()

    filepath = os.path.join('data','defective_scripts.json')
    if os.path.isfile(filepath):
        with open(filepath, 'r') as infile:
            json_array = json.load(infile)

            for json_obj in json_array:
                defective_scripts.add(ContentFile(json_obj))

    filepath = os.path.join('data','unclassified_scripts.json')
    if os.path.isfile(filepath):
        with open(filepath, 'r') as infile:
            json_array = json.load(infile)

            for json_obj in json_array:
                unclassified_scripts.add(ContentFile(json_obj))


    
    dataset = Metrics().calculate(defective_scripts, unclassified_scripts)

if __name__=='__main__':
    main()