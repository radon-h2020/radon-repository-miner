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

from pathlib import Path
from pydriller.repository_mining import GitRepository, RepositoryMining

from iacminer import filters, utils
from iacminer.entities.file import LabeledFile
from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.github_miner import GithubMiner
from iacminer.miners.repository_miner import RepositoryMiner
from iacminer.miners.labeling import LabelTechnique


DESTINATION_PATH = os.path.join('data', 'metrics.csv')

def all_files(path_to_root):
    """
    Get the set of all the files in a folder (excluding .git directory).
    
    Parameters
    ----------
    path_to_root : str : the path to the root of the directory to analyze.

    Return
    ----------
    files : set : the set of strings (filepaths).
    """

    files = set()

    for root, _, filenames in os.walk(path_to_root):
        if '.git' in root:
            continue
        for filename in filenames: 
            path = os.path.join(root, filename)
            path = path.replace(path_to_root, '')
            if path.startswith('/'):
                path = path[1:]

            files.add(path)

    return files

def clone_repo(owner: str, name: str):
    """
    Clone a repository on local machine.
    
    Parameters
    ----------
    owner : str : the name of the owner of the repository.

    name : str : the name of the repository.
    """

    path_to_owner = os.path.join('tmp', owner)
    if os.path.isdir(path_to_owner):
        delete_repo(owner)

    if not os.path.isdir(path_to_owner):
        os.makedirs(path_to_owner)
        git.Git(path_to_owner).clone(f'https://github.com/{owner}/{name}.git')

def delete_repo(owner: str):
    """
    Delete a local repository.
    
    Parameters
    ----------
    owner : str : the name of the owner of the repository.
    """

    path_to_owner = os.path.join('tmp', owner)
    try:
        shutil.rmtree(path_to_owner)
    except:
        print('Error while deleting directory')

def get_content(path):
    """
    Get the content of a file as plain text.
    
    Parameters
    ----------
    path : str : the path to the file.

    Return
    ----------
    str : the content of the file, if exists; None otherwise.
    """
    if not os.path.isfile(path):
        return None

    with open(path, 'r') as f:
        return f.read()

def save(metadata: dict, iac_metrics: dict, delta_metrics: dict, process_metrics: dict):
        
        filepath = str(Path(metadata['filepath']))
        
        metrics = metadata
        metrics.update(iac_metrics)
        metrics.update(delta_metrics)

        # Getting process metrics for the specific filepath
        metrics['change_set_max'] = process_metrics[0]
        metrics['change_set_avg'] = process_metrics[1]
        metrics['code_churn'] = process_metrics[2].get(filepath, 0)
        metrics['code_churn_max'] = process_metrics[3].get(filepath, 0)
        metrics['code_churn_avg'] = process_metrics[4].get(filepath, 0)
        metrics['commits_count'] = process_metrics[5].get(filepath, 0)
        metrics['contributors'] = process_metrics[6].get(filepath, 0)
        metrics['minor_contributors'] = process_metrics[7].get(filepath, 0)
        metrics['highest_experience'] = process_metrics[8].get(filepath, 0)
        metrics['median_hunks_count'] = process_metrics[9].get(filepath, 0)
        metrics['loc_added'] = process_metrics[10].get(filepath, 0)
        metrics['loc_added_max'] = process_metrics[11].get(filepath, 0)
        metrics['loc_added_avg'] = process_metrics[12].get(filepath, 0)
        metrics['loc_removed'] = process_metrics[13].get(filepath, 0)
        metrics['loc_removed_max'] = process_metrics[14].get(filepath, 0)
        metrics['loc_removed_avg'] = process_metrics[15].get(filepath, 0)
        
        # Create pandas dataframe
        dataset = pd.DataFrame()
        
        # Load dataframe, if exists
        if os.path.isfile(DESTINATION_PATH):
            with open(DESTINATION_PATH, 'r') as in_file:
                dataset = pd.read_csv(in_file)

        # Update dataframe
        dataset = dataset.append(metrics, ignore_index=True)

        # Save to csv
        with open(DESTINATION_PATH, 'w') as out:
            dataset.to_csv(out, mode='w', index=False)

