from iacminer.miners.commits import CommitsMiner
from iacminer.miners.scripts import ScriptsMiner
from iacminer.utils import load_repositories

repos = load_repositories()
for repo in repos:
    print(repo)

"""
miner = CommitsMiner()
for repo in repositories:
    miner.mine_commits(repo)

fixing_commits = miner.fixing_commits

miner = ScriptsMiner()
for commit in fixing_commit:
    miner.mine_scripts(commit)

defective_scripts = miner.defective_script
unclassified_scripts = miner.unclassified_scripts



# TODO download files from commits
"""