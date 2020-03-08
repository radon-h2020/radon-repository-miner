import copy
import git
import os
import pandas as pd
import shutil
import sys
import json

import github
import time
from datetime import datetime

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from pathlib import Path
from pydriller.repository_mining import GitRepository, RepositoryMining
from pydriller.domain.commit import ModificationType

from iacminer import filters
from iacminer.entities.release import Release
from iacminer.entities.repository import Repository
from iacminer.miners.repository_miner import RepositoryMiner
from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.github_miner import GithubMiner
from mygit import Git
from iacminer import utils

DESTINATION_PATH = os.path.join('data', 'metrics.csv')
"""
class Main():

    def __init__(self, repository: Repository):
        
        self.repository = repository
        self.__root_path = str(Path(f'repositories/{self.repository.owner}'))
        self.__repo_path = os.path.join(self.__root_path, self.repository.name)

        self.clone_repo()


        print(self.__git_repo.path)
        print(self.__repo_path)
        exit()
 

        git.Git(self.__root_path).clone(f'https://github.com/{self.repository.remote_path}.git')#, branch=self.repository.default_branch)
        git_repo = GitRepository(self.__repo_path)

        self.__git_repo = git_repo
    
    def get_content(self, filepath):
        with open(os.path.join(self.__repo_path, filepath), 'r') as f:
            return f.read()
    

    def save(self, filepath:str, metadata:dict, process_metrics:dict, product_metrics:dict, delta_metrics:dict):
        
        filepath = str(Path(filepath))
        
        metrics = metadata
        metrics.update(product_metrics)
        metrics.update(delta_metrics)

        # Saving process metrics
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
        
        dataset = pd.DataFrame()
        
        if os.path.isfile(DESTINATION_PATH):
            with open(DESTINATION_PATH, 'r') as in_file:
                dataset = pd.read_csv(in_file)

        dataset = dataset.append(metrics, ignore_index=True)

        with open(DESTINATION_PATH, 'w') as out:
            dataset.to_csv(out, mode='w', index=False)

    def run(self, branch: str='master'):
        
        repository_miner = RepositoryMiner(self.__git_repo, branch)
        metrics_miner = MetricsMiner()

        releases = []
        releases_hash = []
        releases_date = []
        commits_hash = []

        for commit in RepositoryMining(self.__repo_path, only_releases=True).traverse_commits():
            releases_hash.append(commit.hash)
            releases_date.append(str(commit.committer_date))

        for commit in RepositoryMining(self.__repo_path).traverse_commits():
            commits_hash.append(commit.hash)

        tmp_releases_hash = releases_hash.copy()
        while tmp_releases_hash:
            hash = tmp_releases_hash.pop(0)
            date = releases_date.pop(0)
            idx = commits_hash.index(hash)
            releases.append(Release(commits_hash[0], commits_hash[idx], date))
            del commits_hash[:idx+1]

        # Mine fixing commits
        repository_miner.mine()
        
        previous_release_product_metrics = dict()

        for i in range(0, len(releases)-1):
            
            release = releases[i]

            # If the release does not have any affected files, do not consider it
            if not repository_miner.defect_prone_files.get(release.end) and not repository_miner.defect_free_files.get(release.end):
                continue

            process_metrics = metrics_miner.mine_process_metrics(self.__repo_path, release.start, release.end)
            self.__git_repo.checkout(release.end)
            
            metadata = {
                'repo': self.repository.remote_path,
                'release_start': release.start,
                'release_end': release.end,
                'release_date': release.date                    
            }

            # Getting filenames in previous release
            renamed_files = dict()
            previous_name_of = dict()
            
            if i < len(releases)-1:
                for commit in RepositoryMining(self.__repo_path, from_commit=release.end, to_commit=releases[i+1].end).traverse_commits():

                    for modified_file in commit.modifications:

                        if modified_file.change_type != ModificationType.RENAME:
                            continue

                        oldest_filepath = renamed_files.get(modified_file.old_path,
                                                            modified_file.old_path)
                        renamed_files[modified_file.new_path] = modified_file.old_path
                        previous_name_of[modified_file.new_path] = oldest_filepath
                
                    if commit.hash in releases_hash and commit.hash != release.end:
                        break

            defect_prone_files = repository_miner.defect_prone_files.get(release.end, set())
            unclassified_files = repository_miner.defect_free_files.get(release.end, set())

            for filepath in defect_prone_files.union(unclassified_files):
                
                if not filters.is_ansible_file(filepath):
                    continue

                try:
                    file_content = self.get_content(filepath)
                    product_metrics = metrics_miner.mine_product_metrics(file_content)
                    tokens = metrics_miner.mine_text(file_content)
                except Exception as e:
                    print(f'commit: {release.end}')
                    print(str(e))
                    continue
                
                #### DELTA METRICS 
                previous_filepath = previous_name_of.get(filepath, filepath)
                delta_metrics = dict()

                for k, v in product_metrics.items():
                    delta_k = f'delta_{k}'
                    delta_v = v - previous_release_product_metrics.get(previous_filepath, {}).get(k, 0)
                    delta_metrics[delta_k] = round(delta_v, 3)

                previous_release_product_metrics[filepath] = product_metrics
                #### END DELTA METRICS

                metadata['filepath'] = filepath
                metadata['defective'] = 'yes' if filepath in defect_prone_files else 'no'
                metadata['tokens'] = ' '.join(tokens)
                self.save(filepath, metadata, process_metrics, product_metrics, delta_metrics=delta_metrics)

            self.__git_repo.reset()
        
        self.__git_repo.clear()
        self.delete_repo()
"""