def main(date_from, date_to, push_after):
    
    github_miner = GithubMiner(
        date_from=date_from,
        date_to=date_to,
        pushed_after=push_after,
        min_stars=1,
        min_releases=1
    )
    
    github_miner.set_token(os.getenv('GITHUB_ACCESS_TOKEN'))
    
    i = 0 
    
    for repo in github_miner.mine():
    
        i += 1

        if not ('ansible' in repo['description'].lower() or 'ansible' in repo['owner'].lower() or 'ansible' in repo['name'].lower()):
            if sum([1 for path in repo['dirs'] if filters.is_ansible_dir(path)]) < 2:
                # If the repo does not contain at least two among 'playbooks', 'roles', 'handlers', 'tasks', 'meta'
                # the discard it. Otherwise it means it has Ansible code, but not 'ansible' in the name or description
                continue

        clone_repo(repo['owner'], repo['name'])
        path_to_repo = os.path.join('tmp', repo['owner'], repo['name'])
        utils.save_ansible_repository(copy.deepcopy(repo))

        # Start analysis
        print(f'Starting analysis for {repo["name"]}')
        print(repo)
        
        git_repo = GitRepository(path_to_repo)
        repo_miner = RepositoryMiner(path_to_repo, branch=repo['default_branch'])
        labeled_files = repo_miner.mine(LabelTechnique.DEFECTIVE_FROM_OLDEST_BIC)
        
        if not labeled_files:
            continue

        # Save fixing commits
        utils.save_fixing_commits(f'{repo["owner"]}/{repo["name"]}', repo_miner.fixing_commits)

        # Group labeled files per release
        commit_file_map = dict()
        for file in labeled_files:
            if not filters.is_ansible_file(file.filepath):
                    continue
            
            utils.save_labeled_file(f'{repo["owner"]}/{repo["name"]}', file)
            commit_file_map.setdefault(file.commit, set()).add(file)

        # Extract metrics
        releases = [c.hash for c in RepositoryMining(path_to_repo, only_releases=True).traverse_commits()]

        release_starts_at = None
        
        metrics_miner = MetricsMiner()
        last_iac_metrics = dict() # Store the last iac metrics for each file

        for commit in RepositoryMining(path_to_repo).traverse_commits():

            if not release_starts_at:
                release_starts_at = commit.hash

            if commit.hash not in releases:
                continue
            
            try:
                process_metrics = metrics_miner.mine_process_metrics(path_to_repo, release_starts_at, commit.hash)
            except Exception as e:
                print(f'Problem with process metrics: {str(e)}')
                continue

            # Checkout to commit to extract product metrics from each file
            git_repo.checkout(commit.hash)
            
            for labeled_file in commit_file_map.get(commit.hash, []):
                
                # Compute product and text metrics
                file_content = get_content(os.path.join(path_to_repo, labeled_file.filepath))
                
                if not file_content:
                    print(f'commit: {commit.hash}. File not found')
                    continue

                try:
                    iac_metrics = metrics_miner.mine_product_metrics(file_content)
                except yaml.error.YAMLError:
                    print(f'commit: {commit.hash}. Cannot properly read yaml file')
                    continue
                
                tokens = metrics_miner.mine_text(file_content)
                
                delta_metrics = dict()

                if labeled_file.fixing_filepath in last_iac_metrics:
                    # Compute delta metrics
                    last = last_iac_metrics[labeled_file.fixing_filepath]
                    for k, v in iac_metrics.items():
                        k_delta = f'delta_{k}'
                        v_delta = v - last[k]
                        delta_metrics[k_delta] = round(v_delta, 3)

                last_iac_metrics[labeled_file.fixing_filepath] = iac_metrics

                # Save metrics
                metadata = {
                    'defective': 'yes' if labeled_file.label == LabeledFile.Label.DEFECT_PRONE else 'no',
                    'filepath': str(labeled_file.filepath),
                    'fixing_filepath': str(labeled_file.fixing_filepath),
                    'fixing_commit': str(labeled_file.fixing_commit),
                    'repo': f'{repo["owner"]}/{repo["name"]}',
                    'release_start': str(release_starts_at),
                    'release_end': str(commit.hash),
                    'release_date': str(commit.committer_date),
                    'tokens': ' '.join(tokens)
                }

                save(metadata, iac_metrics, delta_metrics, process_metrics)

            release_starts_at = None # So the next commit will be the start for the successive release
            git_repo.reset()    # Reset repository's status

        delete_repo(repo['owner'])

    print(f'{i} repositories mined')
    print(f'Quota: {github_miner.quota}')
    print(f'Quota will reset at: {github_miner.quota_reset_at}')

if __name__=='__main__':
    date_from = datetime.strptime('2019-10-21 12:00:00', '%Y-%m-%d %H:%M:%S')
    date_to = datetime.strptime('2019-10-22 00:00:00', '%Y-%m-%d %H:%M:%S')
    push_after=datetime.strptime('2019-09-08 00:00:00', '%Y-%m-%d %H:%M:%S')
    now = datetime.strptime('2020-03-09 00:00:00', '%Y-%m-%d %H:%M:%S')

    while date_to <= now:
        print(f'Searching for: {date_from}..{date_to}. Analysis started at {str(datetime.now())}')
        main(date_from, date_to, push_after)
        date_from = date_to
        date_to += timedelta(hours=12)