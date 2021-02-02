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

from typing import Any, Dict, Set, Union

full_name_pattern = re.compile(r'git(hub|lab)\.com/([\w\W]+)$')


def get_content(path: str) -> Union[str, None]:
    """ Get the content of a file as plain text.

    Parameters
    ----------
    path : str
        The path to the file.

    Return
    ------
    str
        The file's content, if exists; None otherwise.

    """
    if not os.path.isfile(path):
        return None

    try:
        with open(path, 'r') as f:
            return f.read()
    except UnicodeDecodeError:
        return None


def is_remote(path_to_repo: str) -> bool:
    """ Check if the path links to a remote or local repository.

    Parameters
    ----------
    path_to_repo : str
        The path to the repository.

    Return
    ------
    bool
        True if a remote path; False otherwise.

    """
    return path_to_repo.startswith("git@") or path_to_repo.startswith("https://")


class BaseMetricsExtractor:
    """ This is the base class to extract metrics from IaC scripts.
    It is extended by concrete classes to extract metrics for specific languages (e.g., Ansible and Tosca).

    """

    def __init__(self, path_to_repo: str, at: str = 'release'):
        """ The clss constructor.

        Parameters
        ----------
        path_to_repo : str
            The path to the repository.
        at : str
            When to extract metrics: at each release or each commit.

        Attributes
        ----------
        dataset: pandas.DataFrame
            The metrics dataset, populated after ``extract()``.

        Raises
        ------
        ValueError
            If `at` is not one of the following: release, commit.
        NotImplementedError
            The commit option is not implemented yet.

        """

        if at not in ('release', 'commit'):
            raise ValueError(f'{at} is not valid! Try with \'release\' or \'commit\'.')

        if at == 'commit':
            raise NotImplementedError('This functionality is not implemented yet! Please, use at=release')

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

        self.releases = [commit.hash for commit in self.repo_miner.traverse_commits()]
        self.dataset = pd.DataFrame()

    def get_files(self) -> Set[str]:
        """ Return all the files in the repository

        Return
        ------
        Set[str]
            The set of filepath relative to the root of repository

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

    def get_product_metrics(self, script: str) -> Dict[str, Any]:
        """ Extract source code metrics from a script.

        Parameters
        ----------
        script : str
            The content of the script to extract metrics from.

        Returns
        -------
        Dict[str, Any]
            A dictionary of <metric, value>.

        """
        return dict()

    def get_process_metrics(self, from_commit: str, to_commit: str) -> dict:
        """ Extract process metrics for an evolution period.

        Parameters
        ----------
        from_commit : str
            Hash of release start
        to_commit : str
            Hash of release end

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
        """ Extract metrics from labeled files.

        Parameters
        ----------
        labeled_files : List[FailureProneFile]
            The list of FailureProneFile objects that are used to label a script as failure-prone (1) or clean (0).
        product: bool
            Whether to extract product metrics.
        process: bool
            Whether to extract process metrics.
        delta: bool
            Whether to extract delta metrics between two successive releases (or commits).

        """
        git_repo = GitRepository(self.path_to_repo)

        metrics_previous_release = dict()  # Values for iac metrics in the last release

        for commit in RepositoryMining(self.path_to_repo, order='date-order').traverse_commits():

            # To handle renaming in metrics_previous_release
            for modified_file in commit.modifications:

                old_path = modified_file.old_path
                new_path = modified_file.new_path

                if old_path != new_path and old_path in metrics_previous_release:
                    # Rename key old_path wit new_path
                    metrics_previous_release[new_path] = metrics_previous_release.pop(old_path)

            if commit.hash not in self.releases:
                continue

            # Else
            git_repo.checkout(commit.hash)
            process_metrics = {}

            if process:
                # Extract process metrics
                i = self.releases.index(commit.hash)
                from_previous_commit = commit.hash if i == 0 else self.releases[i - 1]
                to_current_commit = commit.hash  # = self.releases[i]
                process_metrics = self.get_process_metrics(from_previous_commit, to_current_commit)

            for filepath in self.get_files():

                file_content = get_content(os.path.join(self.path_to_repo, filepath))

                if not file_content or self.ignore_file(filepath, file_content):
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
                    metrics['code_churn_count'] = process_metrics['dict_code_churn_count'].get(filepath, 0)
                    metrics['code_churn_max'] = process_metrics['dict_code_churn_max'].get(filepath, 0)
                    metrics['code_churn_avg'] = process_metrics['dict_code_churn_avg'].get(filepath, 0)
                    metrics['commits_count'] = process_metrics['dict_commits_count'].get(filepath, 0)
                    metrics['contributors_count'] = process_metrics['dict_contributors_count'].get(filepath, 0)
                    metrics['minor_contributors_count'] = process_metrics['dict_minor_contributors_count'].get(filepath, 0)
                    metrics['highest_contributor_experience'] = process_metrics[
                        'dict_highest_contributor_experience'].get(filepath, 0)
                    metrics['hunks_median'] = process_metrics['dict_hunks_median'].get(filepath, 0)
                    metrics['additions'] = process_metrics['dict_additions'].get(filepath, 0)
                    metrics['additions_max'] = process_metrics['dict_additions_max'].get(filepath, 0)
                    metrics['additions_avg'] = process_metrics['dict_additions_avg'].get(filepath, 0)
                    metrics['deletions'] = process_metrics['dict_deletions'].get(filepath, 0)
                    metrics['deletions_max'] = process_metrics['dict_deletions_max'].get(filepath, 0)
                    metrics['deletions_avg'] = process_metrics['dict_deletions_avg'].get(filepath, 0)

                if product:
                    metrics.update(self.get_product_metrics(file_content))

                if delta:
                    delta_metrics = dict()

                    previous = metrics_previous_release.get(filepath, dict())
                    for metric, value in previous.items():

                        if metric in ('filepath', 'commit', 'committed_at', 'failure_prone'):
                            continue

                        difference = metrics.get(metric, 0) - value
                        delta_metrics[f'delta_{metric}'] = round(difference, 3)

                    metrics_previous_release[filepath] = metrics.copy()
                    metrics.update(delta_metrics)

                self.dataset = self.dataset.append(metrics, ignore_index=True)

            git_repo.reset()

    def ignore_file(self, path_to_file: str, content: str = None):
        return False

    def to_csv(self, filepath):
        """ Save the metrics as csv
        The file is saved asa

        Parameters
        ----------
        filepath : str
            The path to the csv.

        """
        with open(filepath, 'w') as out:
            self.dataset.to_csv(out, mode='w', index=False)
