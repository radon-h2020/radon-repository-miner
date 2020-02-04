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

DESTINATION_PATH = os.path.join('data', 'new_metrics.csv')

class MetricsMiner():

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

        return [
                commits_count,
                contributors_count,
                highest_contributors_experience,
                history_complexity,
                median_hunks_count,
                lines_count,
                lines_count_in_commit
            ]
    
    def mine_product_metrics(self, content: str) -> list:
        """
        Extract product metrics from a file.
        Save the result in the instance and returns it.
        """
        product_metrics = {}

        try:
            ansible_metrics = MetricExtractor().run(StringIO(content))

            for item in ansible_metrics:    
                if ansible_metrics[item]['count'] is None:
                    break

                for k in ansible_metrics[item]:
                    metric = f'{item}_{k}'
                    product_metrics[metric] = ansible_metrics[item][k]

        except LoadingError:
            print('\033[91m' + 'Error: failed to load {}. Insert a valid file!'.format('FILENAME HERE') + '\033[0m')
        except yaml.YAMLError:
            print('The input file is not a yaml file')
        except Exception:
            print('An unknown error has occurred')
            
        return product_metrics