def all_files(path_to_root):
    """
    Get the set of all the files in a folder (excluding .git directory)
    
    Parameters
    ----------
    path_to_root : str : the path to the root of the directory to analyze

    Return
    ----------
    files : set : the set of strings (filepaths)
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
    Clone a repository on local machine
    
    Parameters
    ----------
    owner : str : the name of the owner of the repository

    name : str : the name of the repository
    """

    path_to_owner = os.path.join('tmp', owner)
    if not os.path.isdir(path_to_owner):
        os.makedirs(path_to_owner)

    git.Git(path_to_owner).clone(f'https://github.com/{owner}/{name}.git')#, branch=self.repository.default_branch)

def delete_repo(owner: str):
    """
    Delete a local repository
    
    Parameters
    ----------
    owner : str : the name of the owner of the repository
    """

    path_to_owner = os.path.join('tmp', owner)

    if os.path.isdir(path_to_owner):
        shutil.rmtree(path_to_owner)

def main():
    ansible_repositories = utils.load_ansible_repositories()
    i = 0 
    
    for repo in ansible_repositories:
    
        i += 1

        # Check if ansible repository
        # 1) filter by files in repo.dirs (This to avoid cloning more repo before check)
        if not any(filters.is_ansible_dir(path) for path in repo.dirs):
            continue

        clone_repo(repo.owner, repo.name)
        
        path_to_repo = os.path('tmp', repo.owner, repo.name)
        if any(filters.is_ansible_file(path) for path in all_files(path_to_repo)):
            print(f'{i} - Starting analysis for {repo.name}')
            repo_miner = RepositoryMiner(path_to_repo)#, branch=repo.default_branch)
            labeled_files = repo_miner.mine()
            print(labeled_files)
            # Compute process
            # Compute product metrics
            # Compute text metrics
        delete_repo(repo.owner)
        exit()


    
if __name__=='__main__':

    """
    miner = GithubMiner(
        date_from=datetime.strptime('2014-01-01', '%Y-%m-%d'),
        date_to=datetime.strptime('2020-01-01', '%Y-%m-%d'),
        pushed_after=datetime.strptime('2019-01-01', '%Y-%m-%d'),
        min_stars=1000,
        min_releases=1
    )
    
    miner.set_token(os.getenv('GITHUB_ACCESS_TOKEN'))
    for repo in miner.mine():
        utils.save_ansible_repositories(copy.deepcopy(repo))
        mine repository
    exit()
    """
    main()