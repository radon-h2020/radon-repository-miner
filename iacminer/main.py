import os
import sys
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from iacminer.miners.commits import CommitsMiner
from iacminer.miners.scripts import ScriptsMiner
from iacminer.utils import load_repositories

def main():
    repos = load_repositories()

    miner = CommitsMiner()
    for repo in repos:
        fc = miner.mine_commits(repo)
        print(fc)
    
    """
    fixing_commits = miner.fixing_commits

    miner = ScriptsMiner()
    for commit in fixing_commit:
        miner.mine_scripts(commit)

    defective_scripts = miner.defective_script
    unclassified_scripts = miner.unclassified_scripts



    # TODO download files from commits
    """


if __name__=='__main__':
    main()