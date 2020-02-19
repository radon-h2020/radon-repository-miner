import git
import os
import pandas as pd
import shutil
import sys

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from pathlib import Path
from pydriller.repository_mining import GitRepository, RepositoryMining

from iacminer import filters
from iacminer.configuration import Configuration
from iacminer.entities.release import Release
from iacminer.entities.repository import Repository
from iacminer.miners.commits import CommitsMiner
from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.repositories import RepositoryMiner
from iacminer.utils import load_repositories

DESTINATION_PATH = os.path.join('data', 'metrics.csv')

class Main():

    def __init__(self, repository: Repository):
        
        self.repository = repository
        self.__root_path = str(Path(f'repositories/{self.repository.owner}'))
        self.__repo_path = os.path.join(self.__root_path, self.repository.name)

        self.clone_repo()
        

    def delete_repo(self):
        if os.path.isdir(self.__root_path):
            shutil.rmtree(self.__root_path)

    def clone_repo(self):
        self.delete_repo()
        os.makedirs(self.__root_path)

        git.Git(self.__root_path).clone(f'https://github.com/{self.repository.remote_path}.git', branch='master')
        git_repo = GitRepository(self.__repo_path)

        self.__git_repo = git_repo
    
    def get_content(self, filepath):
        with open(os.path.join(self.__repo_path, filepath), 'r') as f:
            return f.read()
    
    def all_files(self):
        """
        Obtain the list of the files (excluding .git directory).

        :return: the set of the files
        """
        _all = set()

        for root, _, filenames in os.walk(str(self.__repo_path)):
            if '.git' in root:
                continue
            for filename in filenames: 
                path = os.path.join(root, filename)
                path = path.replace(str(self.__repo_path), '')
                if path.startswith('/'):
                    path = path[1:]

                _all.add(path)

        return _all

    def save(self, filepath:str, metadata:dict, process_metrics:dict, product_metrics:dict):
        
        filepath = str(Path(filepath))
        
        metrics = metadata
        metrics.update(product_metrics)

        # Saving process metrics
        metrics['commits_count'] = process_metrics[0].get(filepath, 0)
        metrics['contributors_count'] = process_metrics[1].get(filepath, {}).get('contributors_count', 0)
        metrics['minor_contributors_count'] = process_metrics[1].get(filepath, {}).get('minor_contributors_count', 0)
        metrics['highest_experience'] = process_metrics[2].get(filepath, 0)
        metrics['history_complexity'] = process_metrics[3].get(filepath, 0)
        metrics['median_hunks_count'] = process_metrics[4].get(filepath, 0)
        metrics['total_added_loc'] = process_metrics[5].get(filepath, {}).get('added', 0)
        metrics['total_removed_loc'] = process_metrics[5].get(filepath, {}).get('removed', 0)

        dataset = pd.DataFrame()
        
        if os.path.isfile(DESTINATION_PATH):
            with open(DESTINATION_PATH, 'r') as in_file:
                dataset = pd.read_csv(in_file)

        dataset = dataset.append(metrics, ignore_index=True)

        with open(DESTINATION_PATH, 'w') as out:
            dataset.to_csv(out, mode='w', index=False)

    def run(self, branch: str='master'):
        
        commits_miner = CommitsMiner(self.__git_repo, branch)
        metrics_miner = MetricsMiner()

        releases = []
        releases_hash = []
        releases_date = []
        commits_hash = []

        for commit in RepositoryMining(self.__repo_path, only_releases=True).traverse_commits():
            releases_hash.append(commit.hash)
            releases_date.append(str(commit.committer_date))

        for commit in RepositoryMining(self.__repo_path, only_in_branch='master').traverse_commits():
            commits_hash.append(commit.hash)

        while releases_hash:
            hash = releases_hash.pop(0)
            date = releases_date.pop(0)
            idx = commits_hash.index(hash)
            releases.append(Release(commits_hash[0], commits_hash[idx], date))
            del commits_hash[:idx+1]

        # Mine fixing commits
        commits_miner.mine()

        for release in releases:

            # If the release does not have any affected files, do not consider it
            if not commits_miner.defect_prone_files.get(release.end) and not commits_miner.defect_free_files.get(release.end):
                continue

            process_metrics = metrics_miner.mine_process_metrics(self.__repo_path, release.start, release.end)
            self.__git_repo.checkout(release.end)

            metadata = {
                    'repo': self.repository.remote_path,
                    'release_start': release.start,
                    'release_end': release.end,
                    'release_date': release.date                    
            }

            defect_prone_files = commits_miner.defect_prone_files.get(release.end, set())
            #unclassified_files = self.all_files() - defect_prone_files
            unclassified_files = commits_miner.defect_free_files.get(release.end, set())

            for filepath in defect_prone_files:
                metadata['filepath'] = filepath
                metadata['defective'] = 'yes'

                try:
                    file_content = self.get_content(filepath)
                    product_metrics = metrics_miner.mine_product_metrics(file_content)
                    tokens = metrics_miner.mine_text(file_content)
                    metadata['tokens'] = ' '.join(tokens)
                    self.save(filepath, metadata, process_metrics, product_metrics)

                except Exception:
                    pass#print(f'An unknown error has occurred for file X)

            for filepath in unclassified_files:
                if not filters.is_ansible_file(filepath):
                    continue

                metadata['filepath'] = filepath
                metadata['defective'] = 'no'

                try:
                    file_content = self.get_content(filepath)
                    product_metrics = metrics_miner.mine_product_metrics(file_content)
                    tokens = metrics_miner.mine_text(file_content)
                    metadata['tokens'] = ' '.join(tokens)
                    self.save(filepath, metadata, process_metrics, product_metrics)

                except Exception:
                    pass#print(f'An unknown error has occurred for file X')

            self.__git_repo.reset()
        
        self.__git_repo.clear()
        self.delete_repo()

if __name__=='__main__':

    repository_count =  0

    for repo in RepositoryMiner(Configuration()).mine():
        repository_count += 1
        print(f'{repository_count} - Repository: {repo.remote_path}')
        print(f'\tMain branch: {repo.default_branch}')
        print(f'\tStars: {repo.stars}')
        print(f'\tReleases: {repo.releases}')
        print(f'\tIssues: {repo.issues}')

        main = Main(repo)
        
        ansible_files = 0
        all_files = main.all_files()

        for filepath in all_files:
            if filters.is_ansible_file(filepath):
                ansible_files += 1
        
        print(f'\tAnsible files: {ansible_files}')

        if ansible_files/len(all_files) < 0.11:
            main.delete_repo()
            continue

        # Save 
        # {
        #   total_repositories: repository_count,
        #   ansible_repositories:{
        #      repo_info
        #   }
        # }
        # ansible repo in ansible_repositories.json
        print(f'Starting analysis for {repo.remote_path}')
        main.run(branch=repo['defaultBranchRef'])


        # filter ansible repo


"""
def save(self, repository):
                
    if os.path.isfile(DESTINATION_PATH):
        with open(DESTINATION_PATH, 'r') as in_file:
            dataset = pd.read_csv(in_file)

    dataset = dataset.append(metrics, ignore_index=True)

    with open(DESTINATION_PATH, 'w') as out:
        dataset.to_csv(out, mode='w', index=False)

def load_repositories():
    patah = os.path.join('data', 'repositories.json')
    if os.path.isfile(path):
        with open(path, 'r') as in_file:
            return json.load(in_file) 

def save_json(fixing_commits, filename: str):
    with open(os.path.join('data', filename), 'w') as outfile:
        return json.dump(fixing_commits, outfile)
"""