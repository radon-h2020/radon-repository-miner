import os
import pandas as pd
import re

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

from repominer.files import FailureProneFile

full_name_pattern = re.compile(r'git(hub|lab){1}\.com/([\w\W]+)$')


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


def is_remote(repo: str) -> bool:
    return repo.startswith("git@") or repo.startswith("https://")


class BaseMetricsExtractor:

    def __init__(self, path_to_repo: str, at: str = 'release'):

        if at not in ('release', 'commit'):
            raise ValueError(f'{at} is not valid! Try with \'release\' or \'commit\'.')

        if os.path.isdir(path_to_repo):
            self.path_to_repo = path_to_repo
            self.repo_miner = RepositoryMining(path_to_repo=path_to_repo,
                                               only_releases=True if at == 'release' else False,
                                               order='date-order')
        elif is_remote(path_to_repo):
            match = full_name_pattern.search(path_to_repo.replace('.git', ''))
            repo_name = match.groups()[1].split('/')[1]
            path_to_clone = os.path.join(os.getenv('TMP_REPOSITORIES_DIR'), repo_name)
            self.path_to_repo = path_to_clone

            self.repo_miner = RepositoryMining(path_to_repo=path_to_repo,
                                               clone_repo_to=os.getenv('TMP_REPOSITORIES_DIR') if not os.path.isdir(
                                                   path_to_clone) else None,
                                               only_releases=True if at == 'release' else False,
                                               order='date-order')

        else:
            raise ValueError(f'{path_to_repo} does not seem a path or url to a Git repository.')

        self.dataset = pd.DataFrame()

    def get_files(self) -> set:
        """
        Return all the files in the repository
        :return: a set of strings representing the path of the files in the repository
        """

        files = set()

        for root, _, filenames in os.walk(self.path_to_repo):
            if '.git' in root:
                continue
            for filename in filenames:
                path = os.path.join(root, filename)
                path = path.replace(self.path_to_repo, '')
                if path.startswith('/'):
                    path = path[1:]

                files.add(path)

        return files

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
            'dict_deletions_avg': lines_count.avg_removed()}

    def extract(self,
                labeled_files: List[FailureProneFile],
                product: bool = True,
                process: bool = True,
                delta: bool = False):

        commits_or_releases = list(self.repo_miner.traverse_commits())

        git_repo = GitRepository(self.path_to_repo)

        for i in range(len(commits_or_releases)):
            commit = commits_or_releases[i]

            git_repo.checkout(commit.hash)

            if process:
                # Extract process metrics
                from_previous_commit = commit.hash if i == 0 else commits_or_releases[i - 1].hash
                to_current_commit = commit.hash
                process_metrics = self.get_process_metrics(from_previous_commit, to_current_commit)

            # get all file paths from the root of the repository at this commit
            for filepath in self.get_files():

                file_content = get_content(os.path.join(self.path_to_repo, filepath))

                if self.ignore_file(filepath, file_content):
                    continue

                tmp = FailureProneFile(filepath=filepath, commit=commit.hash, fixing_commit='')
                if tmp not in labeled_files:
                    label = 0  # clean
                else:
                    label = 1  # failure-prone

                metrics = dict(
                    filepath=filepath,
                    commit=commit.hash,
                    committed_at=str(commit.committer_date),
                    failure_prone=label
                )

                if process_metrics:
                    metrics['change_set_max'] = process_metrics['dict_change_set_max']
                    metrics['change_set_avg'] = process_metrics['dict_change_set_avg']
                    metrics['code_churn_count'] = process_metrics['dict_code_churn_count'].get(filepath)
                    metrics['code_churn_max'] = process_metrics['dict_code_churn_max'].get(filepath)
                    metrics['code_churn_avg'] = process_metrics['dict_code_churn_avg'].get(filepath)
                    metrics['commits_count'] = process_metrics['dict_commits_count'].get(filepath)
                    metrics['contributors_count'] = process_metrics['dict_contributors_count'].get(filepath)
                    metrics['minor_contributors_count'] = process_metrics['dict_minor_contributors_count'].get(filepath)
                    metrics['highest_contributor_experience'] = process_metrics[
                        'dict_highest_contributor_experience'].get(filepath)
                    metrics['hunks_median'] = process_metrics['dict_hunks_median'].get(filepath)
                    metrics['additions'] = process_metrics['dict_additions'].get(filepath)
                    metrics['additions_max'] = process_metrics['dict_additions_max'].get(filepath)
                    metrics['additions_avg'] = process_metrics['dict_additions_avg'].get(filepath)
                    metrics['deletions'] = process_metrics['dict_deletions'].get(filepath)
                    metrics['deletions_max'] = process_metrics['dict_deletions_max'].get(filepath)
                    metrics['deletions_avg'] = process_metrics['dict_deletions_avg'].get(filepath)

                if product:
                    metrics.update(self.get_product_metrics(file_content))

                self.dataset = self.dataset.append(metrics, ignore_index=True)

            git_repo.reset()

    def ignore_file(self, path_to_file: str, content: str = None):
        return False

    def to_csv(self, path_to_folder):
        """
        Save the metrics as csv
        :param path_to_folder: path to the folder where to save the csv
        """
        with open(os.path.join(path_to_folder), 'w') as out:
            self.dataset.to_csv(out, mode='w', index=False)
