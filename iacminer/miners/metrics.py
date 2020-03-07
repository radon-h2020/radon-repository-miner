import os
import pandas as pd

from io import StringIO

from pydriller.metrics.process.change_set import ChangeSet
from pydriller.metrics.process.code_churn import CodeChurn
from pydriller.metrics.process.commits_count import CommitsCount
from pydriller.metrics.process.contributors_count import ContributorsCount
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from pydriller.metrics.process.history_complexity import HistoryComplexity
from pydriller.metrics.process.hunks_count import HunksCount
from pydriller.metrics.process.lines_count import LinesCount

from pathlib import Path

from ansiblemetrics.metrics_extractor import MetricExtractor
from iacminer.text.text_processing import TextProcessing

class MetricsMiner():

    def mine_process_metrics(self, path_to_repo: str, from_commit: str, to_commit: str) -> list:
        """
        Extract and return process metrics from a commit.

        :from_commit: str - hash of release start
        :to_commit: str - hash of release end
        """
        change_set = ChangeSet(path_to_repo, from_commit, to_commit)
        code_churn = CodeChurn(path_to_repo, from_commit, to_commit)
        commits_count = CommitsCount(path_to_repo, from_commit, to_commit)
        contributors_count = ContributorsCount(path_to_repo, from_commit, to_commit)
        highest_contributors_experience = ContributorsExperience(path_to_repo, from_commit, to_commit)
        median_hunks_count = HunksCount(path_to_repo, from_commit, to_commit)
        lines_count = LinesCount(path_to_repo, from_commit, to_commit)
        #history_complexity = HistoryComplexity(path_to_repo, from_commit, to_commit).count()
        
        return [change_set.max(),
                change_set.avg(),
                code_churn.count(),
                code_churn.max(),
                code_churn.avg(),
                commits_count.count(),
                contributors_count.count(),
                contributors_count.count_minor(),
                highest_contributors_experience.count(),
                median_hunks_count.count(),
                lines_count.count_added(),
                lines_count.max_added(),
                lines_count.avg_added(),
                lines_count.count_removed(),
                lines_count.max_removed(),
                lines_count.avg_removed()]
            
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
                if 'relative' in k: # for the moment keep only absolute metrics
                    continue

                metric = f'{item}_{k}'
                value = ansible_metrics[item][k]
                product_metrics[metric] = value if value else 0

        return product_metrics

    def mine_text(self, content: str) -> list:
        """
        Extract textual metrics from a file.
        """
        return TextProcessing(content).process()
