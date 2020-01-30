"""
A module for mining fixing commits.
"""
import copy
import github
import json
import os
import re
import time

from datetime import datetime
from requests.exceptions import ReadTimeout

from pydriller.repository_mining import RepositoryMining

from iacminer import utils as utils
from iacminer.entities.commit import Commit, CommitEncoder, Filter
from iacminer.entities.file import File
from iacminer.mygit import Git

class CommitsMiner():

    def __init__(self, repo: str):
        """
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        """

        self.__g = Git()
        self.__fixing_commits = set()
        self.__load_fixing_commits()
        self.__releases = []
        self.__commits_closing_issues = set() # Set of commits sha closing issues

        self.repo = repo
        
    """
    @property
    def fixing_commits(self):
        return self.__fixing_commits
    """
    
    def __load_fixing_commits(self):
        filepath = os.path.join('data','fixing_commits.json')
        if os.path.isfile(filepath):
            with open(filepath, 'r') as infile:
                json_array = json.load(infile)

                for json_obj in json_array:
                    files = set()
                    for file in json_obj['files']:
                        files.add(File(file))
                    
                    commit = Commit(json_obj)
                    commit.files = files
                    self.__fixing_commits.add(commit)

    def __save_fixing_commits(self):
        to_save = copy.deepcopy(list(self.__fixing_commits))

        with open(os.path.join('data', 'fixing_commits.json'), 'w') as outfile:
            json.dump(to_save, outfile, cls=CommitEncoder)

    def __get_closing_commit_id(self, issue: github.Issue) -> str:
        """
        Return the commit id closing the issue, None if no commit closes the issue
        :issue: an Issue object

        :return: str commit id. None if not commit closed the issue
        """
        try:
            issue_events = issue.get_events()
            if issue_events is None or issue_events.totalCount == 0:
                return None
            
            for e in issue_events: 
                if e.event.lower() == 'closed' and e.commit_id:
                    return e.commit_id
        except ReadTimeout:
            # TODO save issue for later
            print('Read timed out.')
            pass

        return None

    def __has_fix_in_message(self, message: str):
        """
        Analyze a message and check whether it contains references to some fix for an issue 
        """
        fix = re.match(r'fix(e(d|s))?\s+.*\(?#\d+\)?', message.lower())
        return fix is not None

    def __set_commits_closing_issues(self):
        """ 
        Analyze a repository, and set the commits that fix some issues \
        by looking at the commit that explicitly closes or fixes those issues.
        """

        for issue in self.__g.get_issues(self.repo):
            
            if not issue:
                continue

            sha = self.__get_closing_commit_id(issue)

            if sha:
                self.__commits_closing_issues.add(sha)

    def __get_fixing_commits(self):
        """
        Analyze a repository, and set the commits that fix some issues\
        by looking at the commit message.
        :return: set of fixing commits.
        """

        commits = self.__g.get_commits(self.repo) 

        is_first_release_commit = True

        for commit in commits:                 
            is_fix = self.__has_fix_in_message(commit.commit.message)
     
            if not is_fix and commit.sha not in self.__commits_closing_issues:
                continue
            
            # Otherwise, create a fixing commit
            fixing_commit = Commit(commit, Filter.ANSIBLE)
            fixing_commit.repo = self.repo
            
            if fixing_commit in self.__fixing_commits:
                continue

            if not len(fixing_commit.files):
                continue
            
            if is_first_release_commit:  # To track releases start commit for the specific commit
                is_first_release_commit = False
                from_commit_sha = fixing_commit.sha

            fixing_commit.release_starts_at = from_commit_sha 
            fixing_commit.release_ends_at = self.__releases[0] if len(self.__releases) else None

            if fixing_commit.sha in self.__releases:
                # Count next commit as starting from the new release period
                is_first_release_commit = True
                self.__releases.pop(0)

            self.__fixing_commits.add(fixing_commit)
            self.__save_fixing_commits()
            yield fixing_commit
            
    
    def mine(self):
        """ 
        Analyze a repository, yielding fixing commits.
        """

        # Get releases for repository        
        for commit in RepositoryMining(f'https://github.com/{self.repo}', only_releases=True).traverse_commits():
            self.__releases.append(commit.hash)

        try:
            self.__set_commits_closing_issues()
            for commit in self.__get_fixing_commits():
                yield commit

        except github.RateLimitExceededException: # TO TEST
            print('API rate limit exceeded')
            
            # Wait self.__g.rate_limiting_resettime()
            t = (datetime.fromtimestamp(self.__g.rate_limiting_resettime) - datetime.now()).total_seconds() + 10
            print(f'Execution stopped. Quota will be reset in {round(t/60)} minutes')
            time.sleep(t)
            self.__g = Git()
