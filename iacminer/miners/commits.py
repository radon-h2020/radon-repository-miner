"""
A module for mining fixing commits.
"""
import github
import re

from iacminer import utils as utils
from iacminer.entities.commit import Commit, Filter 
from iacminer.git import Git


class CommitsMiner():

    def __init__(self):
        self.__fixing_commits = set()
        self.__unclassified_commits = set()

    @property
    def fixing_commits(self):
        return self.__fixing_commits
    
    @property
    def unclassified_commits(self):
        return self.__unclassified_commits

    def __get_closing_commit_id(self, issue: github.Issue) -> str:
        """
        Return the commit id closing the issue, None if no commit closes the issue
        :issue: an Issue object

        :return: str commit id. None if not commit closed the issue
        """
        issue_events = issue.get_events()
        if issue_events is None or issue_events.totalCount == 0:
            return None
        
        for e in issue_events: 
            if e.event.lower() == 'closed' and e.commit_id:
                return e.commit_id
        
        return None

    def __has_fix_in_message(self, message: str):
        """
        Analyze a message and check whether it contains references to some fix for an issue 
        """
        fix = re.match(r'fix(e(d|s))?\s+.*\(?#\d+\)?', message.lower())
        return fix is not None

    def __set_fixing_commits_from_issues(self, repo: str):
        """ 
        Analyze a repository, and set the commits that fix some issues \
        by looking at the commit that explicitly closes or fixes those issues.
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        """

        g = Git()

        for issue in g.get_issues(repo):
            sha = self.__get_closing_commit_id(issue)
            if not sha:
                continue 
            
            commit = g.get_commit(repo, sha)
            if not commit:
                continue
            
            commit = Commit(commit, Filter.ANSIBLE)

            if not len(commit.files):
                continue
            
            commit.repo = repo
            self.__fixing_commits.add(commit)

    def __set_commits_from_messages(self, repo: str):
        """ 
        Analyze a repository, and set the commits that fix some issues\
        by looking at the commit message.
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')

        :return: set of fixing commits.
        """

        g = Git()
        commits = g.get_commits(repo) 

        for commit in commits:
            commit = Commit(commit, Filter.ANSIBLE)
            commit.repo = repo

            if not len(commit.files):
                continue
            
            is_fix = self.__has_fix_in_message(commit.message)

            if is_fix:
                self.__fixing_commits.add(commit)
            else:
                self.__unclassified_commits.add(commit)

    def mine_commits(self, repo: str):
        """ 
        Analyze a repository, and extract fixing and unclassified commits.
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')

        :return: two set of fixing and unclassified commits, respectively.
        """
        self.__set_fixing_commits_from_issues(repo)
        self.__set_commits_from_messages(repo)

        return self.__fixing_commits, self.__unclassified_commits
