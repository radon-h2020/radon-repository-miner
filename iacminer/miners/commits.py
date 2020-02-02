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

from pydriller.repository_mining import GitRepository, RepositoryMining
from pydriller.domain.commit import ModificationType

from iacminer import filters
from iacminer.entities.commit import BuggyInducingCommit, BuggyInducingCommitEncoder
from iacminer.entities.file import File
from iacminer.mygit import Git


class CommitsMiner():

    def __init__(self, git_repo: GitRepository):
        """
        :git_repo: a GitRepository object
        """
        self.repo = git_repo
        
        owner_repo = str(git_repo.path).split('/')[1:]
        self.repo_name = f'{owner_repo[0]}/{owner_repo[1]}'
        self.repo_path = str(git_repo.path)

        self.__g = Git()
        self.__releases = []
        self.__commits_closing_issues = set() # Set of commits sha closing issues

        self.fixing_commits = set()
        self.buggy_inducing_commits = set()
        #self.__fixing_commits = set()
        #self.__load_fixing_commits()
        
    """
    @property
    def fixing_commits(self):
        return self.__fixing_commits
    
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
    """

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

        for issue in self.__g.get_issues(self.repo_name):
            
            if not issue:
                continue
            
            try:
                issue_events = issue.get_events()
                if issue_events is None or issue_events.totalCount == 0:
                    return None
                
                for e in issue_events: 
                    if e.event.lower() == 'closed' and e.commit_id:
                        self.__commits_closing_issues.add(e.commit_id)

            except ReadTimeout:
                # TODO save issue for later
                print('Read timed out.')                
   
    def __set_buggy_inducing_commits(self):
        """
        Analyze a repository, and return the buggy inducing commits.
        :return: Generator 
        """
        release = {}
        date = {}
        is_first_release_commit = True
        #renamed_files = {}

        for commit in RepositoryMining(self.repo_path, only_in_branch='master').traverse_commits():
            date[commit.hash] = {
                'date': commit.committer_date,
                'timezone': commit.committer_timezone
            }

            # Handle release period information
            if is_first_release_commit:
                is_first_release_commit = False
                from_commit_sha = commit.hash

            release[commit.hash] = {
                'starts_at': from_commit_sha,
                'ends_at': self.__releases[0] if len(self.__releases) else None
            }

            if commit.hash in self.__releases:
                # Count next commit as starting from the new release period
                is_first_release_commit = True
                self.__releases.pop(0)
            
            # Skip if not fix (but after handling renaming)
            is_fix = self.__has_fix_in_message(commit.msg)

            """
            if not is_fix and commit.hash not in self.__commits_closing_issues:
                continue
            """
            for modified_file in commit.modifications:
                
                # Filter out non Ansible files
                if not filters.is_ansible_file(modified_file.new_path) and filters.is_ansible_file(modified_file.old_path):
                    continue
                
                """
                if modified_file.change_type == ModificationType.RENAME:
                    # TODO: handle renamed_files
                    renamed_files.setdefault(commit.hash, {}) \
                                 .setdefault(modified_file.new_path, modified_file.old_path)
                """

                # Keep only files that have been modified
                if modified_file.change_type != ModificationType.MODIFY:
                    continue

                if not is_fix and commit.hash not in self.__commits_closing_issues:
                    continue
                
                self.fixing_commits.add({
                    'repo': self.repo_name,
                    'commit_hash': commit.hash
                })# TODO save somewhere

                # Find buggy inducing commits
                files = {}
                buggy_inducing_commits = self.repo.get_commits_last_modified_lines(commit, modified_file)

                for filepath, commit_hashes in buggy_inducing_commits.items():
                    for hash in commit_hashes:
                        files.setdefault(hash, set()).add(filepath)

                for commit_hash, filenames in files.items():
                    bic = BuggyInducingCommit()
                    bic.hash = commit_hash 

                    if bic not in self.buggy_inducing_commits:
                        bic.filepaths = filenames
                        bic.date = date[commit_hash]['date']
                        bic.timezone = date[commit_hash]['timezone']
                        bic.repo = self.repo_name
                        bic.release = [
                            release.get(commit_hash, {}).get('starts_at', None),
                            release.get(commit_hash, {}).get('ends_at', None)
                        ]

                        self.buggy_inducing_commits.add(bic)
                    else:
                        bic = next(iter(self.buggy_inducing_commits))
                        bic.filepaths = bic.filepaths.union(filenames)

    def mine(self):
        """ 
        Analyze a repository, yielding buggy inducing commits.
        """

        # Get releases for repository        
        for commit in RepositoryMining(self.repo_path, only_releases=True).traverse_commits():
            self.__releases.append(commit.hash)
        
        try:
            self.__set_commits_closing_issues()
            self.__set_buggy_inducing_commits()
            return self.buggy_inducing_commits 

        except github.RateLimitExceededException: # TO TEST
            print('API rate limit exceeded')
            
            # Wait self.__g.rate_limiting_resettime()
            t = (datetime.fromtimestamp(self.__g.rate_limiting_resettime) - datetime.now()).total_seconds() + 10
            print(f'Execution stopped. Quota will be reset in {round(t/60)} minutes')
            time.sleep(t)
            self.__g = Git()
