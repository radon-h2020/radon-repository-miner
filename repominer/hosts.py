import os

from abc import ABC, abstractmethod
from typing import NewType, List, Set, Union

import github
from gitlab import Gitlab
from gitlab.v4.objects import ProjectIssue

import re


GithubIssue = NewType('GithubIssue', github.Issue.Issue)


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

    @abstractmethod
    def get_commit_closing_issue(self, issue) -> str:
        """
        Get the commit that closed the issue

        :param issue: the issue
        :return: the sha of the commit closing the issue
        """
        pass


class GithubHost(SVCHost):

    def __init__(self, full_name: Union[str, int]):
        self.__repository = github.Github(os.getenv('GITHUB_ACCESS_TOKEN')).get_repo(full_name)

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

    # From https://docs.gitlab.com/ee/administration/issue_closing_pattern.html
    issue_closing_pattern = r'((?:[Cc]los(?:e[sd]?|ing)|\b[Ff]ix(?:e[sd]|ing)?|\b[Rr]esolv(?:e[sd]?|ing)|\b[Ii]mplement(?:s|ed|ing)?)(:?) +(?:(?:issues? +)?#(\d+)))'

    def __init__(self, full_name: Union[str, int]):
        self.__project = Gitlab('http://gitlab.com', os.getenv('GITLAB_ACCESS_TOKEN')).projects.get(full_name)
        self.__commit_closing_issues = dict()

        iid_closing_pattern = re.compile(self.issue_closing_pattern)
        for commit in self.__project.commits.list(all=True, as_list=False):
            match = iid_closing_pattern.match(commit.title)
            if match and match.groups():
                iid = match.groups()[-1]
                self.__commit_closing_issues[int(iid)] = commit.id

    def get_labels(self) -> Set[str]:
        return set([label.name for label in self.__project.labels.list(all=True)])

    def get_closed_issues(self, label: str) -> List[ProjectIssue]:
        return self.__project.issues.list(state='closed', labels=[label], all=True)

    def get_commit_closing_issue(self, issue: ProjectIssue) -> str:

        sha = self.__commit_closing_issues.get(issue.iid)
        if sha:
            return sha

        closed_via_commit = re.compile('closed via commit ([0-9a-f]{5,40})')
        closed_via_mr = re.compile('closed via merge request !([0-9]+)')

        mr_iid = None

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
