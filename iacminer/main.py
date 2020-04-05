import os
import sys
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

import copy
import git
import json
import pandas as pd
import shutil
import yaml

from datetime import datetime, timedelta

from iacminer import filters, utils
from iacminer.miners.github import GithubMiner


def main(date_from, date_to, push_after):
    
    github_miner = GithubMiner(
        date_from=date_from,
        date_to=date_to,
        pushed_after=push_after,
        min_stars=1,
        min_releases=2
    )
    
    github_miner.set_token(os.getenv('GITHUB_ACCESS_TOKEN'))
    
    i = 0 
    
    ansible_repositories = utils.load_ansible_repositories()
    for repo in github_miner.mine():
        
        i += 1

        if repo['issues'] > 0:  # ONLY TEMPORARY
            continue

        if any(existing['id'] == repo['id'] for existing in ansible_repositories):
            continue # already mined

        if not ('ansible' in repo['description'].lower() or 'ansible' in repo['owner'].lower() or 'ansible' in repo['name'].lower()):
            if sum([1 for path in repo['dirs'] if filters.is_ansible_dir(path)]) < 2:
                # If the repo does not contain at least two among 'playbooks', 'roles', 'handlers', 'tasks', 'meta'
                # the discard it. Otherwise it means it has Ansible code, but not 'ansible' in the name or description
                continue

        utils.save_ansible_repository(copy.deepcopy(repo))

    print(f'{i} repositories mined')
    print(f'Quota: {github_miner.quota}')
    print(f'Quota will reset at: {github_miner.quota_reset_at}')

if __name__=='__main__':
    date_from = datetime.strptime('2018-03-31 00:00:00', '%Y-%m-%d %H:%M:%S')
    date_to = datetime.strptime('2018-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    push_after=datetime.strptime('2019-09-08 00:00:00', '%Y-%m-%d %H:%M:%S')
    now = datetime.strptime('2020-03-09 00:00:00', '%Y-%m-%d %H:%M:%S')

    while date_to <= now:
        print(f'Searching for: {date_from}..{date_to}. Analysis started at {str(datetime.now())}')
        main(date_from, date_to, push_after)
        date_from = date_to
        date_to += timedelta(hours=24)