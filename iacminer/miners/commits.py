"""
A module for mining fixing commits.
"""
import github
import json
import os
import re
import time

from datetime import datetime
from requests.exceptions import ReadTimeout

from iacminer import utils as utils
from iacminer.entities.commit import Commit, CommitEncoder, Filter
from iacminer.entities.file import File
from iacminer.mygit import Git



class CommitsMiner():

    def __init__(self):
        self.__g = Git()
        self.__fixing_commits = set()
        self.__load_fixing_commits()
        reset = (datetime.fromtimestamp(self.__g.rate_limiting_resettime) - datetime.now()).total_seconds()/60
        print(f'Reset time in {round(reset)} minutes')

    @property
    def fixing_commits(self):
        return self.__fixing_commits

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

    def __set_fixing_commits_from_issues(self, repo: str):
        """ 
        Analyze a repository, and set the commits that fix some issues \
        by looking at the commit that explicitly closes or fixes those issues.
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        """

        for issue in self.__g.get_issues(repo):
            
            if not issue:
                continue

            sha = self.__get_closing_commit_id(issue)
            if not sha:
                continue 
            
            commit = self.__g.get_commit(repo, sha)
            if not commit:
                continue
            
            commit = Commit(commit, Filter.ANSIBLE)
            commit.repo = repo

            if not len(commit.files):
                continue
            
            self.__fixing_commits.add(commit)

    def __set_commits_from_messages(self, repo: str):
        """ 
        Analyze a repository, and set the commits that fix some issues\
        by looking at the commit message.
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')

        :return: set of fixing commits.
        """

        commits = self.__g.get_commits(repo) 

        for commit in commits:
            commit = Commit(commit, Filter.ANSIBLE)
            commit.repo = repo

            if not len(commit.files):
                continue
            
            is_fix = self.__has_fix_in_message(commit.message)

            if is_fix:
                self.__fixing_commits.add(commit)

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
        with open(os.path.join('data', 'fixing_commits.json'), 'w') as outfile:
            json.dump(list(self.__fixing_commits), outfile, cls=CommitEncoder)

    def mine(self, repo: str):
        """ 
        Analyze a repository, and extract fixing and unclassified commits.
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')

        :return: the set of fixing commits.
        """
        try:
            self.__set_fixing_commits_from_issues(repo)
            self.__set_commits_from_messages(repo)

            if len(self.__fixing_commits):
                self.__save_fixing_commits()

        except github.RateLimitExceededException: # TO TEST
            print('API rate limit exceeded')
            if len(self.__fixing_commits):
                self.__save_fixing_commits()
            # Wait self.__g.rate_limiting_resettime()
            t = (datetime.fromtimestamp(self.__g.rate_limiting_resettime) - datetime.now()).total_seconds() + 10
            print(f'Execution stopped. Quota will be reset in {round(t/60)} minutes')
            time.sleep(t)
            
        return self.__fixing_commits
