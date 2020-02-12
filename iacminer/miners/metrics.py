import os
import pandas as pd

from io import StringIO

from pydriller.metrics.process.commits_count import CommitsCount
from pydriller.metrics.process.contributors_count import ContributorsCount
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from pydriller.metrics.process.history_complexity import HistoryComplexity
from pydriller.metrics.process.hunks_count import HunksCount
from pydriller.metrics.process.lines_count import LinesCount

from pathlib import Path

from ansiblemetrics.main import MetricExtractor
from iacminer.text.text_processing import TextProcessing

class MetricsMiner():

    def mine_process_metrics(self, path_to_repo: str, from_commit: str, to_commit: str) -> list:
        """
        Extract and return process metrics from a commit.

        :from_commit: str - hash of release start
        :to_commit: str - hash of release end
        """
        commits_count = CommitsCount(path_to_repo, from_commit, to_commit).count()
        contributors_count = ContributorsCount(path_to_repo, from_commit, to_commit).count()
        highest_contributors_experience = ContributorsExperience(path_to_repo, from_commit, to_commit).count()
        history_complexity = HistoryComplexity(path_to_repo, from_commit, to_commit).count()
        median_hunks_count = HunksCount(path_to_repo, from_commit, to_commit).count()
        lines_count = LinesCount(path_to_repo, from_commit, to_commit).count()
        #lines_count_in_commit = LinesCount(path_to_repo, commit_hash, commit_hash).count()

        return [
                commits_count,
                contributors_count,
                highest_contributors_experience,
                history_complexity,
                median_hunks_count,
                lines_count
                #lines_count_in_commit
            ]
            
    def mine_product_metrics(self, content: str) -> list:
        """
        Extract and return product metrics from a file.
        """
        product_metrics = {}

        ansible_metrics = MetricExtractor().run(StringIO(content))

        for item in ansible_metrics:    
            if ansible_metrics[item]['count'] is None:
                break

            for k in ansible_metrics[item]:
                metric = f'{item}_{k}'
                product_metrics[metric] = ansible_metrics[item][k]

    
        return product_metrics

    def mine_text(self, content: str) -> list:
        """
        Extract textual metrics from a file.
        """
        return TextProcessing(content).process()
