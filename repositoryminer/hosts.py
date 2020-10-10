from abc import ABC, abstractmethod
from typing import NewType, List, Set

import github

GithubIssue = NewType('Issue', github.Issue)


class SVCHost(ABC):

    def __init__(self, access_token: str, namespace: str, project_name: str):
        pass

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

    def __init__(self, access_token: str, namespace: str, project_name: str):
        super().__init__(access_token, namespace, project_name)

        self.__repository = github.Github(access_token).get_repo(f'{namespace}/{project_name}')

    def get_labels(self) -> Set[str]:

        labels = set()
        for label in self.__repository.get_labels():
            if type(label) == github.Label.Label:
                labels.add(label.name)

        return labels

    def get_closed_issues(self, label: str) -> List[GithubIssue]:
        label = self.__repository.get_label(label)
        issues = list()
        for issue in self.__repository.get_issues(state='closed', labels=[label], sort='created', direction='desc'):
            issues.append(issue)

        return issues
