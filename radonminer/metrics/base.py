import os
import pandas as pd

from typing import List
from pydriller.git_repository import GitRepository
from pydriller.repository_mining import RepositoryMining
from pydriller.metrics.process.change_set import ChangeSet
from pydriller.metrics.process.code_churn import CodeChurn
from pydriller.metrics.process.commits_count import CommitsCount
from pydriller.metrics.process.contributors_count import ContributorsCount
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from pydriller.metrics.process.hunks_count import HunksCount
from pydriller.metrics.process.lines_count import LinesCount

from radonminer.file import LabeledFile


def get_content(path: str) -> str:
    """
    Get the content of a file as plain text.

    :param path: str : the path to the file.
    :return: the content of the file, if exists; None otherwise.
    """
    if not os.path.isfile(path):
        return ''

    with open(path, 'r') as f:
        return f.read()


class BaseMetricsExtractor:

    def __init__(self, path_to_repo: str):
        self.path_to_repo = path_to_repo
        self.git_repo = GitRepository(path_to_repo)
        self.dataset = pd.DataFrame()

    def get_product_metrics(self, script: str) -> dict:
        """
        Extract product metrics from a script
        """
        return dict()

    def get_process_metrics(self, from_commit: str, to_commit: str) -> dict:
        """
        Extract and return process metrics from a commit.
        :param from_commit: str - hash of release start
        :param to_commit: str - hash of release end
        """
        change_set = ChangeSet(self.path_to_repo, from_commit=from_commit, to_commit=to_commit)
        code_churn = CodeChurn(self.path_to_repo, from_commit=from_commit, to_commit=to_commit)
        commits_count = CommitsCount(self.path_to_repo, from_commit=from_commit, to_commit=to_commit)
        contributors_count = ContributorsCount(self.path_to_repo, from_commit=from_commit, to_commit=to_commit)
        highest_contributors_experience = ContributorsExperience(self.path_to_repo, from_commit=from_commit,
                                                                 to_commit=to_commit)
        median_hunks_count = HunksCount(self.path_to_repo, from_commit=from_commit, to_commit=to_commit)
        lines_count = LinesCount(self.path_to_repo, from_commit=from_commit, to_commit=to_commit)

        return {
            'dict_change_set_max': change_set.max(),
            'dict_change_set_avg': change_set.avg(),
            'dict_code_churn_count': code_churn.count(),
            'dict_code_churn_max': code_churn.max(),
            'dict_code_churn_avg': code_churn.avg(),
            'dict_commits_count': commits_count.count(),
            'dict_contributors_count': contributors_count.count(),
            'dict_minor_contributors_count': contributors_count.count_minor(),
            'dict_highest_contributor_experience': highest_contributors_experience.count(),
            'dict_hunks_median': median_hunks_count.count(),
            'dict_additions': lines_count.count_added(),
            'dict_additions_max': lines_count.max_added(),
            'dict_additions_avg': lines_count.avg_added(),
            'dict_deletions': lines_count.count_removed(),
            'dict_deletions_max': lines_count.max_removed(),
            'dict_deletions-avg': lines_count.avg_removed()}

    def extract(self, labeled_files: List[LabeledFile], product: bool = True, process: bool = True,
                delta: bool = False, at: str = 'release'):

        commits_or_releases = list(RepositoryMining(path_to_repo=self.path_to_repo,
                                                    only_releases=True if at == 'release' else False,
                                                    order='date-order').traverse_commits())

        for i in range(len(commits_or_releases)):
            commit = commits_or_releases[i]

            self.git_repo.checkout(commit.hash)

            if process:
                # Extract process metrics
                from_previous_commit = commit.hash if i == 0 else commits_or_releases[i - 1].hash
                to_current_commit = commit.hash
                process_metrics = self.get_process_metrics(from_previous_commit, to_current_commit)

            for modified_file in commit.modifications:
                idx = labeled_files.index(LabeledFile(filepath=modified_file.new_path, commit=commit.hash,
                                                      label=None, fixing_commit=''))
                if idx > -1:
                    content = get_content(os.path.join(self.path_to_repo, modified_file.new_path))

                    metrics = dict(
                        filepath=modified_file.new_path,
                        commit=commit.hash,
                        committed_at=str(commit.committer_date),
                        failure_prone=1 if labeled_files[idx].label == LabeledFile.Label.FAILURE_PRONE else 0
                    )

                    if process_metrics:
                        metrics['change_set_max'] = process_metrics['dict_change_set_max']
                        metrics['change_set_avg'] = process_metrics['dict_change_set_avg']
                        metrics['code_churn_count'] = process_metrics['dict_code_churn_count'].get(
                            modified_file.new_path)
                        metrics['code_churn_max'] = process_metrics['dict_code_churn_max'].get(modified_file.new_path)
                        metrics['code_churn_avg'] = process_metrics['dict_code_churn_avg'].get(modified_file.new_path)
                        metrics['commits_count'] = process_metrics['dict_commits_count'].get(modified_file.new_path)
                        metrics['contributors_count'] = process_metrics['dict_contributors_count'].get(
                            modified_file.new_path)
                        metrics['minor_contributors_count'] = process_metrics['dict_minor_contributors_count'].get(
                            modified_file.new_path)
                        metrics['highest_contributor_experience'] = process_metrics[
                            'dict_highest_contributor_experience'].get(
                            modified_file.new_path)
                        metrics['hunks_median'] = process_metrics['dict_hunks_median'].get(modified_file.new_path)
                        metrics['additions'] = process_metrics['dict_additions'].get(modified_file.new_path)
                        metrics['additions'] = process_metrics['dict_additions_max'].get(modified_file.new_path)
                        metrics['additions_avg'] = process_metrics['dict_additions_avg'].get(modified_file.new_path)
                        metrics['deletions'] = process_metrics['dict_deletions'].get(modified_file.new_path)
                        metrics['deletions_max'] = process_metrics['dict_deletions_max'].get(modified_file.new_path)
                        metrics['deletions_avg'] = process_metrics['dict_deletions_avg'].get(modified_file.new_path)

                    if product:
                        metrics.update(self.get_product_metrics(content))

                    self.dataset = self.dataset.append(metrics, ignore_index=True)

            self.git_repo.reset()

    def to_csv(self, path_to_folder):
        """
        Save the metrics as csv
        :param path_to_folder: path to the folder where to save the csv
        """
        with open(os.path.join(path_to_folder), 'w') as out:
            self.dataset.to_csv(out, mode='w', index=False)
