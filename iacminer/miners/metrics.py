import os
import pandas as pd
import yaml

from io import StringIO

from pydriller.metrics.process.commits_count import CommitsCount
from pydriller.metrics.process.contributors_count import ContributorsCount
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from pydriller.metrics.process.history_complexity import HistoryComplexity
from pydriller.metrics.process.hunks_count import HunksCount
from pydriller.metrics.process.lines_count import LinesCount

from pathlib import Path

from ansiblemetrics.main import MetricExtractor, LoadingError
from iacminer.entities.commit import BuggyInducingCommit
from iacminer.entities.content import ContentFile

DESTINATION_PATH = os.path.join('data', 'metrics.csv')

class MetricsMiner():

    def __init__(self):
        self.__ansible_metrics = MetricExtractor()
        self.__process_metrics = []
        self.__product_metrics = {}

    def mine_process_metrics(self, path_to_repo: str, commit_hash: str, from_commit: str=None, to_commit: str=None) -> list:
        """
        Extract process metrics from a commit.
        Save the result in the instance and returns it.

        :commit_hash: str - hash of buggy inducing commit
        :from_commit: str - hash of release start
        :to_commit: str - hash of release end
        """

        commits_count = CommitsCount(path_to_repo, from_commit, to_commit).count()
        contributors_count = ContributorsCount(path_to_repo, from_commit, to_commit).count()
        highest_contributors_experience = ContributorsExperience(path_to_repo, from_commit, to_commit).count()
        history_complexity = HistoryComplexity(path_to_repo, from_commit, to_commit).count()
        median_hunks_count = HunksCount(path_to_repo, from_commit, to_commit).count()
        lines_count = LinesCount(path_to_repo, from_commit, to_commit).count()
        lines_count_in_commit = LinesCount(path_to_repo, commit_hash, commit_hash).count()

        self.__process_metrics = [
                commits_count,
                contributors_count,
                highest_contributors_experience,
                history_complexity,
                median_hunks_count,
                lines_count,
                lines_count_in_commit
            ]
        
        return self.__process_metrics
    
    def mine_product_metrics(self, content: str) -> list:
        """
        Extract product metrics from a file.
        Save the result in the instance and returns it.
        """
        # TODO: move exception handling outside? Or log instead of printing
        try:
            ansible_metrics = self.__ansible_metrics.run(StringIO(content))

            for item in ansible_metrics:    
                if ansible_metrics[item]['count'] is None:
                    break

                for k in ansible_metrics[item]:
                    metric = f'{item}_{k}'
                    self.__product_metrics[metric] = ansible_metrics[item][k]

        except LoadingError:
            print('\033[91m' + 'Error: failed to load {}. Insert a valid file!'.format('FILENAME HERE') + '\033[0m')
        except yaml.YAMLError:
            print('The input file is not a yaml file')
        except Exception:
            print('An unknown error has occurred')
            
        return self.__product_metrics

    def save(self, filepath:str, metadata:dict):
        """
        :filepath: str - the filepath for the process metrics
        """
        
        filepath = str(Path(filepath))
        
        metrics = metadata
        metrics.update(self.__product_metrics)

        # Saving process metrics
        metrics['commits_count'] = self.__process_metrics[0].get(filepath, None)
        metrics['contributors_count'] = self.__process_metrics[1].get(filepath, {}).get('contributors_count', None)
        metrics['minor_contributors_count'] = self.__process_metrics[1].get(filepath, {}).get('minor_contributors_count', None)
        metrics['highest_experience'] = self.__process_metrics[2].get(filepath, None)
        metrics['highest_experience'] = self.__process_metrics[3].get(filepath, None)
        metrics['median_hunks_count'] = self.__process_metrics[4].get(filepath, None)
        metrics['total_added_loc'] = self.__process_metrics[5].get(filepath, {}).get('added', None)
        metrics['total_removed_loc'] = self.__process_metrics[5].get(filepath, {}).get('removed', None)
        metrics['norm_added_loc'] = self.__process_metrics[6].get(filepath, {}).get('added', None)
        metrics['norm_removed_loc'] = self.__process_metrics[6].get(filepath, {}).get('removed', None)

        if metrics['total_added_loc'] and metrics['norm_added_loc']:
            metrics['norm_added_loc'] /= metrics['total_added_loc']
        
        if metrics['total_removed_loc'] and metrics['norm_removed_loc']:
            metrics['norm_removed_loc'] /= metrics['total_removed_loc']

        dataset = pd.DataFrame()
        
        if os.path.isfile(DESTINATION_PATH):
            with open(DESTINATION_PATH, 'r') as in_file:
                dataset = pd.read_csv(in_file)

        dataset = dataset.append(metrics, ignore_index=True)

        with open(DESTINATION_PATH, 'w') as out:
            dataset.to_csv(out, mode='w', index=False)
