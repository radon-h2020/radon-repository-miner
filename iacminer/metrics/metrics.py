# Built-in
from datetime import datetime
from io import StringIO
from typing import Dict, List

# Third-parties
from ansiblemetrics.metrics_extractor import extract_all
from iacminer.metrics.text import TextProcessing
from pydriller.metrics.process.change_set import ChangeSet
from pydriller.metrics.process.code_churn import CodeChurn
from pydriller.metrics.process.commits_count import CommitsCount
from pydriller.metrics.process.contributors_count import ContributorsCount
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from pydriller.metrics.process.hunks_count import HunksCount
from pydriller.metrics.process.lines_count import LinesCount


def process_metrics(path_to_repo: str, since: datetime = None, to: datetime = None, from_commit: str = None, to_commit: str = None) -> List[Dict]:
    """
    Collect process metrics from a repository
    :param path_to_repo: path to the local repository
    :param since: from commit date
    :param to: to commit date
    :param from_commit: from commit sha
    :param to_commit: to commit sha
    :return: list of dictionaries, one per process metric
    """
    change_set = ChangeSet(path_to_repo, since=since, to=to, from_commit=from_commit, to_commit=to_commit)
    code_churn = CodeChurn(path_to_repo, since=since, to=to, from_commit=from_commit, to_commit=to_commit)
    commits_count = CommitsCount(path_to_repo, since=since, to=to, from_commit=from_commit, to_commit=to_commit)
    contributors_count = ContributorsCount(path_to_repo, since=since, to=to, from_commit=from_commit,
                                           to_commit=to_commit)
    highest_contributors_experience = ContributorsExperience(path_to_repo, since=since, to=to,
                                                             from_commit=from_commit, to_commit=to_commit)
    median_hunks_count = HunksCount(path_to_repo, since=since, to=to, from_commit=from_commit, to_commit=to_commit)
    lines_count = LinesCount(path_to_repo, since=since, to=to, from_commit=from_commit, to_commit=to_commit)

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


def product_metrics(content: str) -> dict:
    """
    Collect product metrics for Ansible
    :param content: the content of the yaml-based Ansible file
    :return: a dictionary of product metrics
    """
    return extract_all(StringIO(content))


def text_metrics(content: str) -> list:
    """
    Collect textual metrics from a text.
    :param content: a text
    :return: a list of stemmed tokens from the text
    """
    return TextProcessing(content).process()
