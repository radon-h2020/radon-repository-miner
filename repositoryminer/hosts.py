from abc import ABC, abstractmethod
from typing import NewType, List, Set

import github
import gitlab
import re

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

    @abstractmethod
    def get_commit_closing_issue(self, issue) -> str:
        """
        Get the commit that closed the issue

        :param issue: the issue
        :return: the sha of the commit closing the issue
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
        return [issue for issue in self.__repository.get_issues(state='closed', labels=[label], sort='created', direction='desc')]

    def get_commit_closing_issue(self, issue: GithubIssue) -> str:
        for e in issue.get_events():
            is_merged = e.event.lower() == 'merged'
            is_closed = e.event.lower() == 'closed'

            if (is_merged or is_closed) and e.commit_id:
                return e.commit_id


class GitlabHost(SVCHost):

    def __init__(self, access_token: str, namespace: str, project_name: str):
        super().__init__(access_token, namespace, project_name)
        self.__project = gitlab.Gitlab('http://gitlab.com', access_token).projects.get(f'{namespace}/{project_name}')

    def get_labels(self) -> Set[str]:
        return set([label.name for label in self.__project.labels.list()])

    def get_closed_issues(self, label: str) -> List[GithubIssue]:
        label = self.__project.get_label(label)
        return self.__project.issues.list(state='closed', labels=[label], all=True)

    def get_commit_closing_issue(self, issue) -> str:
        closed_via_commit = re.compile('closed via commit ([0-9a-f]{5,40})')
        closed_via_mr = re.compile('closed via merge request !([0-9]+)')

        mr_iid = None
        sha = None

        for note in issue.notes.list(all=True, as_list=False, sort='desc'):
            match = re.search(closed_via_mr, note.body)
            if match:
                mr_iid = match.groups()[0]

            # look also for commit sha
            match = re.search(closed_via_commit, note.body)
            if match:
                sha = match.groups()[0]
                break

        if sha:
            return sha
        elif mr_iid:
            mr = self.__project.mergerequests.get(mr_iid)
            return mr.sha

