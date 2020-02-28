import copy
import git
import os
import pandas as pd
import shutil
import sys
import json

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from pathlib import Path
from pydriller.repository_mining import GitRepository, RepositoryMining
from pydriller.domain.commit import ModificationType

from iacminer import filters
from iacminer.configuration import Configuration
from iacminer.entities.release import Release
from iacminer.entities.repository import Repository
from iacminer.miners.commits import CommitsMiner
from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.repositories import RepositoryMiner
from iacminer import utils

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

        git.Git(self.__root_path).clone(f'https://github.com/{self.repository.remote_path}.git')#, branch=self.repository.default_branch)
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

    def save(self, filepath:str, metadata:dict, process_metrics:dict, product_metrics:dict, delta_metrics:dict):
        
        filepath = str(Path(filepath))
        
        metrics = metadata
        metrics.update(product_metrics)
        metrics.update(delta_metrics)

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
        commits_miner.mine()
        
        previous_release_product_metrics = dict()
        
        for i in range(0, len(releases)-1):
            
            release = releases[i]

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
                        renamed_files[modified_file.new_path] = filepath
                        previous_name_of[modified_file.new_path] = oldest_filepath
                
                    if commit.hash in releases_hash and commit.hash != release.end:
                        break
            
            defect_prone_files = commits_miner.defect_prone_files.get(release.end, set())
            unclassified_files = commits_miner.defect_free_files.get(release.end, set())
            
            for filepath in defect_prone_files.union(unclassified_files):
                
                if not filters.is_ansible_file(filepath):
                    continue

                try:
                    file_content = self.get_content(filepath)
                except Exception as e:
                    print(release.end)
                    print(str(e))
                    continue

                
                product_metrics = metrics_miner.mine_product_metrics(file_content)
                tokens = metrics_miner.mine_text(file_content)

                #### DELTA METRICS 
                previous_filepath = previous_name_of.get(filepath, filepath)
                delta_metrics = dict()

                for k, v in product_metrics.items():
                    delta_k = f'delta_{k}'
                    delta_metrics[delta_k] = v - previous_release_product_metrics.get(previous_filepath, {}).get(k, 0)


                previous_release_product_metrics[filepath] = product_metrics

                #### END DELTA METRICS
                
                metadata['filepath'] = filepath
                metadata['defective'] = 'yes' if filepath in defect_prone_files else 'no'
                metadata['tokens'] = ' '.join(tokens)
                self.save(filepath, metadata, process_metrics, product_metrics, delta_metrics)

            self.__git_repo.reset()
        
        self.__git_repo.clear()
        self.delete_repo()

if __name__=='__main__':

    ansible_repositories = utils.load_ansible_repositories()

    """ This is for the entire process
    for repo in RepositoryMiner(Configuration()).mine():
        if repo in ansible_repositories:
            continue
    
        main = Main(repo)
        
        n_ansible_files = 0
        all_files = main.all_files()

        for filepath in all_files:
            if filters.is_ansible_file(filepath):
                n_ansible_files += 1
        
        if n_ansible_files == 0:
            main.delete_repo()
            continue
        
        ansible_repositories.append(copy.deepcopy(repo))
        utils.save_ansible_repositories(ansible_repositories)

        repository_count = len(ansible_repositories)
        print(f'{repository_count} - Starting analysis for {repo.remote_path}')
        main.run(branch=repo.default_branch)
    """

    #labels = {}
    #from mygit import Git
    #g = Git()

    i = 0

    for repo in ansible_repositories:
        """
        print(f'Starting analysis for {repo.remote_path}')
        for issue in g.get_all_issues(repo.remote_path):
            if not issue:
                continue
            for label in issue.labels:
                labels[label.name] = labels.get(label.name, 0) + 1

        print(str(labels))
        """
        i += 1
        #if i <= X:
        #    continue
        print(f'{i} Starting analysis for {repo.remote_path}')
        main = Main(repo)
        main.run()