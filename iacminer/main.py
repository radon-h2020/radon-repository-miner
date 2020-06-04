import copy
import json
import os
import re
import shutil

import git
import pandas as pd

from datetime import datetime
from dotenv import load_dotenv
from repositoryscorer import scorer

from iacminer import filters
from iacminer.miners.github import GithubMiner
from iacminer.miners.repository import RepositoryMiner

ROOT = os.path.realpath(__file__).rsplit(os.sep, 2)[0]
PATH_TO_REPO = ROOT + '/test_data/adriagalin/ansible.motd'

load_dotenv()


def clone_repository(path_to_folder: str, url_to_repo: str) -> str:
    """
    Clone a repository in the specified folder
    :param path_to_folder: the folder where to clone the repository
    :param url_to_repo: the url to the repository,
    :return: the path to the local repository
    """
    match = re.match(r'(https:\/\/)?github\.com\/(\w+)\/(\w+)(\.git)?', url_to_repo)
    if not match:
        raise ValueError('Not a valid Github url')

    owner, name = match.groups()[1], match.groups()[2]

    path_to_owner = os.path.join(path_to_folder, owner)
    if not os.path.isdir(path_to_owner):
        os.makedirs(path_to_owner)

    git.Git(path_to_owner).clone(url_to_repo)
    return os.path.join(path_to_owner, name)


def delete_repo(path_to_repo: str) -> None:
    """
    Delete a local repository.
    :param path_to_repo: path to the repository to delete  
    :return: None
    """
    try:
        path_to_owner = '/'.join(path_to_repo.split('/')[:-1])
        if len(os.listdir(path_to_owner)) == 1:
            shutil.rmtree(path_to_owner)
        else:
            shutil.rmtree(path_to_repo)

    except Exception as e:
        print(f'>>> Error while deleting directory: {str(e)}')


if __name__ == '__main__':

    result_folder = ''#?

    github_miner = GithubMiner(
        access_token=os.getenv('GITHUB_ACCESS_TOKEN'),
        date_from=datetime.strptime('2018-01-01', '%Y-%m-%d'),
        date_to=datetime.strptime('2018-01-03', '%Y-%m-%d'),
        pushed_after=datetime.strptime('2019-01-01', '%Y-%m-%d'),
        min_stars=1,
        min_releases=2
    )

    for repository in github_miner.mine():
        if not ('ansible' in repository['description'].lower() or 'ansible' in repository['owner'].lower() or
                'ansible' in repository['name'].lower()):

            if sum([1 for path in repository['dirs'] if filters.is_ansible_dir(path)]) < 2:
                # If the repo does not contain at least two among 'playbooks', 'roles', 'handlers', 'tasks', 'meta'
                # then discard it. Otherwise it means it has Ansible code
                continue

        # It is an Ansible repository

        # 1) Clone
        print(f'Cloning {repository["url"]}')
        path_to_repository = clone_repository(os.path.join(ROOT, 'test_data'), repository['url'])
        print(path_to_repository)

        # 2) Get repository scores
        report = scorer.score_repository(path_to_repo=path_to_repository,
                                         threshold_community=2,
                                         threshold_comments_ratio=0.002,
                                         threshold_commit_frequency=2,
                                         threshold_issue_events=0.023,
                                         threshold_sloc=190)

        if report['score'] < 90 or (report['score'] >= 65 and report['issue_frequency'] != 0):
            print(f'Deleting {path_to_repository}')
            delete_repo(path_to_repository)
            continue

        # 3) Start analysis
        repo_miner = RepositoryMiner(os.getenv('GITHUB_ACCESS_TOKEN'), PATH_TO_REPO)

        dataset = pd.DataFrame()

        for metrics in repo_miner.mine():
            print(metrics)
            dataset = dataset.append(metrics, ignore_index=True)

            # Update csv containing metrics for the repository
            with open(result_folder + '/repository_name.csv', 'w') as out:
                dataset.to_csv(out, mode='w', index=False)

        # Save repository metadata
        with open('repository_name.metadata.json', 'w') as out:
            repository = copy.deepcopy(repository)
            repository.update(report)
            json.dump(out, repository)

        print(f'Deleting {path_to_repository}')
        delete_repo(path_to_repository)

        # Use dataset to train model