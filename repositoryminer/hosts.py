from abc import ABC, abstractmethod
from typing import NewType, List, Set

import github

GithubIssue = NewType('Issue', github.Issue)


class SVCHost(ABC):

    @abstractmethod
    def get_labels(self) -> Set[str]:
        """
        Collect all the repository labels
        :return: a set of labels
        """
        pass

    @abstractmethod
    def get_closed_issues(self, label: str):
        """
        Get all the closed issues with a given label

        :param label: the issue label (e.g., 'bug')
        :return: the set of closed issues with that label
        """
        pass


class GithubHost(SVCHost):

    def __init__(self, access_token: str, owner: str, name: str):
        self.__host = github.Github(access_token)
        self.repo_owner = owner
        self.repo_name = name

    def get_labels(self) -> Set[str]:
        repo = self.__host.get_repo('/'.join([self.repo_owner, self.repo_name]))  # repo_owner/repo_name
        labels = set()
        for label in repo.get_labels():
            if type(label) == github.Label.Label:
                labels.add(label.name)

        return labels

    def get_closed_issues(self, label: str) -> List[GithubIssue]:
        repo = self.__host.get_repo('/'.join([self.repo_owner, self.repo_name]))  # repo_owner/repo_name
        label = repo.get_label(label)
        issues = list()
        for issue in repo.get_issues(state='closed', labels=[label], sort='created', direction='desc'):
            issues.append(issue)

        return issues
