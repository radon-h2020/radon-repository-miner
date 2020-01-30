import os
import pandas as pd
import yaml

from io import StringIO

import pydriller.metrics.process.metrics as process_metrics

from pathlib import Path

from ansiblemetrics.main import MetricExtractor, LoadingError
from iacminer.entities.commit import Commit
from iacminer.entities.content import ContentFile

class MetricsMiner():

    def __init__(self):
        self.__ansible_metrics = MetricExtractor()
        self.__process_metrics = []
        self.__product_metrics = {}

    def mine_process_metrics(self, path_to_repo: str, from_commit_sha: str=None, to_commit: str=None) -> list:
        """
        Extract process metrics from a commit.
        Save the result in the instance and returns it.
        """

        commits_count = process_metrics.commits_count(path_to_repo, from_commit_sha, to_commit)
        contributors_count = process_metrics.contributors_count(path_to_repo, from_commit_sha, to_commit)
        highest_contributors_experience = process_metrics.highest_contributors_experience(path_to_repo, from_commit_sha, to_commit)
        #history_complexity_single_commit = None #process_metrics.history_complexity(path_to_repo, periods=[(from_commit_sha, to_sha)])
        hunks_count = process_metrics.hunks_count(path_to_repo, from_commit_sha, to_commit)
        median_hunks_count = process_metrics.hunks_count(path_to_repo, from_commit_sha, to_commit)
        lines_count = process_metrics.lines_count(path_to_repo, from_commit_sha, to_commit)
        
        self.__process_metrics = [
                commits_count,
                contributors_count,
                highest_contributors_experience,
                hunks_count,
                median_hunks_count,
                lines_count
            ]
        
        return self.__process_metrics
    
    def mine_product_metrics(self, file: ContentFile) -> list:
        """
        Extract product metrics from a file.
        Save the result in the instance and returns it.
        """
        # TODO: move exception handling outside? Or log instead of printing
        try:
            ansible_metrics = self.__ansible_metrics.run(StringIO(file.decoded_content))

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

    def save(self, file: ContentFile, defect_prone: bool=False):
        filepath = str(Path(file.filename))
        
        metrics = self.__product_metrics

        # Storing metadata
        metrics['filepath'] = filepath
        metrics['file_sha'] = file.sha
        metrics['commit_sha'] = file.commit_sha
        metrics['repository'] = file.repository
        metrics['release_starts_at'] = file.release_starts_at
        metrics['release_ends_at'] = file.release_ends_at
        metrics['defective'] = 'yes' if defect_prone else 'no'

        # Saving process metrics
        metrics['commits_count'] = self.__process_metrics[0].get(filepath, 0)
        metrics['contributors_count'] = self.__process_metrics[1].get(filepath, {}).get('contributors_count', 0)
        metrics['minor_contributors_count'] = self.__process_metrics[1].get(filepath, {}).get('minor_contributors_count', 0)
        metrics['highest_experience'] = self.__process_metrics[2].get(filepath, 0)
        metrics['commit_hunks_count'] = self.__process_metrics[3].get(filepath, 0)
        metrics['median_hunks_count'] = self.__process_metrics[4].get(filepath, 0)
        metrics['added_loc'] = self.__process_metrics[5].get(filepath, {}).get('added', 0)
        metrics['removed_loc'] = self.__process_metrics[5].get(filepath, {}).get('removed', 0)
        metrics['norm_added_loc'] = self.__process_metrics[5].get(filepath, {}).get('norm_added', 0)
        metrics['norm_removed_loc'] = self.__process_metrics[5].get(filepath, {}).get('norm_removed', 0)
        metrics['total_added_loc'] = self.__process_metrics[5].get(filepath, {}).get('total_added', 0)
        metrics['total_removed_loc'] = self.__process_metrics[5].get(filepath, {}).get('total_removed', 0)
        
        dataset = pd.DataFrame()
        
        if os.path.isfile(os.path.join('data', 'metrics.csv')):
            with open(os.path.join('data', 'metrics.csv'), 'r') as in_file:
                dataset = pd.read_csv(in_file)

        dataset = dataset.append(metrics, ignore_index=True)

        with open(os.path.join('data', 'metrics.csv'), 'w') as out:
            dataset.to_csv(out, mode='w', index=False)